"""Chat routes — SSE streaming chat via OpenClaw Agent."""
import hashlib
import json
import re
from urllib.parse import quote, urlsplit
from uuid import UUID

from anyio import CancelScope
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, get_db
from app.models.analytics import Analytics
from app.models.session import Session
from app.models.message import Message, MessageRole
from app.models.file import File
from app.models.base import new_uuid
from app.models.protocol_run import ProtocolRun
from app.models.protocol_search_log import ProtocolSearchLog
from app.services.file_preview import extract_text
from app.services.openclaw_client import openclaw
from app.services.protocol_run import stop_protocol_worker, stream_protocol_request
from app.services.protocol_run_store import read_run, request_cancel
from app.config import settings
from app.limiter import limiter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str
    file_ids: list[str] = []
    mode: str = "talk"
    tool: str | None = None
    model: str | None = None
    api_base_url: str | None = None
    api_key: str | None = None
    request_id: UUID | None = None


class ProtocolResume(BaseModel):
    after: int = Field(default=0, ge=0)
    retry: bool = False
    api_key: str | None = None


def _tool_marker(tool: str | None) -> str:
    return f"[[TOOL:{tool}]]\n" if tool in {"search", "homework"} else ""


def _strip_markers(content: str) -> str:
    text = content or ""
    while True:
        updated = re.sub(r"^\[\[(?:FILES:[^\]]+|TOOL:(?:search|homework))\]\]\n?", "", text)
        if updated == text:
            return text
        text = updated


def _file_marker(files: list[File]) -> str:
    if not files:
        return ""
    metadata = [
        {
            "id": file.id,
            "name": file.filename,
            "size": file.size,
            "content_type": file.content_type or "",
        }
        for file in files
    ]
    return f"[[FILES:{quote(json.dumps(metadata, ensure_ascii=False), safe='')}]]\n"


def _strip_file_marker(content: str) -> str:
    match = re.match(r"^\[\[FILES:[^\]]+\]\]\n?", content or "")
    return _strip_markers(content)


def _build_file_context(files: list[File]) -> str:
    if not files:
        return ""
    sections: list[str] = []
    total = 0
    for file in files:
        text = extract_text(file.storage_path, file.filename, file.content_type).strip()
        if text:
            remaining = max(0, 30000 - total)
            if remaining <= 0:
                break
            text = text[:remaining]
            if len(text) > 12000:
                text = text[:12000] + "\n[文件内容过长，已截断]"
            sections.append(f"--- 文件：{file.filename} ---\n{text}")
            total += len(text)
        else:
            sections.append(f"--- 文件：{file.filename} ---\n[未能提取可读文本，请告知用户该文件无法直接读取]")
    if not sections:
        return ""
    return "\n\n用户本轮上传了以下资料，请优先结合资料内容回答：\n" + "\n\n".join(sections)


