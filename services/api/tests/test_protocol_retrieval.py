import json
import unittest
from unittest.mock import Mock

import httpx

from services.api.app.services import protocol_index, protocol_retrieval as retrieval
from services.api.app.services.protocol_scope import ProtocolScopeUnavailable, requested_protocol_scope


class ProtocolScopeTests(unittest.TestCase):
    def test_explicit_and_incidental_mentions(self):
        cases = [
            ("Explain network slicing in TS 23.501.", []),
            ("Does TS 23.501 only describe slicing?", []),
            ("Explain clause 4.2.2 of TS 29.512.", []),
            ("Explain TS 29.512 4.2.2.", []),
            ("Explain slicing using only 3GPP TS 23.501.", [("23.501", None, None)]),
            ("Use TS 23.501 only.", [("23.501", None, None)]),
            ("只用 TS 23.501 和 TS 23.502", [("23.501", None, None), ("23.502", None, None)]),
            ("Use only TS 29.512 and TS 23.501 19.9.0.", [("29.512", None, None), ("23.501", None, "19.9.0")]),
            ("只用 TS 29.512 的 Rel-17 v17.6.0", [("29.512", 17, "17.6.0")]),
            ("Use TS 29.512 (Release 17, v17.6.0) only.", [("29.512", 17, "17.6.0")]),
            ("Compare TS 29.512 v17.6.0 and v19.7.0.", [("29.512", None, "17.6.0"), ("29.512", None, "19.7.0")]),
            ("Compare TS 29.512 v17.6.0 with 99.9.9.", [("29.512", None, "17.6.0"), ("29.512", None, "99.9.9")]),
            ("Use only TS 29.512 19.7.0.", [("29.512", None, "19.7.0")]),
            ("Use TS 29.512 19.7.0 only.", [("29.512", None, "19.7.0")]),
            ("Compare Release 17 and Release 19 of TS 29.512.", [("29.512", 17, None), ("29.512", 19, None)]),
            ("Use only Rel-19 for TS 29.512.", [("29.512", 19, None)]),
            ("Use only Release 19.", [(None, 19, None)]),
        ]
        for question, expected in cases:
            with self.subTest(question=question):
                self.assertEqual(requested_protocol_scope(question), [
                    {"spec": f"3GPP TS {spec}" if spec else None, "release": release, "version": version}
                    for spec, release, version in expected
                ])

    def test_explicit_exclusions_are_not_includes(self):
        excluded = {"spec": "3GPP TS 29.512", "release": None, "version": "19.7.0", "exclude": True}
        included = {"spec": "3GPP TS 29.512", "release": None, "version": None}
        self.assertEqual(requested_protocol_scope("Do not use TS 29.512 v19.7.0."), [excluded])
        self.assertEqual(requested_protocol_scope("Use only TS 29.512, not TS 29.512 v19.7.0."), [included, excluded])
        self.assertEqual(requested_protocol_scope("Exclude Rel-19 of TS 29.512."), [
            {"spec": "3GPP TS 29.512", "release": 19, "version": None, "exclude": True},
        ])
        self.assertEqual(requested_protocol_scope("Do not use Release 19."), [
            {"spec": None, "release": 19, "version": None, "exclude": True},
        ])


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

    def respond(self, request, *, duplicate=False, query="scope"):
        body = json.loads(request.content)
        if str(request.url) == protocol_index.EMBEDDINGS_URL:
            self.assertEqual(body["input"], [query])
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

    def use_multiple_protocols(self):
        for index, (spec, release, version, document_id) in enumerate((
            ("3GPP TS 29.512", 17, "17.6.0", "TS29512-V17.6.0"),
            ("3GPP TS 29.512", 19, "19.7.0", "TS29512-V19.7.0"),
            ("3GPP TS 23.501", 19, "19.9.0", "TS23501-V19.9.0"),
        )):
            self.metadatas[index * 20:(index + 1) * 20] = [
                {"spec": spec, "release": release, "version": version, "document_id": document_id}
            ] * 20
        self.retriever = retrieval.ProtocolRetriever(self.collection)

    async def test_explicit_documents_filter_dense_and_bm25_before_fusion(self):
        self.use_multiple_protocols()
        cases = [
            ("只用 TS 23.501", ["TS23501-V19.9.0"], self.ids[40:]),
            ("Explain TS 29.512 Rel-17.", ["TS29512-V17.6.0"], self.ids[:20]),
            ("Compare TS 29.512 v17.6.0 and v19.7.0.",
             ["TS29512-V17.6.0", "TS29512-V19.7.0"], self.ids[:40]),
            ("Use only TS 29.512, not TS 29.512 v19.7.0.", ["TS29512-V17.6.0"], self.ids[:20]),
            ("Do not use TS 29.512 v19.7.0.", ["TS23501-V19.9.0", "TS29512-V17.6.0"], self.ids[:20] + self.ids[40:]),
        ]
        for query, documents, allowed_chunks in cases:
            with self.subTest(query=query):
                self.collection.query.return_value = {
                    "ids": [allowed_chunks], "distances": [[0.0] * len(allowed_chunks)],
                }
                async with httpx.AsyncClient(transport=httpx.MockTransport(
                    lambda request: self.respond(request, query=query)
                )) as http:
                    result = await self.retriever.search(query, http, "test-key")
                where = documents[0] if len(documents) == 1 else {"$in": documents}
                self.assertEqual(self.collection.query.call_args.kwargs["where"], {"document_id": where})
                for stage in ("dense", "bm25"):
                    self.assertEqual({row["chunk_id"] for row in result["trace"][stage]}, set(allowed_chunks))
                for stage in ("rrf", "rerank"):
                    self.assertTrue({row["chunk_id"] for row in result["trace"][stage]} <= set(allowed_chunks))
                self.assertEqual(len(result["evidence"]), 5)
                self.assertTrue({row["metadata"]["document_id"] for row in result["evidence"]} <= set(documents))

    async def test_one_missing_version_stops_the_entire_comparison_before_embedding(self):
        self.use_multiple_protocols()
        async def step(stage, operation, *, remote=False):
            self.assertFalse(remote)
            self.assertEqual(stage, "scope")
            scope = await operation()
            self.assertEqual(scope["document_ids"], ["TS29512-V17.6.0"])
            self.assertEqual(scope["missing"], [{"spec": "3GPP TS 29.512", "release": None, "version": "99.9.9"}])
            return scope

        async with httpx.AsyncClient(transport=httpx.MockTransport(Mock(side_effect=AssertionError))) as http:
            with self.assertRaises(ProtocolScopeUnavailable):
                await self.retriever.search("Compare TS 29.512 v17.6.0 with 99.9.9.", http, "test-key", step=step)
        self.collection.query.assert_not_called()

    async def test_empty_included_scope_does_not_fall_back_after_exclusion(self):
        self.use_multiple_protocols()
        async with httpx.AsyncClient(transport=httpx.MockTransport(Mock(side_effect=AssertionError))) as http:
            with self.assertRaises(ProtocolScopeUnavailable):
                await self.retriever.search("Use only TS 23.501, not TS 23.501.", http, "test-key")
        self.collection.query.assert_not_called()
