"""Chat routes — SSE streaming chat via OpenClaw Agent."""
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.session import Session
from app.models.message import Message, MessageRole
from app.services.openclaw_client import openclaw
from app.config import settings
from app.limiter import limiter
from pydantic import BaseModel



router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


async def _get_session(session_id: str, user_id: str, db: AsyncSession) -> Session:
    """Retrieve or create a chat session."""
    from sqlalchemy import select
    result = await db.execute(select(Session).where(Session.id == session_id, Session.user_id == user_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/stream")
@limiter.limit("1/second")
async def chat_stream(req: ChatRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Send a message and stream the AI response via SSE."""
    user_id = request.state.user_id
    session = await _get_session(req.session_id, user_id, db)

    # Save user message
    user_msg = Message(session_id=session.id, role=MessageRole.user, content=req.message)
    db.add(user_msg)
    await db.commit()

    # Build history
    from sqlalchemy import select
    result = await db.execute(
        select(Message).where(Message.session_id == session.id).order_by(Message.created_at)
    )
    history = result.scalars().all()
    RECENT_ROUNDS = 10
    messages = [{"role": m.role.value, "content": m.content} for m in history[-(RECENT_ROUNDS * 2):]]

    async def generate():
        full_content = ""
        try:
            async for token in openclaw.chat_stream(messages, system_prompt=settings.wireless_prompt, user_id=session.id):
                full_content += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            msg = str(e).lower()
            if "timeout" in msg or "timed out" in msg:
                user_msg = "回复生成超时，请缩短问题或稍后重试"
            elif "connection" in msg or "refused" in msg:
                user_msg = "AI 服务暂时不可用，请稍后重试 📡"
            elif "401" in msg or "unauthorized" in msg:
                user_msg = "AI 服务认证失败，请检查 Gateway 配置"
            else:
                user_msg = f"服务异常：{str(e)}"
            yield f"data: {json.dumps({'error': user_msg})}\n\n"

        # Save assistant response
        if full_content:
            from app.database import async_session
            async with async_session() as s:
                assistant_msg = Message(session_id=session.id, role=MessageRole.assistant, content=full_content)
                s.add(assistant_msg)
                # Also write to analytics
                from app.models.analytics import Analytics
                s.add(Analytics(session_id=session.id, user_id=user_id, question=req.message, answer=full_content))
                await s.commit()

        yield f"data: {json.dumps({'done': True, 'message_id': ''})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")