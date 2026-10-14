from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..deps import get_current_user
from ..models import Task, User
from ..schemas import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def _owned(task_id: str, user: User, db: AsyncSession) -> Task:
    t = await db.get(Task, task_id)
    if t is None or t.user_id != user.id:
        raise HTTPException(404, detail="任务不存在")
    return t


@router.get("/", response_model=list[TaskOut])
async def list_tasks(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc()))
    return res.scalars().all()


@router.post("/", response_model=TaskOut, status_code=201)
async def create_task(body: TaskCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    t = Task(user_id=user.id, type=body.type, params=body.params or {}, status=body.status or "pending")
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _owned(task_id, user, db)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: str, body: TaskUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    t = await _owned(task_id, user, db)
    if body.status is not None:
        t.status = body.status
    if body.result is not None:
        t.result = body.result
    if body.params is not None:
        t.params = body.params
    await db.commit()
    await db.refresh(t)
    return t


@router.delete("/{task_id}")
async def delete_task(task_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    t = await _owned(task_id, user, db)
    await db.delete(t)
    await db.commit()
    return {"ok": True}