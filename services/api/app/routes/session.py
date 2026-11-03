"""Session routes 闁?list, create, delete conversation sessions."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.session import Session
from app.models.message import Message, MessageRole
from app.models.project import Project
from app.deps import get_owned
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionUpdate(BaseModel):
    title: str | None = None
    project_id: str | None = None


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0
    project_id: str | None = None


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
            project_id=s.project_id,
        ))
    return out


@router.post("/", status_code=201, response_model=SessionOut)
async def create_session(request: Request, project_id: str | None = None, db: AsyncSession = Depends(get_db)):
    if project_id:
        await get_owned(db, Project, project_id, request.state.user_id, "项目不存在")
    session = Session(user_id=request.state.user_id, project_id=project_id, title="New Chat")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionOut(
        id=session.id, title=session.title,
        created_at=session.created_at.isoformat(), updated_at=session.updated_at.isoformat(),
        message_count=0,
        project_id=session.project_id,
    )



@router.patch("/{session_id}", response_model=SessionOut)
async def update_session(session_id: str, req: SessionUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.user_id == request.state.user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if req.project_id:
        await get_owned(db, Project, req.project_id, request.state.user_id, "项目不存在")
        session.project_id = req.project_id
    elif req.project_id is not None:
        session.project_id = None
    if req.title is not None and req.title.strip():
        session.title = req.title.strip()
    await db.commit()
    await db.refresh(session)
    count_result = await db.execute(select(Message).where(Message.session_id == session.id))
    return SessionOut(
        id=session.id, title=session.title,
        created_at=session.created_at.isoformat(), updated_at=session.updated_at.isoformat(),
        message_count=len(count_result.scalars().all()), project_id=session.project_id,
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

