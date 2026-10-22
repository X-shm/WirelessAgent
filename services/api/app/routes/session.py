"""Session routes 闁?list, create, delete conversation sessions."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.session import Session
from app.models.message import Message, MessageRole
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0


@router.get("/", response_model=list[SessionOut])
async def list_sessions(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Session).where(Session.user_id == request.state.user_id).order_by(Session.updated_at.desc())
    )
    sessions = result.scalars().all()
    out = []
    for s in sessions:
        count_result = await db.execute(select(Message).where(Message.session_id == s.id))
        out.append(SessionOut(
            id=s.id, title=s.title,
            created_at=s.created_at.isoformat(), updated_at=s.updated_at.isoformat(),
            message_count=len(count_result.scalars().all()),
        ))
    return out


@router.post("/", status_code=201, response_model=SessionOut)
async def create_session(request: Request, db: AsyncSession = Depends(get_db)):
    session = Session(user_id=request.state.user_id, title="New Chat")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionOut(
        id=session.id, title=session.title,
        created_at=session.created_at.isoformat(), updated_at=session.updated_at.isoformat(),
        message_count=0,
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.user_id == request.state.user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
    return {"ok": True}



class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


@router.get("/{session_id}/messages", response_model=list[MessageOut])
async def get_session_messages(session_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.user_id == request.state.user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    msg_result = await db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    )
    messages = msg_result.scalars().all()
    return [
        MessageOut(id=m.id, role=m.role.value, content=m.content, created_at=m.created_at.isoformat())
        for m in messages
    ]

