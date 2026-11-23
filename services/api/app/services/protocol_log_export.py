"""Export recent protocol search samples as JSONL from the backend database."""

import argparse
import asyncio
import json
import re

from sqlalchemy import select

from app.database import async_session, engine
from app.models.protocol_search_log import ProtocolSearchLog


_REDACTIONS = (
    (re.compile(r"[\w.+-]+@[\w.-]+\.[A-Z]{2,}", re.IGNORECASE), "[email]"),
    (re.compile(r"(?<!\d)(?:\+86[ -]?)?1[3-9]\d{9}(?!\d)"), "[phone]"),
    (re.compile(r"\b(?:Bearer\s+[A-Z0-9._~+/=-]+|(?:sk|ak)-[A-Z0-9_-]{8,})\b", re.IGNORECASE), "[credential]"),
)


def _redact(text: str) -> str:
    for pattern, replacement in _REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def export_record(row: ProtocolSearchLog) -> dict:
    retrieval = {**row.retrieval, "query": _redact(row.retrieval.get("query", row.query))}
    return {
        "request_id": row.request_id,
        "timestamp": row.created_at.isoformat() + "Z",
        "question": _redact(row.question),
        "query": _redact(row.query),
        "model": _redact(row.model),
        "status": row.retrieval.get("request_status", row.status),
        "retrieval": retrieval,
        "answer": _redact(row.answer),
        "citations": row.citations,
    }


async def export_samples(limit: int) -> None:
    try:
        async with async_session() as session:
            statement = select(ProtocolSearchLog).order_by(
                ProtocolSearchLog.created_at.desc(), ProtocolSearchLog.request_id
            ).limit(limit)
            rows = await session.stream_scalars(statement)
            async for row in rows:
                print(json.dumps(export_record(row), ensure_ascii=True))
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    asyncio.run(export_samples(args.limit))
