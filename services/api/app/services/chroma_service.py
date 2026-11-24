"""Lazy access to the persistent Chroma client."""
from pathlib import Path
try:
    from chromadb import PersistentClient
except ImportError:
    PersistentClient = None
from app.config import settings


class ChromaService:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            persist_dir = Path(settings.chroma_persist_dir)
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = PersistentClient(path=str(persist_dir.resolve()))
        return self._client


chroma = ChromaService()
