"""Import precomputed 3GPP vectors and retrieve their source passages."""

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

import httpx
import numpy as np


MODEL = "qwen3.7-text-embedding"
DIMENSION = 1024
COLLECTION = "3gpp_protocol_qwen_v1"
ACTIVE_INDEX = "active_protocol_index.json"
EMBEDDINGS_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
INDEX_METADATA = {"embedding_model": MODEL, "dimension": DIMENSION, "hnsw:space": "cosine"}
SOURCE_METADATA_VERSION = 2
DOCUMENT_FIELDS = ("document_id", "spec", "release", "version")
SOURCE_FIELDS = ("clause", "authority", "pdf_page_start", "pdf_page_end", "printed_page_start", "printed_page_end")


def official_protocol_url(metadata: dict) -> str:
    spec = re.fullmatch(r"3GPP TS (\d{2})\.(\d{3})", metadata["spec"])
    version = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{1,2})", metadata["version"])
    if not spec or not version or int(version[1]) != int(metadata["release"]):
        raise ValueError("Invalid 3GPP protocol identity")
    number = "1" + spec[1] + spec[2]
    series = number[:4]
    formatted = [f"{int(part):02d}" for part in version.groups()]
    url = metadata["official_url"]
    if not re.fullmatch(
        rf"https://www\.etsi\.org/deliver/etsi_ts/{series}00_{series}99/{number}/"
        rf"{re.escape('.'.join(formatted))}_\d+/ts_{number}v{''.join(formatted)}p\.pdf",
        url,
    ):
        raise ValueError("Official PDF URL does not match the protocol version")
    return url


