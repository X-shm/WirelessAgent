from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..deps import get_current_user
from ..models import Message, Session, User
from ..schemas import MessageOut, SessionCreate, SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


async def _owned(session_id: str, user: User, db: AsyncSession) -> Session:
    s = await db.get(Session, session_id)
    if s is None or s.user_id != user.id:
        raise HTTPException(404, detail="会话不存在")
    return s


@router.get("/", response_model=list[SessionOut])
async def list_sessions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Session).where(Session.user_id == user.id).order_by(Session.updated_at.desc()))
    return res.scalars().all()


@router.post("/", response_model=SessionOut, status_code=201)
async def create_session(body: SessionCreate | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = Session(user_id=user.id, title=(body.title if body else "新会话"))
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@router.delete("/{session_id}")
async def delete_session(session_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = await _owned(session_id, user, db)
    await db.delete(s)
    await db.commit()
    return {"ok": True}


@router.get("/{session_id}/messages", response_model=list[MessageOut])
async def get_messages(session_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _owned(session_id, user, db)
    res = await db.execute(select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc()))
    return res.scalars().all()