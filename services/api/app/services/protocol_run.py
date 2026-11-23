"""Execute and replay a standard-search request using durable checkpoints."""

import asyncio
import json
import logging
import random
from contextlib import aclosing
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from functools import partial
from time import monotonic, perf_counter

import httpx
from anyio import CancelScope, create_task_group, fail_after, move_on_after, sleep
from anyio.to_thread import run_sync

from app.services.chroma_service import chroma
from app.services.openclaw_client import openclaw
from app.services.protocol_attachment import extract_protocol_attachment
from app.services.protocol_chat import ProtocolCitations, retrieve_protocol_evidence
from app.services.protocol_index import open_protocol_index
from app.services.protocol_retrieval import ProtocolRerankError, retrieval_parameters
from app.services.protocol_scope import ProtocolScopeUnavailable, requested_protocol_scope
from app.services import protocol_run_store as store


logger = logging.getLogger(__name__)
_workers = {}
_slots = asyncio.Semaphore(2)
_WAIT_LIMIT = 10
_REQUEST_TIMEOUT = 180
_CONTEXT_BYTES = 120000
_ANSWER_LIMIT = 65536


class StageError(Exception):
    def __init__(self, kind):
        super().__init__(kind)
        self.kind = kind


def _failure(error):
    if isinstance(error, ProtocolRerankError):
        error = error.__cause__
    if isinstance(error, httpx.HTTPStatusError):
        if error.response.status_code == 402:
            return "billing", None
        if error.response.status_code in {400, 403}:
            try:
                payload = error.response.json()
            except (ValueError, httpx.ResponseNotRead):
                payload = None
            detail = payload.get("error", payload) if isinstance(payload, dict) else None
            if isinstance(detail, dict) and detail.get("code") in ("Arrearage", "isv.OUT_OF_SERVICE"):
                return "billing", None
        if error.response.status_code in {429, 503}:
            retry_after = error.response.headers.get("Retry-After")
            if retry_after:
                try:
                    return "transient", max(0, int(retry_after))
                except ValueError:
                    try:
                        return "transient", max(0, parsedate_to_datetime(retry_after).timestamp() - datetime.now(timezone.utc).timestamp())
                    except (ValueError, TypeError, OverflowError):
                        pass
            return "transient", random.uniform(0.25, 0.75)
        return ("unknown" if error.response.status_code >= 500 else "permanent"), None
    if isinstance(error, (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout)):
        return "transient", random.uniform(0.25, 0.75)
    if isinstance(error, httpx.TransportError):
        return "unknown", None
    if isinstance(error, StageError):
        return error.kind, None
    if isinstance(error, ProtocolScopeUnavailable):
        return "scope_unavailable", None
    return "permanent", None


async def _retry(run, stage, error):
    kind, delay = _failure(error)
    if delay is not None and delay <= _WAIT_LIMIT and run.attempts.get(stage, 0) < 2:
        await store.clear_in_flight(run)
        await sleep(delay)
        return
    raise StageError(kind) from error


async def _step(run, stage, operation, *, remote=False):
    found, value = await store.read_checkpoint(run.request_id, stage)
    if found:
        return value
    while True:
        await store.start_stage(run, stage, remote=remote)
        start = perf_counter()
        try:
            value = await operation()
        except Exception as error:
            await _retry(run, stage, error)
            continue
        await store.save_checkpoint(run, stage, value, round((perf_counter() - start) * 1000))
        return value


async def _prepare_prompt(run):
    make_step = partial(_step, run)

    async def attachments():
        sections = []
        remaining = 30000
        for file in run.inputs["files"]:
            if remaining <= 0:
                break
            try:
                text = await extract_protocol_attachment(file["path"], file["name"], file["type"], min(12000, remaining))
            except TimeoutError:
                text = "[附件提取超时]"
            except OSError:
                text = "[附件不可读取]"
            text = (text.strip() or "[未能提取附件文字]")[:min(12000, remaining)]
            sections.append(f"--- 文件：{file['name']} ---\n{text}")
            remaining -= len(text)
        return "\n\n".join(sections)

    async def index():
        collection = await run_sync(lambda: open_protocol_index(chroma.client))
        return {
            "collection": collection.name, "index_metadata": dict(collection.metadata or {}),
            "parameters": retrieval_parameters(),
        }

    files = await make_step("attachments", attachments)
    indexed = await make_step("index", index)
    if indexed["parameters"] != retrieval_parameters():
        raise StageError("configuration_changed")
    result = await retrieve_protocol_evidence(run.inputs["query"], collection=indexed["collection"], step=make_step)
    renderer = ProtocolCitations(result["evidence"])
    prompt = run.inputs["prompt"] + "\n\n" + files + renderer.prompt
    input_bytes = len(prompt.encode()) + sum(len(message["content"].encode()) for message in run.inputs["messages"])
    if input_bytes > _CONTEXT_BYTES:
        raise StageError("context_limit")
    return {
        "evidence": [{"chunk_id": row["chunk_id"], "metadata": row["metadata"]} for row in result["evidence"]],
        "prompt": prompt,
        "context_chunk_ids": [row["chunk_id"] for row in result["evidence"]],
        "parameters": result["parameters"],
    }


