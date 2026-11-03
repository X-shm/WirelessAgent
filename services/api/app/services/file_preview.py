"""文件预览与文本提取：类型分类、编码识别、Office 转 PDF、PDF 文本读取。"""
import html
import io
import re
import subprocess
import tempfile
import zipfile
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
    """读取文本并识别常见中文编码，避免预览和模型读取时乱码。"""
    data = Path(path).read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk", "utf-16", "big5", "latin-1"):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def _pdf_text(data: bytes) -> str:
    try:
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        text = "\n\n".join(page.get_text("text") for page in doc)
        doc.close()
        if text.strip():
            return text
    except Exception:
        pass
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


def _ocr_text(path: str) -> str:
    try:
        result = subprocess.run(
            ["tesseract", str(path), "stdout", "-l", "chi_sim+eng"],
            capture_output=True, timeout=180,
        )
        if result.returncode == 0:
            return result.stdout.decode("utf-8", errors="replace")
    except Exception:
        pass
    return ""


def _xml_text(data: bytes) -> str:
    try:
        raw = data.decode("utf-8", errors="replace")
    except Exception:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _office_zip_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if ext == ".docx":
                targets = [name for name in names if name == "word/document.xml"]
            elif ext == ".pptx":
                targets = sorted(name for name in names if re.match(r"ppt/slides/slide\d+\.xml$", name))
            elif ext == ".xlsx":
                targets = [name for name in names if name == "xl/sharedStrings.xml"]
            else:
                targets = []
            return "\n\n".join(filter(None, (_xml_text(archive.read(name)) for name in targets)))
    except Exception:
        return ""


def convert_to_pdf(path: str) -> bytes | None:
    """用 LibreOffice 将 Office 文档转为 PDF，返回 PDF 字节。"""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, str(path)],
                check=True,
                timeout=120,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            out = Path(tmp) / (Path(path).stem + ".pdf")
            if out.exists():
                return out.read_bytes()
    except Exception:
        return None
    return None


def extract_text(path: str, filename: str, content_type: str | None = None) -> str:
    """尽力提取可供模型阅读的文本；失败时返回空字符串。"""
    kind = classify(filename, content_type)
    if kind == "text":
        return preview_text(path)
    if kind == "pdf":
        text = _pdf_text(Path(path).read_bytes())
        if text.strip():
            return text
        ocr = _ocr_text(path)
        return ocr if ocr.strip() else "文件为图片型或扫描件，无法提取文本"
    if kind == "office":
        direct = _office_zip_text(path)
        if direct:
            return direct
        pdf_data = convert_to_pdf(path)
        if pdf_data:
            return _pdf_text(pdf_data)
    return ""