"""Persist checkpoints and serialize state changes for a standard-search request."""

from datetime import timedelta

import numpy as np
from sqlalchemy import delete, or_, select, update

from app.database import async_session
from app.models.base import new_uuid, utcnow
from app.models.message import Message, MessageRole
from app.models.protocol_run import ProtocolCheckpoint, ProtocolEvent, ProtocolRun
from app.models.protocol_search_log import ProtocolSearchLog
from app.models.session import Session


LEASE_TIME = timedelta(seconds=20)
CHECKPOINT_TTL = timedelta(hours=24)
TERMINAL = {"complete", "canceled", "expired"}
FAILED = {"search_failed", "generation_interrupted"}
RETRYABLE = {"transient", "unknown", "interrupted", "credential"}
RANK_STAGES = ("dense", "bm25", "rrf", "rerank")


class LeaseLost(Exception):
    pass


async def read_run(request_id):
    async with async_session() as db:
        return await db.get(ProtocolRun, request_id)


def _match(run):
    return update(ProtocolRun).where(
        ProtocolRun.request_id == run.request_id, ProtocolRun.status == run.status,
        ProtocolRun.lease == run.lease,
    )


def has_active_lease(run):
    return run.lease_until is not None and run.lease_until > utcnow()


async def claim(run, retry, *, allow_work=True):
    now = utcnow()
    if run.status in TERMINAL or not run.inputs or (run.lease_until and run.lease_until > now):
        return None
    if run.status == "cancel_requested":
        await finalize(run, "canceled", "user")
        return None
    if now - run.updated_at > CHECKPOINT_TTL:
        if run.status not in FAILED:
            await finalize(run, "expired", "expired")
        return None
    if run.status == "running" and run.in_flight:
        status = "generation_interrupted" if run.stage == "generation" else "search_failed"
        await finalize(run, status, "unknown")
        return None
    if not allow_work or (run.status in FAILED and (not retry or run.error_kind not in RETRYABLE)):
        return None

    async with async_session() as db:
        lease = new_uuid()
        result = await db.execute(_match(run).where(ProtocolRun.updated_at == run.updated_at).values(
            lease=lease, lease_until=now + LEASE_TIME, updated_at=now, status="running", in_flight=False, error_kind=None,
        ))
        await db.commit()
        return lease if result.rowcount == 1 else None


def _owned(run):
    return update(ProtocolRun).where(
        ProtocolRun.request_id == run.request_id, ProtocolRun.lease == run.lease,
        ProtocolRun.status == "running", ProtocolRun.lease_until > utcnow(),
    )


async def _update(db, run, **values):
    result = await db.execute(_owned(run).values(updated_at=utcnow(), **values))
    if result.rowcount != 1:
        raise LeaseLost()


async def heartbeat(run):
    async with async_session() as db:
        await _update(db, run, lease_until=utcnow() + LEASE_TIME)
        await db.commit()


async def read_checkpoint(request_id, stage):
    async with async_session() as db:
        row = await db.get(ProtocolCheckpoint, (request_id, stage))
        if row is None:
            return False, None
        value = np.frombuffer(row.binary, dtype="<f4") if row.binary is not None else row.payload["value"]
        return True, value


async def start_stage(run, stage, *, remote):
    attempts = {**run.attempts, stage: run.attempts.get(stage, 0) + 1}
    async with async_session() as db:
        await _update(db, run, stage=stage, in_flight=remote, attempts=attempts)
        await db.commit()
    run.attempts = attempts
    run.stage = stage
    run.in_flight = remote


async def clear_in_flight(run):
    async with async_session() as db:
        await _update(db, run, in_flight=False)
        await db.commit()
    run.in_flight = False


