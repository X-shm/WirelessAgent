"""RAG routes — search knowledge base, index documents."""
from fastapi import APIRouter, Query
from app.services.rag_service import rag

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.get("/search")
async def search_knowledge(q: str = Query(..., description="Search query"), top_k: int = Query(5, ge=1, le=20)):
    """Search the local knowledge base."""
    hits = await rag.search(q, top_k)
    return {"query": q, "results": hits, "total": len(hits)}


@router.post("/reindex")
async def reindex_knowledge_base():
    """Re-index all files in the knowledge base."""
    await rag.index_knowledge_base()
    return {"status": "reindex_started"}
