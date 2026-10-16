"""Project routes - user-owned container for sessions and tasks."""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from wag.database import get_db
from wag.deps import get_owned
from wag.models.project import Project
from wag.models.session import Session
from wag.models.task import Task

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    created_at: str
    updated_at: str


def _out(p: Project) -> ProjectOut:
    return ProjectOut(
        id=p.id,
        name=p.name,
        description=p.description,
        created_at=p.created_at.isoformat(),
        updated_at=p.updated_at.isoformat(),
    )


@router.post("/", status_code=201, response_model=ProjectOut)
async def create_project(req: ProjectCreate, request: Request, db: AsyncSession = Depends(get_db)):
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="项目名称不能为空")
    project = Project(user_id=request.state.user_id, name=name, description=req.description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return _out(project)


@router.get("/", response_model=list[ProjectOut])
async def list_projects(request: Request, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(Project).where(Project.user_id == request.state.user_id).order_by(Project.updated_at.desc())
        )
    ).scalars().all()
    return [_out(p) for p in rows]


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    return _out(await get_owned(db, Project, project_id, request.state.user_id, "项目不存在"))


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: str, req: ProjectUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    project = await get_owned(db, Project, project_id, request.state.user_id, "项目不存在")
    if req.name is not None:
        name = req.name.strip()
        if not name:
            raise HTTPException(status_code=422, detail="项目名称不能为空")
        project.name = name
    if req.description is not None:
        project.description = req.description
    await db.commit()
    await db.refresh(project)
    return _out(project)


@router.delete("/{project_id}")
async def delete_project(project_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    project = await get_owned(db, Project, project_id, request.state.user_id, "项目不存在")
    await db.execute(update(Session).where(Session.project_id == project_id).values(project_id=None))
    await db.execute(update(Task).where(Task.project_id == project_id).values(project_id=None))
    await db.delete(project)
    await db.commit()
    return {"ok": True}