"""Session routes - list, create, delete conversations."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from wag.database import get_db
from wag.deps import get_owned
from wag.models.message import Message
from wag.models.project import Project
from wag.models.session import Session

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionOut(BaseModel):
    id: str
    project_id: str | None = None
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0


class SessionCreate(BaseModel):
    title: str = "New Chat"
    project_id: str | None = None


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


@router.get("/", response_model=list[SessionOut])
async def list_sessions(
    request: Request,
    project_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Session).where(Session.user_id == request.state.user_id)
    if project_id:
        stmt = stmt.where(Session.project_id == project_id)
    stmt = stmt.order_by(Session.updated_at.desc())
    sessions = (await db.execute(stmt)).scalars().all()

    out = []
    for s in sessions:
        count = (
            await db.execute(select(func.count()).select_from(Message).where(Message.session_id == s.id))
        ).scalar_one()
        out.append(
            SessionOut(
                id=s.id,
                project_id=s.project_id,
                title=s.title,
                created_at=s.created_at.isoformat(),
                updated_at=s.updated_at.isoformat(),
                message_count=count,
            )
        )
    return out


@router.post("/", status_code=201, response_model=SessionOut)
async def create_session(request: Request, body: SessionCreate | None = None, db: AsyncSession = Depends(get_db)):
    title = (body.title.strip() if body and body.title else "New Chat") or "New Chat"
    project_id = body.project_id if body else None
    if project_id:
        await get_owned(db, Project, project_id, request.state.user_id, "项目不存在")

    session = Session(user_id=request.state.user_id, project_id=project_id, title=title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionOut(
        id=session.id,
        project_id=session.project_id,
        title=session.title,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        message_count=0,
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    session = await get_owned(db, Session, session_id, request.state.user_id, "Session not found")
    await db.delete(session)
    await db.commit()
    return {"ok": True}


@router.get("/{session_id}/messages", response_model=list[MessageOut])
async def get_session_messages(session_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    session = await get_owned(db, Session, session_id, request.state.user_id, "Session not found")
    msgs = (
        await db.execute(select(Message).where(Message.session_id == session.id).order_by(Message.created_at))
    ).scalars().all()
    return [
        MessageOut(id=m.id, role=m.role.value, content=m.content, created_at=m.created_at.isoformat())
        for m in msgs
    ]