async def _answer(run, prepared, key):
    found, citations = await store.read_checkpoint(run.request_id, "generation")
    if found:
        return citations
    if run.inputs.get("base_url") and not key:
        raise StageError("credential")

    while True:
        await store.start_stage(run, "generation", remote=bool(prepared["evidence"]))
        await store.append_event(run, None)
        start = flush_at = perf_counter()
        renderer = ProtocolCitations(prepared["evidence"])
        buffer = ""
        emitted = False
        acknowledged = False
        length = 0

        async def acknowledge():
            nonlocal acknowledged
            if not acknowledged:
                await store.record_generation_dispatch(run, "acknowledged")
                acknowledged = True

        try:
            if not prepared["evidence"]:
                buffer = "未检索到可用于回答的 3GPP 协议证据。"
            else:
                await store.record_generation_dispatch(run, "dispatch_unknown")
                stream = openclaw.chat_stream(
                    run.inputs["messages"], system_prompt=prepared["prompt"], user_id=run.session_id,
                    model=run.inputs["model"], api_base_url=run.inputs.get("base_url"), api_key=key,
                    require_complete=True, on_accepted=acknowledge, max_tokens=4096,
                )
                async with aclosing(stream):
                    async for token in stream:
                        if not acknowledged:
                            await acknowledge()
                        visible = renderer.consume(token)
                        length += len(visible)
                        if length > _ANSWER_LIMIT:
                            raise StageError("interrupted")
                        buffer += visible
                        if buffer and (not emitted or len(buffer) >= 2048 or perf_counter() - flush_at >= 0.35):
                            await store.append_event(run, buffer)
                            buffer, emitted, flush_at = "", True, perf_counter()
                if not (emitted or buffer.strip()):
                    raise StageError("interrupted")
            suffix, citations = renderer.finish()
        except LeaseLost:
            raise
        except Exception as error:
            if buffer:
                await store.append_event(run, buffer)
            if emitted or buffer:
                raise StageError("interrupted") from error
            if isinstance(error, RuntimeError):
                raise StageError("unknown") from error
            await _retry(run, "generation", error)
            continue
        if buffer or suffix:
            await store.append_event(run, buffer + suffix)
        await store.save_checkpoint(run, "generation", citations, round((perf_counter() - start) * 1000))
        return citations


LeaseLost = store.LeaseLost


async def _heartbeat(run, scope):
    while True:
        await sleep(2)
        try:
            await store.heartbeat(run)
        except Exception:
            scope.cancel()
            return


async def _execute(run, key, handle):
    status, kind, citations = "paused", None, None
    with CancelScope() as scope:
        handle["scope"] = scope
        if handle.get("stop"):
            scope.cancel()
        async with create_task_group() as group:
            group.start_soon(_heartbeat, run, scope)
            try:
                with fail_after(_REQUEST_TIMEOUT):
                    async with _slots:
                        if ("embedding" in run.attempts and "scope" not in run.attempts
                                and requested_protocol_scope(run.inputs["query"])):
                            raise StageError("configuration_changed")
                        prepared = await _step(run, "prompt", partial(_prepare_prompt, run))
                        citations = await _answer(run, prepared, key)
                status = "complete"
            except LeaseLost:
                pass
            except Exception as error:
                status = "generation_interrupted" if run.stage == "generation" else "search_failed"
                if isinstance(error, TimeoutError):
                    kind = "unknown" if run.in_flight else "transient"
                else:
                    kind = _failure(error)[0]
                logger.warning("Protocol request %s failed at %s (%s)", run.request_id, run.stage, kind)
            finally:
                group.cancel_scope.cancel()

    if status == "paused" and run.in_flight:
        status = "generation_interrupted" if run.stage == "generation" else "search_failed"
        kind = "interrupted" if run.stage == "generation" else "unknown"
    try:
        with move_on_after(5, shield=True):
            await store.finalize(run, status, kind, citations, worker=True)
            current = await store.read_run(run.request_id)
            if current.status == "cancel_requested" and current.lease == run.lease:
                await store.finalize(run, "canceled", "user", worker=True)
    except Exception as error:
        logger.warning("Protocol request %s could not save its final state (%s)", run.request_id, type(error).__name__)
    finally:
        if _workers.get(run.request_id) is handle:
            _workers.pop(run.request_id, None)