def _sha256(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def _checked_file(root: Path, relative_path: str, sha256: str) -> Path:
    path = (root / relative_path).resolve()
    if not path.is_relative_to(root.resolve()) or _sha256(path) != sha256:
        raise ValueError(f"Asset path or SHA-256 mismatch: {relative_path}")
    return path


def _valid_vectors(matrix: np.ndarray, rows: int) -> bool:
    return (
        matrix.shape == (rows, DIMENSION)
        and np.isfinite(matrix).all()
        and np.any(matrix != 0, axis=1).all()
    )


def _load_document(vectors_dir, evidence_dir, pdf, entry, vector_entry):
    source = _checked_file(evidence_dir, entry["file"], entry["sha256"])
    if vector_entry["source_sha256"] != entry["sha256"] or vector_entry["records"] != entry["records"]:
        raise ValueError(f"Vector and JSONL manifests disagree: {source.name}")
    vector_file = _checked_file(vectors_dir, vector_entry["file"], vector_entry["sha256"])
    with source.open(encoding="utf-8") as file:
        rows = [json.loads(line) for line in file if line.strip()]
    ids = [row["id"] for row in rows]
    if not ids or len(ids) != entry["records"] or len(ids) != len(set(ids)):
        raise ValueError(f"Invalid or duplicate Chunk IDs: {source.name}")
    with np.load(vector_file, allow_pickle=False) as data:
        vectors = data["vectors"]
        if (
            data["ids"].tolist() != ids
            or data["model"].item() != MODEL
            or data["dim"].item() != DIMENSION
            or vectors.dtype != np.float32
            or not _valid_vectors(vectors, len(ids))
        ):
            raise ValueError(f"Vector model, dimension, values or ID order mismatch: {vector_file.name}")

    identity = {field: entry[field] for field in DOCUMENT_FIELDS}
    if any(identity[field] != pdf[field] for field in DOCUMENT_FIELDS):
        raise ValueError(f"PDF version mismatch: {source.name}")
    official_url = official_protocol_url(pdf)
    metadata = []
    for row in rows:
        source_metadata = row["metadata"]
        if any(str(source_metadata.get(field, value)) != str(value) for field, value in identity.items()):
            raise ValueError(f"Chunk and document version mismatch: {row['id']}")
        clause_path = source_metadata.get("clause_path") or []
        if not isinstance(clause_path, list) or any(not isinstance(label, str) for label in clause_path):
            raise ValueError(f"Invalid clause path: {row['id']}")
        section_path = " > ".join(label.strip() for label in clause_path[-2:] if label.strip())
        if not section_path and isinstance(source_metadata.get("title"), str):
            section_path = source_metadata["title"].strip()
        metadata.append({
            **identity,
            "content_type": row["content_type"],
            "official_url": official_url,
            **{field: source_metadata[field] for field in SOURCE_FIELDS if source_metadata.get(field) is not None},
            **({"section_path": section_path} if section_path else {}),
        })
    return ids, vectors, [row["text"] for row in rows], metadata


def _collection_names(client):
    return {item if isinstance(item, str) else item.name for item in client.list_collections()}


def _open_or_create_collection(client, name, metadata):
    if name not in _collection_names(client):
        try:
            return client.create_collection(name, embedding_function=None, metadata=metadata)
        except Exception:
            if name not in _collection_names(client):
                raise
    return client.get_collection(name, embedding_function=None)


def _write_manifest(destination, value):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent, delete=False) as file:
        temporary = Path(file.name)
        json.dump(value, file)
    try:
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def import_protocol_index(chroma_dir, vectors_dir, evidence_dir, pdf_root, pdf_manifest, document_ids=()):
    """Validate the selected assets, then upsert them into the matching collection."""
    import chromadb

    vector_manifest_path = vectors_dir / "manifest.json"
    vector_manifest = json.loads(vector_manifest_path.read_text(encoding="utf-8"))
    if (vector_manifest["model"], vector_manifest["dimension"], vector_manifest["status"]) != (MODEL, DIMENSION, "complete"):
        raise ValueError("Expected a complete 1024-dimensional Qwen vector package")
    evidence_manifest_path = _checked_file(evidence_dir, "manifest.json", vector_manifest["package_manifest_sha256"])
    evidence = json.loads(evidence_manifest_path.read_text(encoding="utf-8"))
    pdfs = {row["document_id"]: row for row in json.loads(pdf_manifest.read_text(encoding="utf-8"))["documents"]}
    vector_files = {Path(entry["file"]).stem: entry for entry in vector_manifest["files"]}
    selected = [entry for entry in evidence["files"] if not document_ids or entry["document_id"] in document_ids]
    if not selected or set(document_ids) - {entry["document_id"] for entry in selected}:
        raise ValueError("Requested document version is missing from the package")

    expected_rows = sum(entry["records"] for entry in selected)
    if not document_ids and (
        expected_rows != vector_manifest["total_records"] or len(selected) != len(vector_files)
    ):
        raise ValueError("Chunk count does not match the complete vector package")
    metadata = {
        **INDEX_METADATA,
        "source_metadata_version": SOURCE_METADATA_VERSION,
        "vector_manifest_sha256": _sha256(vector_manifest_path),
        "pdf_manifest_sha256": _sha256(pdf_manifest),
        "expected_rows": expected_rows,
        "document_count": len(selected),
        "scope": "smoke" if document_ids else "complete",
    }
    fingerprint = hashlib.sha256(json.dumps([metadata, sorted(set(document_ids))], sort_keys=True).encode()).hexdigest()
    name = f"{COLLECTION}_{fingerprint[:24]}"
    metadata["fingerprint"] = fingerprint
    client = chromadb.PersistentClient(path=str(chroma_dir))
    try:
        collection = _open_or_create_collection(client, name, metadata)
        current = collection.metadata or {}
        if any(current.get(key) != value for key, value in metadata.items()):
            raise ValueError("Existing protocol collection belongs to a different asset bundle")
        ready_file = Path(chroma_dir) / f"{name}.ready.json"
        ready_manifest = {"collection": name, "fingerprint": fingerprint, "rows": expected_rows}
        ready = ready_file.is_file() and json.loads(ready_file.read_text(encoding="utf-8")) == ready_manifest
        seen_ids = set()
        for entry in selected:
            pdf = pdfs[entry["document_id"]]
            _checked_file(pdf_root, pdf["pdf_path"], pdf["sha256"])
            ids, vectors, texts, metadatas = _load_document(
                vectors_dir, evidence_dir, pdf, entry, vector_files[Path(entry["file"]).stem]
            )
            if seen_ids.intersection(ids):
                raise ValueError("Duplicate Chunk IDs across documents")
            seen_ids.update(ids)
            if not ready:
                for start in range(0, len(ids), 256):
                    batch = slice(start, start + 256)
                    collection.upsert(
                        ids=ids[batch], embeddings=vectors[batch], documents=texts[batch], metadatas=metadatas[batch]
                    )
            del ids, vectors, texts, metadatas
        indexed = collection.get(include=[])["ids"]
        if len(indexed) != expected_rows or set(indexed) != seen_ids:
            raise ValueError("Protocol collection does not contain exactly the selected Chunk IDs")
        if not ready:
            _write_manifest(ready_file, ready_manifest)
        if not document_ids:
            _write_manifest(Path(chroma_dir) / ACTIVE_INDEX, {"collection": name})
        return {"documents": len(selected), "imported_chunks": len(seen_ids), "indexed_chunks": len(indexed), "collection": name}
    finally:
        # Older Chroma clients did not expose close().
        if hasattr(client, "close"):
            client.close()


