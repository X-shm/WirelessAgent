"""Hybrid retrieval and cloud reranking for the 3GPP protocol collection."""

import re
from functools import partial

import httpx
from anyio.to_thread import run_sync

from .protocol_index import MODEL, dense_protocol_search, embed_protocol_query


DENSE_TOP_K = 50
BM25_TOP_K = 50
RRF_K = 60
RRF_TOP_K = 25
RRF_WEIGHTS = {"dense": 1.0, "bm25": 1.0}
CONTEXT_TOP_K = 5
BM25_PARAMETERS = {"k1": 1.5, "b": 0.75, "epsilon": 0.25}
RERANK_MODEL = "qwen3.7-text-rerank"
RERANK_URL = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
TOKEN = re.compile(r"[^\W_]+(?:[./_-][^\W_]+)*")


def retrieval_parameters(document_id=None):
    return {
        "embedding_model": MODEL, "rerank_model": RERANK_MODEL,
        "dense_top_k": DENSE_TOP_K, "bm25_top_k": BM25_TOP_K, "bm25": dict(BM25_PARAMETERS),
        "rrf_k": RRF_K, "rrf_top_k": RRF_TOP_K, "rrf_weights": dict(RRF_WEIGHTS), "context_top_k": CONTEXT_TOP_K,
        "document_id": document_id,
    }


def _rank(scored_chunks, limit=None):
    return sorted(scored_chunks, key=lambda item: (-item[1], item[0]))[:limit]


def _trace(ranking):
    return [
        {"chunk_id": chunk_id, "rank": rank, "score": score}
        for rank, (chunk_id, score) in enumerate(ranking, 1)
    ]


def _search_text(text, metadata):
    section_path = metadata.get("section_path")
    return f"{section_path}\n{text}" if section_path else text


class ProtocolRerankError(ValueError):
    def __init__(self, result: dict):
        super().__init__("Protocol candidate reranking failed")
        self.result = result


async def _run_once(_name, operation, *, remote=False):
    return await operation()


class ProtocolRetriever:
    """Build BM25 once from the same published Chroma collection used for dense search."""

    def __init__(self, collection):
        from rank_bm25 import BM25Okapi

        count = collection.count()
        if not count:
            raise ValueError("The protocol collection is empty")
        self.collection = collection
        self.chunk_ids = []
        self.document_ids = []

        def corpus_tokens():
            for offset in range(0, count, 512):
                batch = collection.get(limit=512, offset=offset, include=["documents", "metadatas"])
                for chunk_id, text, metadata in zip(batch["ids"], batch["documents"], batch["metadatas"], strict=True):
                    self.chunk_ids.append(chunk_id)
                    self.document_ids.append(metadata["document_id"])
                    yield TOKEN.findall(_search_text(text, metadata).lower())

        self.bm25 = BM25Okapi(corpus_tokens(), **BM25_PARAMETERS)
        if len(self.chunk_ids) != count or len(set(self.chunk_ids)) != count:
            raise ValueError("Protocol collection changed while loading BM25")

    def _dense(self, vector, document_id):
        hits = dense_protocol_search(self.collection, vector, top_k=DENSE_TOP_K, document_id=document_id, include_content=False)
        return _rank((hit["chunk_id"], 1.0 - hit["distance"]) for hit in hits)

    def _lexical(self, query, document_id):
        scores = self.bm25.get_scores(TOKEN.findall(query.lower()))
        return _rank(
            (
                (chunk_id, float(score))
                for chunk_id, doc_id, score in zip(self.chunk_ids, self.document_ids, scores, strict=True)
                if not document_id or doc_id == document_id
            ),
            BM25_TOP_K,
        )

    async def _fuse(self, dense, bm25):
        fused_scores = {}
        for name, ranking in (("dense", dense), ("bm25", bm25)):
            for rank, (chunk_id, _) in enumerate(ranking, 1):
                fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + RRF_WEIGHTS[name] / (RRF_K + rank)
        return _rank(fused_scores.items(), RRF_TOP_K)

    def _passages(self, ids):
        if not ids:
            return {}
        rows = self.collection.get(ids=ids, include=["documents", "metadatas"])
        passages = {
            chunk_id: {"chunk_id": chunk_id, "text": text, "metadata": metadata}
            for chunk_id, text, metadata in zip(rows["ids"], rows["documents"], rows["metadatas"], strict=True)
        }
        if set(passages) != set(ids) or len(rows["ids"]) != len(ids):
            raise ValueError("Ranked protocol passages are missing or duplicated")
        return passages

    async def search(self, query: str, http: httpx.AsyncClient, api_key: str, *, document_id: str | None = None,
                     step=_run_once) -> dict:
        vector = await step("embedding", partial(embed_protocol_query, query, http, api_key), remote=True)
        dense = await step("dense", partial(run_sync, self._dense, vector, document_id))
        bm25 = await step("bm25", partial(run_sync, self._lexical, query, document_id))
        fused = await step("rrf", partial(self._fuse, dense, bm25))
        result = {
            "query": query,
            "index_metadata": dict(self.collection.metadata or {}),
            "parameters": retrieval_parameters(document_id or None),
            "trace": {
                "dense": _trace(dense), "bm25": _trace(bm25), "rrf": _trace(fused), "rerank": [],
            },
            "evidence": [],
        }
        if not fused:
            return result

        async def rerank():
            ids = [chunk_id for chunk_id, _ in fused]
            passages = await run_sync(self._passages, ids)
            documents = [_search_text(passages[chunk_id]["text"], passages[chunk_id]["metadata"]) for chunk_id in ids]
            try:
                return await self._rerank(query, ids, documents, http, api_key)
            except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
                raise ProtocolRerankError(result) from exc

        reranked = await step("rerank", rerank, remote=True)
        result["trace"]["rerank"] = _trace(reranked)
        ids = [chunk_id for chunk_id, _ in reranked[:CONTEXT_TOP_K]]
        passages = await step("evidence", partial(run_sync, self._passages, ids))
        result["evidence"] = [passages[chunk_id] for chunk_id in ids]
        return result

    async def _rerank(self, query, ids, documents, http: httpx.AsyncClient, api_key):
        response = await http.post(
            RERANK_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": RERANK_MODEL,
                "input": {"query": query, "documents": documents},
                "parameters": {"top_n": len(ids), "return_documents": False},
            },
            timeout=30,
        )
        response.raise_for_status()
        scores = {}
        for row in response.json()["output"]["results"]:
            position, score = row["index"], row["relevance_score"]
            if type(position) is not int or not 0 <= position < len(ids) or position in scores:
                raise ValueError("Qwen rerank returned an invalid or duplicate candidate index")
            if type(score) not in (int, float) or not 0 <= score <= 1:
                raise ValueError("Qwen rerank returned an invalid relevance score")
            scores[position] = score
        if len(scores) != len(ids):
            raise ValueError("Qwen rerank returned incomplete candidate scores")
        return _rank((ids[position], score) for position, score in scores.items())
