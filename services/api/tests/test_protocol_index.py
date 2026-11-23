import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import chromadb
import httpx
import numpy as np
from chromadb.api.models.Collection import Collection

from services.api.app.services import protocol_index as index


class ProtocolIndexTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory(ignore_cleanup_errors=True)))
        self.vectors_dir = self.root / "vectors"
        self.vectors_dir.mkdir()
        self.chroma_dir = self.root / "chroma"
        self.pdf_manifest = self.root / "pdf_manifest.json"
        self.document = {"document_id": "TS29512-V17.6.0", "spec": "3GPP TS 29.512", "release": 17, "version": "17.6.0"}
        self.ids = ["chunk-1", "chunk-2"]
        self.vectors = np.eye(2, index.DIMENSION, dtype=np.float32)
        self.official_url = "https://www.etsi.org/deliver/etsi_ts/129500_129599/129512/17.06.00_60/ts_129512v170600p.pdf"
        pdf = self.root / "standard.pdf"
        pdf.write_bytes(b"fixture for checking the PDF digest")
        self.write_json(self.pdf_manifest, {"documents": [{
            **self.document, "official_url": self.official_url, "pdf_path": pdf.name, "sha256": index._sha256(pdf),
        }]})
        source = self.root / "standard.jsonl"
        source.write_text("\n".join(json.dumps({
            "id": chunk_id,
            "text": f"Passage {number}",
            "content_type": "terminology_index" if number == 1 else "prose",
            "metadata": {"release": "17", "authority": "derived_index"} if number == 1 else
            {"clause": "2", "release": "17", "pdf_page_start": 12,
             "clause_path": ["Service", "Create operation", "Association establishment"]},
        }) for number, chunk_id in enumerate(self.ids, 1)), encoding="utf-8")
        self.source_digest = index._sha256(source)
        self.write_json(self.root / "manifest.json", {"files": [{
            **self.document, "file": source.name, "records": 2, "sha256": self.source_digest,
        }]})

    @staticmethod
    def write_json(path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_vectors(self, ids, *, model=index.MODEL, dimension=index.DIMENSION):
        vectors = self.vectors_dir / "standard.npz"
        np.savez(vectors, ids=ids, vectors=self.vectors[:, :dimension], model=model, dim=dimension)
        self.write_json(self.vectors_dir / "manifest.json", {
            "model": index.MODEL, "dimension": index.DIMENSION, "status": "complete", "total_records": 2,
            "package_manifest_sha256": index._sha256(self.root / "manifest.json"),
            "files": [{"file": vectors.name, "records": 2, "source_sha256": self.source_digest, "sha256": index._sha256(vectors)}],
        })

    def import_index(self, document_ids=()):
        return index.import_protocol_index(self.chroma_dir, self.vectors_dir, self.root, self.root, self.pdf_manifest, document_ids)

    async def test_import_retry_and_query_preserve_evidence_identity(self):
        self.write_vectors(self.ids)
        imported = self.import_index()
        self.assertEqual((imported["documents"], imported["imported_chunks"], imported["indexed_chunks"]), (1, 2, 2))
        self.assertEqual(self.import_index()["indexed_chunks"], 2)
        client = chromadb.PersistentClient(path=str(self.chroma_dir))
        if hasattr(client, "close"):
            self.addCleanup(client.close)
        collection = index.open_protocol_index(client)
        self.assertEqual(collection.metadata["source_metadata_version"], index.SOURCE_METADATA_VERSION)
        terminology = collection.get(ids=["chunk-1"], include=["metadatas"])["metadatas"][0]
        self.assertEqual(terminology["authority"], "derived_index")
        self.assertNotIn("clause", terminology)

        def embed(request):
            self.assertEqual(json.loads(request.content), {
                "model": index.MODEL, "input": ["What is the procedure?"],
                "dimensions": index.DIMENSION, "encoding_format": "float",
            })
            return httpx.Response(200, json={"model": index.MODEL, "data": [
                {"index": 0, "embedding": self.vectors[1].tolist()},
            ]})

        async with httpx.AsyncClient(transport=httpx.MockTransport(embed)) as http:
            hits = await index.search_protocol_index(
                collection, "What is the procedure?", http, "test-key", top_k=1, document_id=self.document["document_id"]
            )
        self.assertEqual(hits[0]["chunk_id"], "chunk-2")
        self.assertEqual(hits[0]["text"], "Passage 2")
        self.assertEqual(hits[0]["metadata"], {
            **self.document, "content_type": "prose", "official_url": self.official_url, "clause": "2", "pdf_page_start": 12,
            "section_path": "Create operation > Association establishment",
        })
        self.assertAlmostEqual(hits[0]["distance"], 0)

    def test_rejects_wrong_vectors_before_publishing(self):
        cases = (
            ("ID order", {"ids": self.ids[::-1]}),
            ("embedding model", {"ids": self.ids, "model": "another-model"}),
            ("embedding dimension", {"ids": self.ids, "dimension": 768}),
        )
        for name, inputs in cases:
            with self.subTest(name=name):
                self.write_vectors(**inputs)
                with self.assertRaisesRegex(ValueError, "Vector model, dimension, values or ID order mismatch"):
                    self.import_index()
                self.assertFalse((self.chroma_dir / index.ACTIVE_INDEX).exists())

    def test_rejects_changed_vector_file_before_publishing(self):
        self.write_vectors(self.ids)
        with (self.vectors_dir / "standard.npz").open("ab") as file:
            file.write(b"changed after the manifest was written")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.import_index()
        self.assertFalse((self.chroma_dir / index.ACTIVE_INDEX).exists())

    def test_interrupted_import_is_private_and_resumes(self):
        self.write_vectors(self.ids)
        real_upsert = Collection.upsert

        def interrupted(collection, **batch):
            real_upsert(collection, **{key: values[:1] for key, values in batch.items()})
            raise RuntimeError("interrupted after first vector")

        with patch.object(Collection, "upsert", interrupted):
            with self.assertRaisesRegex(RuntimeError, "first vector"):
                self.import_index()
        client = chromadb.PersistentClient(path=str(self.chroma_dir))
        if hasattr(client, "close"):
            self.addCleanup(client.close)
        with self.assertRaisesRegex(ValueError, "No protocol index"):
            index.open_protocol_index(client)
        complete = self.import_index()
        self.assertEqual(index.open_protocol_index(client).count(), 2)
        smoke = self.import_index([self.document["document_id"]])
        self.assertNotEqual(complete["collection"], smoke["collection"])
        self.assertEqual(index.open_protocol_index(client).name, complete["collection"])
        with self.assertRaisesRegex(ValueError, "incomplete"):
            index.open_protocol_index(client, smoke["collection"])

        manifest = json.loads(self.pdf_manifest.read_text(encoding="utf-8"))
        manifest["revision"] = 2
        self.write_json(self.pdf_manifest, manifest)
        with patch.object(Collection, "upsert", interrupted):
            with self.assertRaisesRegex(RuntimeError, "first vector"):
                self.import_index()
        self.assertEqual(index.open_protocol_index(client).name, complete["collection"])

    def test_wrong_etsi_version_is_rejected_at_import(self):
        self.write_vectors(self.ids)
        manifest = json.loads(self.pdf_manifest.read_text(encoding="utf-8"))
        manifest["documents"][0]["official_url"] = self.official_url.replace("17.06.00", "19.07.00").replace("v170600", "v190700")
        self.write_json(self.pdf_manifest, manifest)
        with self.assertRaisesRegex(ValueError, "PDF URL does not match"):
            self.import_index()
        self.assertFalse((self.chroma_dir / index.ACTIVE_INDEX).exists())

    def test_existing_collection_metadata_is_read_without_writing(self):
        client = Mock()
        client.list_collections.return_value = ["already-present"]
        self.assertIs(
            index._open_or_create_collection(client, "already-present", {"digest": "new"}),
            client.get_collection.return_value,
        )
        client.create_collection.assert_not_called()
        client.get_or_create_collection.assert_not_called()