async def save_checkpoint(run, stage, value, elapsed_ms):
    payload = {"elapsed_ms": elapsed_ms}
    binary = None
    if stage == "embedding":
        binary = np.asarray(value, dtype="<f4").tobytes()
    else:
        payload["value"] = value
    async with async_session() as db:
        await _update(db, run, stage=stage, in_flight=False)
        db.add(ProtocolCheckpoint(request_id=run.request_id, stage=stage, payload=payload, binary=binary))
        await db.commit()
    run.in_flight = False


async def append_event(run, token):
    seq = run.last_seq + 1
    attempt = run.attempt + (token is None)
    async with async_session() as db:
        await _update(db, run, last_seq=seq, attempt=attempt)
        db.add(ProtocolEvent(request_id=run.request_id, seq=seq, attempt=attempt, token=token))
        await db.commit()
    run.last_seq, run.attempt = seq, attempt


async def record_generation_dispatch(run, state):
    stage = "generation_dispatch"
    payload = {"value": {"attempt": run.attempt, "state": state}}
    async with async_session() as db:
        await _update(db, run)
        row = await db.get(ProtocolCheckpoint, (run.request_id, stage))
        if row is None:
            db.add(ProtocolCheckpoint(request_id=run.request_id, stage=stage, payload=payload))
        else:
            row.payload = payload
        await db.commit()


async def read_events(request_id, after):
    async with async_session() as db:
        return (await db.scalars(select(ProtocolEvent).where(
            ProtocolEvent.request_id == request_id, ProtocolEvent.seq > after,
        ).order_by(ProtocolEvent.seq).limit(200))).all()


async def request_cancel(run):
    while run.status not in TERMINAL | {"cancel_requested"} and run.inputs:
        if run.lease_until and run.lease_until > utcnow():
            async with async_session() as db:
                await db.execute(_match(run).values(status="cancel_requested", updated_at=utcnow()))
                await db.commit()
        else:
            await finalize(run, "canceled", "user")
        run = await read_run(run.request_id)
    return run.status


async def _write_log(db, run, status, error_kind, answer, citations):
    checkpoints = (await db.scalars(select(ProtocolCheckpoint).where(
        ProtocolCheckpoint.request_id == run.request_id, ProtocolCheckpoint.stage != "embedding",
    ))).all()
    stages = {row.stage: row.payload for row in checkpoints}
    indexed = stages.get("index", {}).get("value", {})
    prepared = stages.get("prompt", {}).get("value", {})
    dispatch = stages.get("generation_dispatch", {}).get("value", {})
    dispatch_state = dispatch["state"] if dispatch.get("attempt") == run.attempt else "not_started"
    prepared_ids = prepared.get("context_chunk_ids", [])
    if not dispatch and "generation" in stages and prepared_ids:
        dispatch_state = "acknowledged"
    retrieval = {
        "query": run.inputs["query"], "collection": run.inputs.get("collection"),
        "request_status": status, "failure_stage": run.stage if error_kind else None, "error_kind": error_kind,
        "attempts": run.attempts,
        "elapsed_ms": {stage: entry["elapsed_ms"] for stage, entry in stages.items() if "elapsed_ms" in entry},
        "trace": {
            stage: [{"chunk_id": item[0], "rank": rank, "score": item[1]}
                    for rank, item in enumerate(stages[stage]["value"], 1)]
            for stage in RANK_STAGES if stage in stages
        },
        "prepared_context_chunk_ids": prepared_ids,
        "generation_dispatch": dispatch_state,
        "context_chunk_ids": prepared_ids if dispatch_state == "acknowledged" else [],
        **indexed,
        "parameters": prepared.get("parameters", indexed.get("parameters", {})),
    }
    if "scope" in stages:
        retrieval["scope"] = stages["scope"]["value"]
    log = await db.get(ProtocolSearchLog, run.request_id)
    log.status = status if status in {"complete", "search_failed", "generation_interrupted"} else (
        "generation_interrupted" if answer else "search_failed"
    )
    log.answer = answer
    log.citations = citations
    log.retrieval = retrieval


