from fastapi import APIRouter, Depends, File as FileParam, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..deps import get_current_user
from ..models import File, User
from ..schemas import FileOut

router = APIRouter(prefix="/files", tags=["files"])

_TEXT_EXTS = (".txt", ".md", ".csv", ".json", ".xml", ".py", ".js", ".ts", ".html", ".css", ".log", ".yaml", ".yml")
_TEXT_CT = ("text/", "application/json", "application/xml", "application/x-ndjson")


def _decode_text(data: bytes) -> str:
    """尽量按 UTF-8 解码，失败则回退 GB18030（兼容中文 GBK），再回退 big5。"""
    for enc in ("utf-8", "gb18030", "big5"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def _is_text(content_type: str, filename: str) -> bool:
    ct = (content_type or "").lower()
    name = (filename or "").lower()
    return ct.startswith(_TEXT_CT) or name.endswith(_TEXT_EXTS)


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

    ct = (f.content_type or "application/octet-stream").lower()

    # 文本类：解码成 UTF-8 再返回，避免 GBK 等编码乱码
    if _is_text(f.content_type, f.filename):
        return Response(content=_decode_text(f.content), media_type="text/plain; charset=utf-8")

    # 图片 / PDF：按原类型返回，浏览器可直接预览
    if ct.startswith("image/") or ct == "application/pdf":
        return Response(content=f.content, media_type=ct)

    # 其他二进制（docx/xlsx/pptx 等）：原样返回，前端引导下载
    return Response(
        content=f.content,
        media_type=ct,
        headers={"Content-Disposition": f'attachment; filename="{f.filename}"'},
    )