from fastapi import APIRouter, Depends, File as FileParam, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..deps import get_current_user
from ..models import File, User
from ..schemas import FileOut

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileOut, status_code=201)
async def upload(file: UploadFile = FileParam(...), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await file.read()
    f = File(user_id=user.id, filename=file.filename or "未命名", size=len(content), content_type=file.content_type, content=content)
    db.add(f)
    await db.commit()
    await db.refresh(f)
    return f


@router.get("/", response_model=list[FileOut])
async def list_files(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(File).where(File.user_id == user.id).order_by(File.created_at.desc()))
    return res.scalars().all()


@router.get("/{file_id}/content")
async def file_content(file_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    f = await db.get(File, file_id)
    if f is None or f.user_id != user.id:
        raise HTTPException(404, detail="文档不存在")
    media = f.content_type or "application/octet-stream"
    if media.startswith("text/") or media in ("application/json", "application/pdf", "application/x-pdf"):
        return Response(content=f.content, media_type="text/plain; charset=utf-8")
    return Response(content=f.content, media_type=media)