async def _get_session(session_id: str, user_id: str, db: AsyncSession) -> Session:
    result = await db.execute(select(Session).where(Session.id == session_id, Session.user_id == user_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def _protocol_response(request_id, *, after=0, retry=False, key=None):
    return StreamingResponse(
        stream_protocol_request(request_id, after, retry, key), media_type="text/event-stream",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no", "X-Protocol-Request-Id": request_id},
    )


async def _owned_protocol_run(request_id, user_id, db):
    run = await read_run(str(request_id))
    if run is None or run.user_id != user_id:
        raise HTTPException(status_code=404, detail="Protocol request not found")
    await _get_session(run.session_id, user_id, db)
    return run


async def _start_protocol(req, user_id, files, message_text, user_msg, db):
    if len(req.message) > 16000:
        raise HTTPException(status_code=413, detail="标准检索问题过长")
    if req.api_base_url:
        try:
            base = urlsplit(req.api_base_url)
            if (base.scheme not in {"http", "https"} or not base.hostname
                    or base.username is not None or base.password is not None or base.query or base.fragment):
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=422, detail="自定义生成服务地址需要提供独立的 API Key") from None
    request_id = str(req.request_id) if req.request_id else new_uuid()
    model = req.model or settings.openclaw_model
    signature = hashlib.sha256(json.dumps(
        [req.session_id, req.message, req.file_ids, model, req.api_base_url], ensure_ascii=False,
    ).encode()).hexdigest()

    def existing(run):
        if run.user_id != user_id:
            raise HTTPException(status_code=404, detail="Protocol request not found")
        if run.input_hash != signature:
            raise HTTPException(status_code=409, detail="Protocol request ID is already in use")
        return _protocol_response(request_id, key=req.api_key)

    run = await db.get(ProtocolRun, request_id)
    if run:
        return existing(run)
    if req.api_base_url and not (req.api_key or "").strip():
        raise HTTPException(status_code=422, detail="自定义生成服务需要提供对应的 API Key")

    history = (await db.scalars(select(Message).where(Message.session_id == req.session_id).order_by(
        Message.created_at.desc(), Message.id.desc(),
    ).limit(19))).all()
    messages = []
    budget = 40000
    for message in history:
        if not budget:
            break
        text = _strip_markers(message.content)[:min(budget, 12000)]
        messages.append({"role": message.role.value, "content": text})
        budget -= len(text)
    messages.reverse()
    messages.append({"role": "user", "content": message_text})
    db.add_all([
        user_msg,
        ProtocolSearchLog(request_id=request_id, question=req.message, query=message_text, model=model),
        ProtocolRun(request_id=request_id, user_id=user_id, session_id=req.session_id, input_hash=signature, inputs={
            "query": message_text, "model": model, "base_url": req.api_base_url,
            "messages": messages, "prompt": settings.wireless_prompt,
            "files": [{"name": file.filename, "path": file.storage_path, "type": file.content_type} for file in files],
        }),
    ])
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        run = await db.get(ProtocolRun, request_id)
        if run is None:
            raise
        return existing(run)
    return _protocol_response(request_id, key=req.api_key)


@router.post("/protocol/{request_id}/resume")
async def resume_protocol(request_id: UUID, body: ProtocolResume, request: Request, db: AsyncSession = Depends(get_db)):
    run = await _owned_protocol_run(request_id, request.state.user_id, db)
    if body.after > run.last_seq:
        raise HTTPException(status_code=409, detail="Invalid protocol event cursor")
    return _protocol_response(run.request_id, after=body.after, retry=body.retry, key=(body.api_key or "").strip())


@router.post("/protocol/{request_id}/cancel")
async def cancel_protocol(request_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    run = await _owned_protocol_run(request_id, request.state.user_id, db)
    status = await request_cancel(run)
    if status == "cancel_requested":
        stop_protocol_worker(run.request_id)
    return {"request_id": run.request_id, "status": status}


@router.post("/stream")
@limiter.limit("1/second")
async def chat_stream(req: ChatRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Send a message with optional file attachments and stream the response."""
    user_id = request.state.user_id
    session = await _get_session(req.session_id, user_id, db)

    files: list[File] = []
    requested_ids = list(dict.fromkeys(req.file_ids))[:8]
    if requested_ids:
        result = await db.execute(select(File).where(File.id.in_(requested_ids), File.user_id == user_id))
        by_id = {file.id: file for file in result.scalars().all()}
        files = [by_id[file_id] for file_id in requested_ids if file_id in by_id]

    message_text = req.message.strip() or "请阅读并分析我上传的文件。"
    user_content = _tool_marker(req.tool) + _file_marker(files) + message_text
    user_msg = Message(session_id=session.id, role=MessageRole.user, content=user_content)
    if req.mode == "work" and req.tool == "search":
        return await _start_protocol(req, user_id, files, message_text, user_msg, db)
    db.add(user_msg)
    await db.commit()

    result = await db.execute(
        select(Message).where(Message.session_id == session.id).order_by(Message.created_at)
    )
    history = result.scalars().all()
    recent_rounds = 10
    messages = [
        {"role": message.role.value, "content": _strip_markers(message.content)}
        for message in history[-(recent_rounds * 2):]
    ]

    mode_prompt = (
        "当前处于工作模式。请根据用户的工程任务、上传资料和已有工具能力给出可执行、严谨的结果。"
        if req.mode == "work"
        else "当前处于交谈模式。请用清晰、自然的方式回答、讲解和讨论。"
    )
    tool_prompt = ""
    if req.mode == "work" and req.tool == "homework":
        tool_prompt = "\n\n已启用习题解答。请先识别题目条件，再分步骤推导，最后给出结论并检查结果。"
    system_prompt = settings.wireless_prompt + "\n\n" + mode_prompt + tool_prompt + _build_file_context(files)

    async def generate():
        full_content = ""
        try:
            async for token in openclaw.chat_stream(
                messages, system_prompt=system_prompt, user_id=session.id, model=req.model,
                api_base_url=req.api_base_url, api_key=req.api_key,
            ):
                full_content += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as error:
            message = str(error).lower()
            if "timeout" in message or "timed out" in message:
                error_text = "回复生成超时，请缩短问题或稍后重试"
            elif "connection" in message or "refused" in message:
                error_text = "AI 服务暂时不可用，请稍后重试 📡"
            elif "401" in message or "unauthorized" in message:
                error_text = "AI 服务认证失败，请检查 Gateway 配置"
            else:
                error_text = f"服务异常：{str(error)}"
            yield f"data: {json.dumps({'error': error_text}, ensure_ascii=False)}\n\n"
        finally:
            if full_content:
                with CancelScope(shield=True):
                    async with async_session() as save_session:
                        save_session.add(Message(session_id=session.id, role=MessageRole.assistant, content=full_content))
                        save_session.add(Analytics(
                            session_id=session.id, user_id=user_id, question=message_text, answer=full_content
                        ))
                        await save_session.commit()

        yield f"data: {json.dumps({'done': True, 'message_id': ''})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
