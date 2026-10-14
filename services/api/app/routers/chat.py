import datetime
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..deps import get_current_user
from ..models import Message, Session, User

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(body: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session_id = body.get("session_id")
    text = (body.get("message") or "").strip()
    if not session_id or not text:
        raise HTTPException(400, detail="缺少 session_id 或 message")

    s = await db.get(Session, session_id)
    if s is None or s.user_id != user.id:
        raise HTTPException(404, detail="会话不存在")

    db.add(Message(session_id=session_id, role="user", content=text))
    # 占位回复：真实大模型由上层接入（本 Issue 只负责存储与接口）
    reply = "（后端已收到：%s）这是存储接口的占位回复，接入大模型后替换为真实生成内容。" % text[:60]
    db.add(Message(session_id=session_id, role="assistant", content=reply))
    s.updated_at = datetime.datetime.now(datetime.timezone.utc)
    await db.commit()

    async def gen():
        yield "data: " + json.dumps({"token": reply}, ensure_ascii=False) + "\n\n"
        yield "data: " + json.dumps({"done": True}) + "\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")