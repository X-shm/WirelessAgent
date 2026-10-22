"""RAG service — document parsing, chunking, indexing, and retrieval."""
import os
from pathlib import Path
try:
    from app.services.chroma_service import chroma
except ImportError:
    chroma = None
from app.config import settings


class RAGService:
    """High-level RAG operations: index files, search knowledge base, format citations."""

    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    COLLECTION_NAME = "wireless_knowledge"

    async def index_knowledge_base(self):
        """Scan knowledge-base directories and index all supported files."""
        kb_paths = [
            Path(settings.skills_base_path) / "knowledge-retrieval" / "knowledge-base",
        ]
        for kb_path in kb_paths:
            if not kb_path.exists():
                continue
            for file_path in kb_path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in {".md", ".txt", ".pdf"}:
                    await self._index_file(file_path)

    async def _index_file(self, file_path: Path):
        """Parse and index a single file."""
        try:
            if file_path.suffix.lower() == ".pdf":
                text = await self._read_pdf(file_path)
            else:
                text = file_path.read_text(encoding="utf-8", errors="ignore")

            chunks = self._chunk_text(text)
            ids = [f"{file_path.stem}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": str(file_path), "chunk_index": i} for i in range(len(chunks))]
            chroma.index_documents(self.COLLECTION_NAME, chunks, metadatas, ids)
        except Exception as e:
            print(f"Failed to index {file_path}: {e}")

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.CHUNK_SIZE, len(text))
            chunks.append(text[start:end])
            start += self.CHUNK_SIZE - self.CHUNK_OVERLAP
        return chunks

    async def _read_pdf(self, file_path: Path) -> str:
        """Extract text from a PDF file."""
        # Inline import to avoid hard dependency at module load
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            return f"[PDF 文件需安装 pypdf: {file_path}]"

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search the knowledge base and return formatted results."""
        results = chroma.search(self.COLLECTION_NAME, query, top_k)
        hits = []
        if results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results.get("metadatas", [[{}]])[0][i] if results.get("metadatas") else {}
                hits.append({
                    "content": doc,
                    "source": meta.get("source", "unknown"),
                    "chunk_index": meta.get("chunk_index", 0),
                })
        return hits


# Singleton
rag = RAGService()