async def finalize(run, status, error_kind=None, citations=None, *, worker=False):
    async with async_session() as db:
        current = await db.get(ProtocolRun, run.request_id)
        if current is None or not current.inputs or current.lease != run.lease or current.status in TERMINAL:
            return
        if worker and current.status not in {"running", "cancel_requested"}:
            return
        now = utcnow()
        if not worker and current.lease_until and current.lease_until > now:
            return
        if current.status == "cancel_requested":
            status, error_kind = "canceled", "user"
        if status == "complete" and await db.get(Session, current.session_id) is None:
            status, error_kind = "canceled", "session"

        message_id = new_uuid() if status == "complete" else None
        target = _match(current)
        if not worker:
            target = target.where(or_(ProtocolRun.lease_until.is_(None), ProtocolRun.lease_until <= now))
        values = dict(
            status=status, error_kind=error_kind, lease=None, lease_until=None, in_flight=False,
            updated_at=utcnow(), message_id=message_id,
        )
        if status == "expired":
            values["inputs"] = {}
            values["purged_at"] = now
        changed = await db.execute(target.values(**values).execution_options(synchronize_session=False))
        if changed.rowcount != 1:
            return
        answer = "".join((await db.scalars(select(ProtocolEvent.token).where(
            ProtocolEvent.request_id == current.request_id, ProtocolEvent.attempt == current.attempt,
            ProtocolEvent.token.is_not(None),
        ).order_by(ProtocolEvent.seq))).all())
        citations = (citations or []) if status == "complete" else []
        if message_id:
            db.add(Message(id=message_id, session_id=current.session_id, role=MessageRole.assistant, content=answer,
                           tool_calls={"request_id": current.request_id, "citations": citations}))
        await _write_log(db, current, status, error_kind, answer, citations)
        if status == "expired":
            await _delete_checkpoints(db, [current.request_id])
        await db.commit()


async def done_payload(run):
    async with async_session() as db:
        log = await db.get(ProtocolSearchLog, run.request_id)
        expired = run.status not in TERMINAL and (
            not run.inputs or utcnow() - run.updated_at > CHECKPOINT_TTL
        )
        return {
            "done": True, "request_id": run.request_id, "status": "expired" if expired else run.status, "stage": run.stage,
            "message_id": run.message_id or "", "answer": log.answer, "citations": log.citations,
            "retryable": not expired and (run.status == "paused" or run.error_kind in RETRYABLE),
            "error_kind": "expired" if expired else run.error_kind, "seq": run.last_seq,
        }


async def _delete_checkpoints(db, request_ids):
    await db.execute(delete(ProtocolCheckpoint).where(ProtocolCheckpoint.request_id.in_(request_ids)))
    await db.execute(delete(ProtocolEvent).where(ProtocolEvent.request_id.in_(request_ids)))


async def prune_checkpoints():
    now = utcnow()
    async with async_session() as db:
        abandoned = (await db.scalars(select(ProtocolRun).where(
            or_(ProtocolRun.lease_until.is_(None), ProtocolRun.lease_until <= now),
            ProtocolRun.status.in_({"queued", "paused", "running", "cancel_requested"}),
            or_(ProtocolRun.status == "cancel_requested", ProtocolRun.updated_at < now - CHECKPOINT_TTL),
        ).limit(100))).all()
    for run in abandoned:
        await finalize(run, "expired", "expired")

    async with async_session() as db:
        expired = select(ProtocolRun.request_id).where(
            ProtocolRun.updated_at < now - CHECKPOINT_TTL,
            ProtocolRun.status.in_(TERMINAL | FAILED),
            ProtocolRun.purged_at.is_(None),
        )
        ids = (await db.scalars(expired.order_by(ProtocolRun.updated_at).limit(100))).all()
        if ids:
            await _delete_checkpoints(db, ids)
            await db.execute(update(ProtocolRun).where(ProtocolRun.request_id.in_(ids)).values(inputs={}, purged_at=now))
        await db.commit()
