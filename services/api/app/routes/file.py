"""文件路由：上传、列表、预览、下载、删除（按用户隔离）。"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_owned
from app.models.file import File
from app.services.file_preview import classify, convert_to_pdf, preview_text

router = APIRouter(prefix="/api/files", tags=["files"])


def _out(f: File) -> dict:
    return {
        "id": f.id,
        "filename": f.filename,
        "size": f.size,
        "content_type": f.content_type,
        "created_at": f.created_at.isoformat(),
    }


@router.post("/upload", status_code=201)
async def upload_file(request: Request, file: UploadFile, db: AsyncSession = Depends(get_db)):
    upload_dir = Path(settings.upload_dir) / request.state.user_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid.uuid4())
    safe_name = f"{file_id}_{file.filename or 'unnamed'}"
    path = upload_dir / safe_name
    total = 0
    limit = settings.max_upload_size_mb * 1024 * 1024
    try:
        with path.open("wb") as output:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise HTTPException(status_code=413, detail=f"文件不能超过 {settings.max_upload_size_mb} MB")
                output.write(chunk)
    except Exception:
        path.unlink(missing_ok=True)
        raise

    rec = File(
        user_id=request.state.user_id,
        filename=file.filename or "unnamed",
        size=total,
        content_type=file.content_type,
        storage_path=str(path),
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return _out(rec)


@router.get("/")
async def list_files(request: Request, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(File).where(File.user_id == request.state.user_id).order_by(File.created_at.desc())
        )
    ).scalars().all()
    return [_out(f) for f in rows]


@router.get("/{file_id}/download")
async def download_file(file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    f = await get_owned(db, File, file_id, request.state.user_id, "文件不存在")
    if not os.path.exists(f.storage_path):
        raise HTTPException(status_code=404, detail="文件已丢失")
    return FileResponse(f.storage_path, filename=f.filename)


@router.get("/{file_id}/content")
async def file_content(file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    f = await get_owned(db, File, file_id, request.state.user_id, "文件不存在")
    if not os.path.exists(f.storage_path):
        raise HTTPException(status_code=404, detail="文件已丢失")

    kind = classify(f.filename, f.content_type)
    if kind == "image":
        return FileResponse(f.storage_path, media_type=f.content_type or "application/octet-stream")
    if kind == "pdf":
        return FileResponse(f.storage_path, media_type="application/pdf")
    if kind in ("audio", "video"):
        return FileResponse(f.storage_path, media_type=f.content_type or "application/octet-stream")
    if kind == "text":
        return Response(preview_text(f.storage_path), media_type="text/plain; charset=utf-8")
    if kind == "office":
        pdf = convert_to_pdf(f.storage_path)
        if pdf:
            return Response(pdf, media_type="application/pdf")
        return FileResponse(f.storage_path, filename=f.filename)
    return FileResponse(f.storage_path, filename=f.filename)


@router.delete("/{file_id}")
async def delete_file(file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    f = await get_owned(db, File, file_id, request.state.user_id, "文件不存在")
    try:
        os.remove(f.storage_path)
    except OSError:
        pass
    await db.delete(f)
    await db.commit()
    return {"ok": True}