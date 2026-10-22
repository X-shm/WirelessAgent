"""ChromaDB service — vector storage and retrieval for RAG."""
from pathlib import Path
try:
    from chromadb import PersistentClient
except ImportError:
    PersistentClient = None
from app.config import settings


class ChromaService:
    """Manages the ChromaDB vector store. Embedding function loads lazily on first use."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._ef = None
            cls._instance._client = None
            cls._instance._collections = {}
        return cls._instance

    def _ensure_client(self):
        if self._client is None:
            persist_dir = Path(settings.chroma_persist_dir)
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = PersistentClient(path=str(persist_dir.resolve()))

    def _ensure_ef(self):
        if self._ef is None:
            from chromadb.utils import embedding_functions
            self._ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.embedding_model
            )

    def get_or_create_collection(self, name: str):
        self._ensure_client()
        self._ensure_ef()
        if name not in self._collections:
            self._collections[name] = self._client.get_or_create_collection(
                name=name,
                embedding_function=self._ef,
            )
        return self._collections[name]

    def index_documents(self, collection_name: str, documents: list[str], metadatas: list[dict] | None = None, ids: list[str] | None = None):
        col = self.get_or_create_collection(collection_name)
        col.add(documents=documents, metadatas=metadatas, ids=ids)

    def search(self, collection_name: str, query: str, top_k: int = 5) -> dict:
        col = self.get_or_create_collection(collection_name)
        return col.query(query_texts=[query], n_results=top_k)

    def list_collections(self) -> list[str]:
        self._ensure_client()
        return self._client.list_collections()


# Singleton — no eager init, safe to import
chroma = ChromaService()
