"""Task routes - submit, query, cancel background tasks."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from wag.database import get_db
from wag.deps import get_owned
from wag.models.project import Project
from wag.models.task import Task
from wag.task_status import TERMINAL, TaskStatus, ensure_transition

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _now():
    return datetime.now(timezone.utc)


class TaskCreate(BaseModel):
    type: str
    parameters: dict | None = None
    project_id: str | None = None


class TaskOut(BaseModel):
    id: str
    project_id: str | None = None
    type: str
    parameters: dict | None = None
    status: str
    progress: int
    stage: str | None = None
    result: dict | None = None
    error: str | None = None
    created_at: str
    updated_at: str
    queued_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None


def _out(t: Task) -> TaskOut:
    return TaskOut(
        id=t.id,
        project_id=t.project_id,
        type=t.type,
        parameters=t.parameters,
        status=t.status,
        progress=t.progress,
        stage=t.stage,
        result=t.result,
        error=t.error,
        created_at=t.created_at.isoformat(),
        updated_at=t.updated_at.isoformat(),
        queued_at=t.queued_at.isoformat() if t.queued_at else None,
        started_at=t.started_at.isoformat() if t.started_at else None,
        finished_at=t.finished_at.isoformat() if t.finished_at else None,
    )


@router.post("/", status_code=201, response_model=TaskOut)
async def create_task(req: TaskCreate, request: Request, db: AsyncSession = Depends(get_db)):
    task_type = req.type.strip()
    if not task_type:
        raise HTTPException(status_code=422, detail="任务类型不能为空")

    project_id = req.project_id
    if project_id:
        await get_owned(db, Project, project_id, request.state.user_id, "项目不存在")

    task = Task(user_id=request.state.user_id, project_id=project_id, type=task_type, parameters=req.parameters or {})
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # enqueue (pending -> queued)
    task.status = ensure_transition(task.status, TaskStatus.queued.value).value
    task.queued_at = _now()
    await db.commit()
    await db.refresh(task)
    return _out(task)


@router.get("/", response_model=list[TaskOut])
async def list_tasks(request: Request, project_id: str | None = Query(None), db: AsyncSession = Depends(get_db)):
    stmt = select(Task).where(Task.user_id == request.state.user_id)
    if project_id:
        stmt = stmt.where(Task.project_id == project_id)
    stmt = stmt.order_by(Task.created_at.desc())
    return [_out(t) for t in (await db.execute(stmt)).scalars().all()]


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    return _out(await get_owned(db, Task, task_id, request.state.user_id, "任务不存在"))


@router.post("/{task_id}/cancel", response_model=TaskOut)
async def cancel_task(task_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    task = await get_owned(db, Task, task_id, request.state.user_id, "任务不存在")
    if task.status in {s.value for s in TERMINAL}:
        raise HTTPException(status_code=409, detail=f"任务已结束（{task.status}），无法取消")
    task.status = ensure_transition(task.status, TaskStatus.cancelled.value).value
    task.finished_at = _now()
    await db.commit()
    await db.refresh(task)
    return _out(task)