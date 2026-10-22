"""文件预览：类型分类、文本编码识别、Office 转 PDF。"""
import subprocess
import tempfile
from pathlib import Path

IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}
PDF = {".pdf"}
AUDIO = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
VIDEO = {".mp4", ".webm", ".mov", ".mkv"}
TEXT = {".txt", ".md", ".csv", ".json", ".xml", ".log", ".py", ".js", ".html", ".css", ".yaml", ".yml", ".ini", ".conf"}
OFFICE = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".rtf", ".odt", ".ods", ".odp"}


def classify(filename: str, content_type: str | None = None) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext in IMAGE:
        return "image"
    if ext in PDF:
        return "pdf"
    if ext in AUDIO:
        return "audio"
    if ext in VIDEO:
        return "video"
    if ext in TEXT:
        return "text"
    if ext in OFFICE:
        return "office"
    return "binary"


def preview_text(path: str) -> str:
    """读取文本并识别编码，返回 UTF-8 字符串（防乱码）。"""
    data = Path(path).read_bytes()
    for enc in ("utf-8", "gbk", "gb18030", "utf-16", "big5", "latin-1"):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def convert_to_pdf(path: str) -> bytes | None:
    """用 LibreOffice 将 Office 文档转为 PDF，返回 PDF 字节。"""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, str(path)],
                check=True, timeout=120,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            out = Path(tmp) / (Path(path).stem + ".pdf")
            if out.exists():
                return out.read_bytes()
    except Exception:
        return None
    return None