import json
import unittest
from unittest.mock import Mock

import httpx

from services.api.app.services import protocol_index, protocol_retrieval as retrieval


class ProtocolRetrievalTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ids = [f"chunk-{number:02}" for number in range(60)]
        self.documents = [f"Passage {number}" for number in range(60)]
        self.documents[49] = "The scope of the procedure"
        self.metadata = {"document_id": "TS29512-V19.7.0", "clause": "1"}
        self.metadatas = [self.metadata] * len(self.ids)
        self.collection = Mock(metadata={"vector_manifest_sha256": "fixture-digest"})
        self.collection.count.return_value = len(self.ids)

        def get(*, ids=None, limit=None, offset=0, include):
            del include
            ids = ids if ids is not None else self.ids[offset:offset + limit]
            return {"ids": ids, "documents": [self.documents[self.ids.index(row)] for row in ids],
                    "metadatas": [self.metadatas[self.ids.index(row)] for row in ids]}

        self.collection.get.side_effect = get
        dense_positions = [49, *range(49)]
        self.collection.query.return_value = {
            "ids": [[self.ids[position] for position in dense_positions]],
            "documents": [[self.documents[position] for position in dense_positions]],
            "metadatas": [[self.metadata] * len(dense_positions)],
            "distances": [[rank / 100 for rank in range(len(dense_positions))]],
        }
        self.retriever = retrieval.ProtocolRetriever(self.collection)
        self.rerank_request = None

    def respond(self, request, *, duplicate=False):
        body = json.loads(request.content)
        if str(request.url) == protocol_index.EMBEDDINGS_URL:
            self.assertEqual(body["input"], ["scope"])
            return httpx.Response(200, json={"model": protocol_index.MODEL, "data": [
                {"index": 0, "embedding": [1.0] + [0.0] * (protocol_index.DIMENSION - 1)},
            ]})
        self.assertEqual(str(request.url), retrieval.RERANK_URL)
        self.rerank_request = body
        results = [{"index": rank, "relevance_score": rank / 100} for rank in range(len(body["input"]["documents"]))]
        if duplicate:
            results[-1]["index"] = results[0]["index"]
        return httpx.Response(200, json={"output": {"results": results}})

    async def test_pipeline_limits_fusion_and_evidence_identity(self):
        document_id = self.metadata["document_id"]
        async with httpx.AsyncClient(transport=httpx.MockTransport(self.respond)) as http:
            result = await self.retriever.search("scope", http, "test-key", document_id=document_id)

        self.assertEqual(self.collection.get.call_args_list[0].kwargs,
                         {"limit": 512, "offset": 0, "include": ["documents", "metadatas"]})
        self.assertEqual([len(call.kwargs["ids"]) for call in self.collection.get.call_args_list[1:]], [25, 5])
        self.assertEqual(self.collection.query.call_args.kwargs["n_results"], 50)
        self.assertEqual(self.collection.query.call_args.kwargs["where"], {"document_id": document_id})
        self.assertEqual({stage: len(rows) for stage, rows in result["trace"].items()}, {
            "dense": 50, "bm25": 50, "rrf": 25, "rerank": 25,
        })
        trace = result["trace"]
        self.assertEqual(trace["bm25"][0]["chunk_id"], "chunk-49")
        self.assertEqual(trace["rrf"][0], {"chunk_id": "chunk-49", "rank": 1, "score": 2 / 61})
        self.assertEqual(self.rerank_request, {
            "model": retrieval.RERANK_MODEL,
            "input": {"query": "scope", "documents": [self.documents[self.ids.index(row["chunk_id"])] for row in trace["rrf"]]},
            "parameters": {"top_n": 25, "return_documents": False},
        })
        fused_ids = [row["chunk_id"] for row in trace["rrf"]]
        self.assertEqual([row["chunk_id"] for row in result["evidence"]], fused_ids[::-1][:5])
        self.assertEqual(result["evidence"][0]["metadata"], self.metadata)

    async def test_duplicate_rerank_indices_fail_instead_of_returning_evidence(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: self.respond(request, duplicate=True))) as http:
            with self.assertRaises(retrieval.ProtocolRerankError) as failure:
                await self.retriever.search("scope", http, "test-key")
        self.assertIn("duplicate candidate index", str(failure.exception.__cause__))
        self.assertEqual(len(failure.exception.result["trace"]["rrf"]), 25)
        self.assertEqual(failure.exception.result["evidence"], [])

    async def test_section_path_enriches_search_but_preserves_original_evidence(self):
        self.documents[49] = "1. POST /sm-policies"
        self.metadatas[49] = {**self.metadata, "section_path": "Scope > Association establishment"}
        retriever = retrieval.ProtocolRetriever(self.collection)

        def rank_first_highest(request):
            response = self.respond(request)
            if str(request.url) != retrieval.RERANK_URL:
                return response
            body = response.json()
            body["output"]["results"][0]["relevance_score"] = 1.0
            return httpx.Response(200, json=body)

        async with httpx.AsyncClient(transport=httpx.MockTransport(rank_first_highest)) as http:
            result = await retriever.search("scope", http, "test-key")

        self.assertEqual(result["trace"]["bm25"][0]["chunk_id"], "chunk-49")
        self.assertEqual(self.rerank_request["input"]["documents"][0],
                         "Scope > Association establishment\n1. POST /sm-policies")
        self.assertEqual(result["evidence"][0]["chunk_id"], "chunk-49")
        self.assertEqual(result["evidence"][0]["text"], "1. POST /sm-policies")