def stop_protocol_worker(request_id, worker=None):
    handle = _workers.get(request_id)
    if handle and (worker is None or worker is handle["task"]):
        handle["stop"] = True
        if "scope" in handle:
            handle["scope"].cancel()


async def stop_protocol_workers():
    tasks = []
    for request_id, handle in list(_workers.items()):
        stop_protocol_worker(request_id)
        tasks.append(handle["task"])
    if tasks:
        await asyncio.wait(tasks, timeout=5)


async def maintain_protocol_runs():
    while True:
        try:
            await store.prune_checkpoints()
        except Exception as error:
            logger.warning("Protocol checkpoint cleanup failed (%s)", type(error).__name__)
        await sleep(60)


def _frame(data):
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_protocol_request(request_id, after, retry, key):
    worker = None
    worker_lease = None
    recovered = False
    heartbeat_at = monotonic()
    try:
        yield _frame({"request_id": request_id})
        while True:
            run = await store.read_run(request_id)
            worker_finished = worker is not None and worker.done()
            give_up = recovered and worker_finished and run.status == "running" and run.lease == worker_lease
            missing_key = False
            if (worker is None or worker_finished) and not give_up and run.status not in store.TERMINAL:
                if run.inputs.get("base_url") and not key:
                    missing_key = True
                    if not store.has_active_lease(run):
                        generation_saved, _ = await store.read_checkpoint(request_id, "generation")
                        missing_key = not generation_saved
                paused_here = run.status == "paused" and worker_finished
                lease = None if paused_here else await store.claim(run, retry, allow_work=not missing_key)
                if not lease and retry and not missing_key and run.status == "running" and run.in_flight:
                    current = await store.read_run(request_id)
                    if current.error_kind == "unknown" and current.lease is None:
                        lease = await store.claim(current, retry=True)
                if lease:
                    retry = False
                    recovered = worker_finished
                    worker_lease = lease
                    claimed = await store.read_run(request_id)
                    handle = {}
                    _workers[request_id] = handle
                    worker = asyncio.create_task(_execute(claimed, key, handle))
                    handle["task"] = worker
            for event in await store.read_events(request_id, after):
                after = event.seq
                yield _frame({"seq": event.seq, "attempt": event.attempt, **(
                    {"reset": True} if event.token is None else {"token": event.token}
                )})
            run = await store.read_run(request_id)
            give_up = give_up and run.status == "running" and run.lease == worker_lease
            needs_key = missing_key and not store.has_active_lease(run) and (
                run.status in {"queued", "paused", "running"} or run.error_kind in store.RETRYABLE
            )
            if (run.status in store.TERMINAL | store.FAILED or needs_key or give_up
                    or (run.status == "paused" and worker is not None and worker.done())):
                if after < run.last_seq and run.inputs:
                    continue
                done = await store.done_payload(run)
                if needs_key and done["status"] not in store.TERMINAL:
                    done.update(retryable=True, error_kind="credential")
                elif give_up and done["status"] == "running":
                    done.update(status="paused", retryable=True, error_kind="unknown" if run.in_flight else "transient")
                yield _frame(done)
                break
            if monotonic() - heartbeat_at >= 12:
                yield ": keepalive\n\n"
                heartbeat_at = monotonic()
            await sleep(0.15)
    finally:
        if worker is not None and not worker.done():
            stop_protocol_worker(request_id, worker)
            with move_on_after(3, shield=True):
                await asyncio.shield(worker)