def published_collection_name(client):
    path = Path(client.get_settings().persist_directory) / ACTIVE_INDEX
    if not path.is_file():
        raise ValueError("No protocol index has been published")
    name = json.loads(path.read_text(encoding="utf-8"))["collection"]
    if not re.fullmatch(rf"{COLLECTION}_[a-f0-9]{{24}}", name):
        raise ValueError("Invalid protocol index name")
    return name


def open_protocol_index(client, name=None):
    name = name or published_collection_name(client)
    if not re.fullmatch(rf"{COLLECTION}_[a-f0-9]{{24}}", name):
        raise ValueError("Invalid protocol index name")
    ready_file = Path(client.get_settings().persist_directory) / f"{name}.ready.json"
    if not ready_file.is_file():
        raise ValueError("Protocol collection has not finished building")
    ready = json.loads(ready_file.read_text(encoding="utf-8"))
    collection = client.get_collection(name, embedding_function=None)
    metadata = collection.metadata or {}
    if any(metadata.get(key) != value for key, value in INDEX_METADATA.items()) or (
        ready != {"collection": name, "fingerprint": metadata.get("fingerprint"), "rows": metadata.get("expected_rows")}
        or metadata.get("scope") != "complete"
        or collection.count() != metadata.get("expected_rows")
    ):
        raise ValueError("Protocol collection is incomplete or incompatible")
    return collection


async def embed_protocol_query(query: str, http: httpx.AsyncClient, api_key: str):
    if not query.strip():
        raise ValueError("A nonempty query is required")
    if not api_key.strip():
        raise ValueError("A DashScope API key is required")
    response = await http.post(
        EMBEDDINGS_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": MODEL, "input": [query], "dimensions": DIMENSION, "encoding_format": "float"},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    data = payload["data"]
    if payload.get("model") != MODEL or len(data) != 1 or data[0]["index"] != 0:
        raise ValueError("Qwen returned an unexpected embedding response")
    vectors = np.asarray([data[0]["embedding"]], dtype=np.float32)
    if not _valid_vectors(vectors, 1):
        raise ValueError("Qwen query embedding must be a finite, nonzero 1024-dimensional vector")
    return vectors[0]


def dense_protocol_search(collection, vector, *, top_k=50, document_id=None, include_content=True):
    if top_k < 1:
        raise ValueError("A positive top_k is required")
    result = collection.query(
        query_embeddings=np.asarray([vector], dtype=np.float32),
        n_results=top_k,
        where={"document_id": document_id} if document_id else None,
        include=["documents", "metadatas", "distances"] if include_content else ["distances"],
    )
    if not include_content:
        return [
            {"chunk_id": chunk_id, "distance": distance}
            for chunk_id, distance in zip(result["ids"][0], result["distances"][0], strict=True)
        ]
    return [
        {"chunk_id": chunk_id, "text": text, "metadata": metadata, "distance": distance}
        for chunk_id, text, metadata, distance in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0], strict=True
        )
    ]


async def search_protocol_index(collection, query: str, http: httpx.AsyncClient, api_key: str, *, top_k=50, document_id=None):
    vector = await embed_protocol_query(query, http, api_key)
    return dense_protocol_search(collection, vector, top_k=top_k, document_id=document_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vectors-dir", required=True, type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--pdf-root", required=True, type=Path, help="Base directory of the paths in the PDF manifest")
    parser.add_argument("--pdf-manifest", required=True, type=Path)
    parser.add_argument("--chroma-dir", required=True, type=Path)
    parser.add_argument("--document", action="append", default=[], help="Document ID to import. Defaults to all versions.")
    args = parser.parse_args()
    print(json.dumps(import_protocol_index(
        args.chroma_dir, args.vectors_dir, args.evidence_dir, args.pdf_root, args.pdf_manifest, args.document
    )))
