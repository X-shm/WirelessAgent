"""工作空间：文件/项目聚合视图（基础版，暂不含代码执行）。"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.file import File
from app.models.project import Project

router = APIRouter(prefix="/api/workspace", tags=["workspace"])


@router.get("/")
async def workspace_overview(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    files_result = await db.execute(
        select(File).where(File.user_id == user_id).order_by(File.created_at.desc())
    )
    files = files_result.scalars().all()
    projects_result = await db.execute(
        select(Project).where(Project.user_id == user_id).order_by(Project.updated_at.desc())
    )
    projects = projects_result.scalars().all()
    return {
        "files": [
            {
                "id": f.id,
                "filename": f.filename,
                "size": f.size,
                "content_type": f.content_type or "",
                "created_at": f.created_at.isoformat(),
            }
            for f in files
        ],
        "projects": [
            {"id": p.id, "name": p.name, "updated_at": p.updated_at.isoformat()}
            for p in projects
        ],
    }
