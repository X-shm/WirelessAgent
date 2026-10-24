"""资料库路由：主动上传、从聊天附件保存、列表、预览、下载和删除。"""
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
from app.models.library_file import LibraryFile
from app.services.file_preview import classify, convert_to_pdf, preview_text

router = APIRouter(prefix="/api/library", tags=["library"])


def _out(item: LibraryFile) -> dict:
    return {
        "id": item.id,
        "filename": item.filename,
        "size": item.size,
        "content_type": item.content_type,
        "created_at": item.created_at.isoformat(),
    }


async def _save_stream(file: UploadFile, directory: Path) -> tuple[Path, int]:
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "unnamed").name
    path = directory / f"{uuid.uuid4()}_{safe_name}"
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
    return path, total


@router.post("/upload", status_code=201)
async def upload_library_file(request: Request, file: UploadFile, db: AsyncSession = Depends(get_db)):
    directory = Path(settings.upload_dir) / request.state.user_id / "library"
    path, size = await _save_stream(file, directory)
    item = LibraryFile(
        user_id=request.state.user_id,
        filename=Path(file.filename or "unnamed").name,
        size=size,
        content_type=file.content_type,
        storage_path=str(path),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _out(item)


@router.post("/from-chat/{file_id}", status_code=201)
async def save_chat_file(file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    source = await get_owned(db, File, file_id, request.state.user_id, "文件不存在")
    existing = (
        await db.execute(
            select(LibraryFile).where(
                LibraryFile.user_id == request.state.user_id,
                LibraryFile.storage_path == source.storage_path,
            )
        )
    ).scalar_one_or_none()
    if existing:
        return _out(existing)
    item = LibraryFile(
        user_id=request.state.user_id,
        filename=source.filename,
        size=source.size,
        content_type=source.content_type,
        storage_path=source.storage_path,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _out(item)


@router.get("/files")
async def list_library_files(request: Request, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(LibraryFile)
            .where(LibraryFile.user_id == request.state.user_id)
            .order_by(LibraryFile.created_at.desc())
        )
    ).scalars().all()
    return [_out(item) for item in rows]


@router.get("/files/{file_id}/download")
async def download_library_file(file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, LibraryFile, file_id, request.state.user_id, "文件不存在")
    if not os.path.exists(item.storage_path):
        raise HTTPException(status_code=404, detail="文件已丢失")
    return FileResponse(item.storage_path, filename=item.filename)


@router.get("/files/{file_id}/content")
async def library_file_content(file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, LibraryFile, file_id, request.state.user_id, "文件不存在")
    if not os.path.exists(item.storage_path):
        raise HTTPException(status_code=404, detail="文件已丢失")
    kind = classify(item.filename, item.content_type)
    if kind in {"image", "pdf", "audio", "video"}:
        return FileResponse(item.storage_path, media_type=item.content_type or "application/octet-stream")
    if kind == "text":
        return Response(preview_text(item.storage_path), media_type="text/plain; charset=utf-8")
    if kind == "office":
        pdf = convert_to_pdf(item.storage_path)
        if pdf:
            return Response(pdf, media_type="application/pdf")
        return FileResponse(item.storage_path, filename=item.filename)
    return FileResponse(item.storage_path, filename=item.filename)


@router.delete("/files/{file_id}")
async def delete_library_file(file_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    item = await get_owned(db, LibraryFile, file_id, request.state.user_id, "文件不存在")
    await db.delete(item)
    await db.commit()
    return {"ok": True}