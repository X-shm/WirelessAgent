import asyncio
import json
from contextlib import aclosing
from pathlib import Path
from time import monotonic, sleep
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from app.database import async_session
from app.main import app
from app.models.base import utcnow
from app.models.file import File
from app.models.protocol_run import ProtocolRun
from app.models.protocol_search_log import ProtocolSearchLog
from app.routes import chat
from app.services import openclaw_client, protocol_attachment, protocol_run, protocol_run_store
from app.services.protocol_log_export import export_record
from app.services.protocol_scope import ProtocolScopeUnavailable


REL17 = "https://www.etsi.org/deliver/etsi_ts/129500_129599/129512/17.06.00_60/ts_129512v170600p.pdf"
REL19 = "https://www.etsi.org/deliver/etsi_ts/129500_129599/129512/19.07.00_60/ts_129512v190700p.pdf"


def result(query, **_):
    return {
        "query": query,
        "trace": {"dense": [{"chunk_id": "r17", "rank": 1}]},
        "parameters": {"rrf_k": 60},
        "evidence": [
            {"chunk_id": "r17", "text": "Release 17 evidence.", "metadata": {
                "document_id": "TS29512-V17.6.0", "spec": "3GPP TS 29.512", "release": 17,
                "version": "17.6.0", "clause": "A.2", "pdf_page_start": 12, "official_url": REL17,
            }},
            {"chunk_id": "r19", "text": "Release 19 evidence.", "metadata": {
                "document_id": "TS29512-V19.7.0", "spec": "3GPP TS 29.512", "release": 19,
                "version": "19.7.0", "clause": "A.2", "official_url": REL19,
            }},
        ],
    }


@pytest.fixture
def conversation(monkeypatch):
    monkeypatch.setattr(chat.limiter, "enabled", False)
    monkeypatch.setattr(protocol_run, "_slots", asyncio.Semaphore(2))
    monkeypatch.setattr(protocol_run, "chroma", SimpleNamespace(client=None))
    monkeypatch.setattr(protocol_run, "open_protocol_index", lambda _: SimpleNamespace(name="fixture-index", metadata={}))
    with TestClient(app) as client:
        auth = client.post("/api/auth/guest")
        assert auth.status_code == 200
        headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}
        session = client.post("/api/sessions/", headers=headers)
        assert session.status_code == 201
        yield client, headers, session.json()["id"]


def send(conversation, question="What policy rules apply?", mode="work", **extras):
    client, headers, session_id = conversation
    response = client.post("/api/chat/stream", headers=headers, json={
        "session_id": session_id, "message": question, "mode": mode, "tool": "search", **extras,
    })
    assert response.status_code == 200
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]


def resume(conversation, request_id, *, after=0, retry=False, api_key=None):
    client, headers, _ = conversation
    response = client.post(
        f"/api/chat/protocol/{request_id}/resume", headers=headers,
        json={"after": after, "retry": retry, "api_key": api_key},
    )
    assert response.status_code == 200
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]


async def ranked_fixture(query, *, collection, step, rerank=None):
    assert collection == "fixture-index"

    async def ranking():
        return [["r17", 1.0], ["r19", 0.5]]

    for stage in ("dense", "bm25", "rrf"):
        await step(stage, ranking)
    await step("rerank", rerank or ranking, remote=True)
    return result(query)


async def read_log(request_id):
    async with async_session() as session:
        return export_record(await session.get(ProtocolSearchLog, request_id))


def test_standard_answer_citations_and_export(conversation, monkeypatch):
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", ranked_fixture)

    async def generate(_, **kwargs):
        assert kwargs["require_complete"]
        prompt = kwargs["system_prompt"]
        assert "Release 17 evidence." in prompt and "Release 19 evidence." in prompt
        assert REL17 not in prompt and REL19 not in prompt
        for token in ("The policy is defined in [", "S1] and [S", "2]. [S99]", " Contact test@example.org."):
            yield token

    monkeypatch.setattr(chat.openclaw, "chat_stream", generate)
    events = send(conversation, "Compare the two versions. test@example.org")
    answer = "".join(event.get("token", "") for event in events)
    done = events[-1]
    assert done["status"] == "complete" and done["message_id"]
    assert [row["chunk_id"] for row in done["citations"]] == ["r17", "r19"]
    assert "S99" not in answer
    assert REL17 not in answer and REL19 not in answer
    assert [(row["url"], row.get("pdf_page_start")) for row in done["citations"]] == [(REL17, 12), (REL19, None)]
    client, headers, session_id = conversation
    history = client.get(f"/api/sessions/{session_id}/messages", headers=headers).json()
    assert history[-1]["content"] == answer and history[-1]["id"] == done["message_id"]
    assert history[-1]["protocol_search"] and history[-1]["citations"] == done["citations"]
    sample = client.portal.call(read_log, done["request_id"])
    assert sample["status"] == "complete" and sample["request_id"] == done["request_id"]
    assert sample["retrieval"]["context_chunk_ids"] == ["r17", "r19"]
    assert sample["retrieval"]["generation_dispatch"] == "acknowledged"
    assert sample["retrieval"]["trace"]["dense"][0]["rank"] == 1
    assert sample["citations"] == done["citations"]
    assert "test@example.org" not in json.dumps(sample)
    assert "user_id" not in sample and "session_id" not in sample
    legacy_export = client.get("/api/analytics/export", headers=headers)
    assert legacy_export.status_code == 200 and "test@example.org" not in legacy_export.text


def test_search_failure_saves_partial_trace_without_calling_generation(conversation, monkeypatch):
    async def rerank():
        raise httpx.ReadTimeout("provider outcome unknown")

    async def retrieve(query, **kwargs):
        return await ranked_fixture(query, **kwargs, rerank=rerank)

    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", retrieve)
    generation = AsyncMock()
    monkeypatch.setattr(chat.openclaw, "chat_stream", generation)
    events = send(conversation, "scope")
    assert events[-1]["status"] == "search_failed"
    assert events[-1]["error_kind"] == "unknown"
    sample = conversation[0].portal.call(read_log, events[-1]["request_id"])
    assert sample["retrieval"]["failure_stage"] == "rerank"
    assert set(sample["retrieval"]["trace"]) == {"dense", "bm25", "rrf"}
    assert sample["answer"] == "" and sample["citations"] == []
    generation.assert_not_called()


def test_embedding_billing_error_is_reported_without_retry(conversation, monkeypatch):
    attempts = 0

    async def embed():
        nonlocal attempts
        attempts += 1
        request = httpx.Request("POST", "https://fixture.invalid/embeddings")
        response = httpx.Response(400, json={"error": {"code": "Arrearage"}}, request=request)
        response.raise_for_status()

    async def retrieve(query, *, collection, step):
        await step("embedding", embed, remote=True)

    generation = AsyncMock()
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", retrieve)
    monkeypatch.setattr(chat.openclaw, "chat_stream", generation)
    done = send(conversation)[-1]
    assert (done["status"], done["stage"], done["error_kind"]) == ("search_failed", "embedding", "billing")
    assert not done["retryable"] and attempts == 1
    generation.assert_not_called()


def test_unavailable_protocol_scope_is_logged_without_generation(conversation, monkeypatch):
    selector = {"spec": "3GPP TS 29.512", "release": None, "version": "99.9.9"}
    saved_scope = {"requested": [selector], "document_ids": [], "missing": [selector]}

    async def retrieve(query, *, collection, step):
        async def resolve():
            return saved_scope
        await step("scope", resolve)
        raise ProtocolScopeUnavailable()

    generation = AsyncMock()
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", retrieve)
    monkeypatch.setattr(chat.openclaw, "chat_stream", generation)
    done = send(conversation, "Use only TS 29.512 v99.9.9.")[-1]
    assert (done["status"], done["stage"], done["error_kind"]) == ("search_failed", "scope", "scope_unavailable")
    assert not done["retryable"]
    sample = conversation[0].portal.call(read_log, done["request_id"])
    assert sample["retrieval"]["scope"] == saved_scope
    assert sample["retrieval"]["trace"] == {}
    generation.assert_not_called()


def test_interrupted_answer_and_ordinary_chat(conversation, monkeypatch):
    retrieve = AsyncMock(side_effect=ranked_fixture)
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", retrieve)

    async def generate(_, *, require_complete=False, **kwargs):
        if require_complete:
            yield "Partial answer [S1]."
            raise RuntimeError("simulated stream interruption")
        yield "Ordinary answer"

    monkeypatch.setattr(chat.openclaw, "chat_stream", generate)
    events = send(conversation)
    assert events[-1]["status"] == "generation_interrupted"
    sample = conversation[0].portal.call(read_log, events[-1]["request_id"])
    assert sample["answer"].startswith("Partial answer") and sample["status"] == "generation_interrupted"

    async def restarted(_, **kwargs):
        assert "Release 17 evidence." in kwargs["system_prompt"]
        yield "Restored answer [S1]."

    monkeypatch.setattr(chat.openclaw, "chat_stream", restarted)
    done = events[-1]
    replay = resume(conversation, done["request_id"], after=done["seq"])
    assert replay[-1]["status"] == "generation_interrupted"
    retried = resume(conversation, done["request_id"], after=done["seq"], retry=True)
    assert any(event.get("reset") for event in retried)
    assert retried[-1]["status"] == "complete" and "Partial" not in retried[-1]["answer"]
    monkeypatch.setattr(chat.openclaw, "chat_stream", generate)
    assert send(conversation, "Hello", mode="talk") == [{"token": "Ordinary answer"}, {"done": True, "message_id": ""}]
    retrieve.assert_awaited_once()


def test_rerank_429_then_timeout_resumes_with_saved_candidates(conversation, monkeypatch):
    calls = {stage: 0 for stage in ("embedding", "dense", "bm25", "rrf", "rerank")}

    async def retrieve(query, *, collection, step):
        for stage in calls:
            async def work():
                calls[stage] += 1
                if stage == "embedding":
                    return [1.0] * 1024
                if stage == "rerank" and calls[stage] == 1:
                    response = httpx.Response(429, headers={"Retry-After": "0"})
                    request = httpx.Request("POST", "https://fixture.invalid")
                    raise httpx.HTTPStatusError("limited", request=request, response=response)
                if stage == "rerank" and calls[stage] == 2:
                    raise httpx.ReadTimeout("remote outcome unknown")
                return [["r17", 1.0]]

            await step(stage, work, remote=stage in {"embedding", "rerank"})
        return result(query)

    async def gateway(_, **kwargs):
        yield "Complete [S1]."

    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", retrieve)
    monkeypatch.setattr(chat.openclaw, "chat_stream", gateway)
    request_id = str(uuid4())
    first = send(conversation, request_id=request_id)[-1]
    assert first["status"] == "search_failed" and first["retryable"]
    assert calls == {"embedding": 1, "dense": 1, "bm25": 1, "rrf": 1, "rerank": 2}
    second = resume(conversation, request_id, retry=True)[-1]
    assert second["status"] == "complete" and second["message_id"]
    assert calls == {"embedding": 1, "dense": 1, "bm25": 1, "rrf": 1, "rerank": 3}
    assert resume(conversation, request_id, after=second["seq"])[-1]["message_id"] == second["message_id"]
    assert send(conversation, request_id=request_id)[-1]["message_id"] == second["message_id"]
    client, headers, session_id = conversation
    history = client.get(f"/api/sessions/{session_id}/messages", headers=headers).json()
    assert [row["role"] for row in history] == ["user", "assistant"]


def test_stop_during_generation_is_terminal_and_releases_worker(conversation, monkeypatch):
    entered, closed = Event(), Event()
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", ranked_fixture)

    async def gateway(_, **kwargs):
        try:
            yield "partial " * 400
            entered.set()
            await asyncio.sleep(15)
        finally:
            closed.set()

    monkeypatch.setattr(chat.openclaw, "chat_stream", gateway)
    request_id = str(uuid4())
    client, headers, _ = conversation
    with ThreadPoolExecutor(max_workers=1) as executor:
        streaming = executor.submit(send, conversation, request_id=request_id)
        assert entered.wait(8)
        cancel = client.post(f"/api/chat/protocol/{request_id}/cancel", headers=headers)
        assert cancel.status_code == 200 and cancel.json()["status"] in {"cancel_requested", "canceled"}
        done = streaming.result(timeout=8)[-1]
    assert done["status"] == "canceled" and done["answer"].startswith("partial ") and closed.is_set()
    run = client.portal.call(protocol_run_store.read_run, request_id)
    assert run.lease is None and request_id not in protocol_run._workers
    assert resume(conversation, request_id, retry=True)[-1]["status"] == "canceled"


def test_expired_worker_does_not_retry_generation_without_user_action(conversation, monkeypatch):
    retrieve = AsyncMock(side_effect=ranked_fixture)
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", retrieve)

    async def interrupted(_, **kwargs):
        yield "First attempt."
        raise httpx.ReadTimeout("interrupted")

    monkeypatch.setattr(chat.openclaw, "chat_stream", interrupted)
    done = send(conversation)[-1]
    request_id = done["request_id"]

    async def simulate_abandoned_lease():
        async with async_session() as db:
            run = await db.get(ProtocolRun, request_id)
            run.status, run.in_flight, run.lease = "running", True, str(uuid4())
            run.lease_until = utcnow() - timedelta(seconds=1)
            await db.commit()

    client, _, _ = conversation
    client.portal.call(simulate_abandoned_lease)
    calls = 0

    async def finish(_, **kwargs):
        nonlocal calls
        calls += 1
        yield "Recovered [S1]."

    monkeypatch.setattr(chat.openclaw, "chat_stream", finish)
    observed = resume(conversation, request_id)[-1]
    assert (observed["status"], observed["error_kind"], calls) == ("generation_interrupted", "unknown", 0)
    client.portal.call(simulate_abandoned_lease)
    recovered = resume(conversation, request_id, retry=True)
    assert any(event.get("reset") for event in recovered)
    assert recovered[-1]["answer"] == "Recovered 〔S1〕."
    assert calls == 1 and retrieve.await_count == 1


def test_finalization_failure_recovers_in_the_original_stream(conversation, monkeypatch):
    retrieve = AsyncMock(side_effect=ranked_fixture)
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", retrieve)
    monkeypatch.setattr(protocol_run_store, "LEASE_TIME", timedelta(seconds=1))
    actual_finalize = protocol_run_store.finalize
    actual_stream = protocol_run.stream_protocol_request
    failed = False
    calls = 0

    async def finalize(run, status, *args, **kwargs):
        nonlocal failed
        if status == "complete" and not failed:
            failed = True
            raise OSError("temporary database write failure")
        return await actual_finalize(run, status, *args, **kwargs)

    async def generate(_, **kwargs):
        nonlocal calls
        calls += 1
        yield "Saved answer [S1]."

    async def bounded_stream(*args):
        async with aclosing(actual_stream(*args)) as stream:
            while True:
                try:
                    event = await asyncio.wait_for(anext(stream), timeout=5)
                except StopAsyncIteration:
                    return
                yield event

    monkeypatch.setattr(protocol_run_store, "finalize", finalize)
    monkeypatch.setattr(chat, "stream_protocol_request", bounded_stream)
    monkeypatch.setattr(chat.openclaw, "chat_stream", generate)
    events = send(conversation)
    assert failed and events[-1]["status"] == "complete" and calls == 1
    assert events[-1]["answer"] == "Saved answer 〔S1〕."
    retrieve.assert_awaited_once()
    client, headers, session_id = conversation
    history = client.get(f"/api/sessions/{session_id}/messages", headers=headers).json()
    assert [message["role"] for message in history] == ["user", "assistant"]


@pytest.mark.parametrize("in_flight", [False, True])
def test_expired_custom_model_can_resume_after_key_is_restored(conversation, monkeypatch, in_flight):
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", ranked_fixture)
    keys = []

    async def generate(_, *, api_key, **kwargs):
        keys.append(api_key)
        if len(keys) == 1:
            raise httpx.ReadTimeout("gateway outcome unknown")
        yield "Restored [S1]."

    monkeypatch.setattr(chat.openclaw, "chat_stream", generate)
    initial = send(conversation, model="custom", api_base_url="https://fixture.invalid/v1", api_key="initial-key")[-1]
    request_id = initial["request_id"]
    client, _, _ = conversation
    audit = client.portal.call(read_log, request_id)["retrieval"]
    assert audit["generation_dispatch"] == "dispatch_unknown"
    assert audit["prepared_context_chunk_ids"] == ["r17", "r19"]
    assert audit["context_chunk_ids"] == []

    async def expire_lease():
        async with async_session() as db:
            run = await db.get(ProtocolRun, request_id)
            run.status, run.in_flight, run.lease = "running", in_flight, str(uuid4())
            run.lease_until = utcnow() - timedelta(seconds=1)
            await db.commit()

    client.portal.call(expire_lease)
    blocked = resume(conversation, request_id, retry=True)[-1]
    assert blocked["error_kind"] == "credential" and blocked["retryable"]
    assert keys == ["initial-key"]
    resumed = resume(conversation, request_id, retry=True, api_key="replacement-key")[-1]
    assert resumed["status"] == "complete"
    assert keys == ["initial-key", "replacement-key"]


def test_cancel_after_prompt_preparation_does_not_record_sent_evidence(conversation, monkeypatch):
    prompt_saved = Event()
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", ranked_fixture)
    generate = AsyncMock()
    monkeypatch.setattr(chat.openclaw, "chat_stream", generate)
    actual_save = protocol_run_store.save_checkpoint

    async def save(run, stage, *args):
        await actual_save(run, stage, *args)
        if stage == "prompt":
            prompt_saved.set()
            await asyncio.sleep(20)

    monkeypatch.setattr(protocol_run_store, "save_checkpoint", save)
    request_id = str(uuid4())
    client, headers, _ = conversation
    with ThreadPoolExecutor(max_workers=1) as executor:
        response = executor.submit(send, conversation, request_id=request_id)
        assert prompt_saved.wait(5)
        assert client.post(f"/api/chat/protocol/{request_id}/cancel", headers=headers).is_success
        assert response.result(timeout=5)[-1]["status"] == "canceled"
    generate.assert_not_called()
    retrieval = client.portal.call(read_log, request_id)["retrieval"]
    assert retrieval["prepared_context_chunk_ids"] == ["r17", "r19"]
    assert retrieval["generation_dispatch"] == "not_started"
    assert retrieval["context_chunk_ids"] == []


def test_stop_terminates_running_attachment_extractor(conversation, monkeypatch, tmp_path):
    path = tmp_path / "attached.pdf"
    path.touch()
    marker = tmp_path / "process.pid"
    descendant_output = tmp_path / "descendant-finished"
    extractor = tmp_path / "extractor.py"
    descendant = f"import time; from pathlib import Path; time.sleep(1.2); Path({str(descendant_output)!r}).touch()"
    extractor.write_text(
        "import os, subprocess, sys, time\nfrom pathlib import Path\n"
        f"subprocess.Popen([sys.executable, '-c', {descendant!r}])\n"
        f"Path({str(marker)!r}).write_text(str(os.getpid()))\n"
        "time.sleep(30)\n", encoding="utf-8",
    )
    monkeypatch.setattr(protocol_attachment, "_EXTRACTOR", extractor)
    monkeypatch.setattr(protocol_attachment, "ATTACHMENT_TIMEOUT", 20)
    generate = AsyncMock()
    monkeypatch.setattr(chat.openclaw, "chat_stream", generate)
    request_id = str(uuid4())
    client, headers, session_id = conversation
    file_id = client.portal.call(insert_attachment, session_id, path)

    with ThreadPoolExecutor(max_workers=1) as executor:
        response = executor.submit(send, conversation, file_ids=[file_id], request_id=request_id)
        deadline = monotonic() + 5
        while not marker.exists() and monotonic() < deadline:
            sleep(0.03)
        assert marker.exists(), "extractor never started"
        assert client.post(f"/api/chat/protocol/{request_id}/cancel", headers=headers).is_success
        assert response.result(timeout=5)[-1]["status"] == "canceled"
    assert protocol_run._slots._value == 2
    generate.assert_not_called()
    sleep(1.3)
    assert not descendant_output.exists(), "extractor subprocess survived cancellation"


def test_attachment_text_is_bounded_and_extraction_timeout_is_recoverable(conversation, monkeypatch, tmp_path):
    client, _, session_id = conversation
    path = tmp_path / "attachment.txt"
    path.write_text("首行\n" + "x" * 12000 + "TAIL", encoding="utf-8")
    file_id = client.portal.call(insert_attachment, session_id, path)
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", ranked_fixture)
    prompts = []

    async def generate(_, *, system_prompt, **kwargs):
        prompts.append(system_prompt)
        yield "Answer [S1]."

    monkeypatch.setattr(chat.openclaw, "chat_stream", generate)
    assert send(conversation, file_ids=[file_id])[-1]["status"] == "complete"
    assert "首行" in prompts[0] and "TAIL" not in prompts[0]

    extractor = tmp_path / "timeout.py"
    extractor.write_text("import time\ntime.sleep(20)\n", encoding="utf-8")
    monkeypatch.setattr(protocol_attachment, "_EXTRACTOR", extractor)
    monkeypatch.setattr(protocol_attachment, "ATTACHMENT_TIMEOUT", 0.3)
    assert send(conversation, file_ids=[file_id])[-1]["status"] == "complete"
    assert "[附件提取超时]" in prompts[1]


def test_expired_checkpoints_keep_the_original_failure_log(conversation, monkeypatch):
    async def timeout():
        raise httpx.ReadTimeout("rerank result unknown")

    async def retrieve(query, **kwargs):
        return await ranked_fixture(query, **kwargs, rerank=timeout)

    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", retrieve)
    request_id = send(conversation)[-1]["request_id"]
    client, _, _ = conversation

    async def age_checkpoints():
        async with async_session() as db:
            run = await db.get(ProtocolRun, request_id)
            run.updated_at = utcnow() - protocol_run_store.CHECKPOINT_TTL - timedelta(seconds=1)
            await db.commit()
        await protocol_run_store.prune_checkpoints()
        assert (await protocol_run_store.read_run(request_id)).inputs == {}
        assert await protocol_run_store.read_checkpoint(request_id, "rrf") == (False, None)

    client.portal.call(age_checkpoints)
    result_after_expiry = resume(conversation, request_id, retry=True)[-1]
    assert result_after_expiry["status"] == "expired" and not result_after_expiry["retryable"]
    audit = client.portal.call(read_log, request_id)
    assert audit["status"] == "search_failed" and audit["retrieval"]["failure_stage"] == "rerank"
    assert audit["retrieval"]["parameters"]["dense_top_k"] == 50


def test_resume_and_cancel_require_ownership(conversation, monkeypatch):
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", ranked_fixture)

    async def gateway(_, **kwargs):
        yield "Answer [S1]."

    monkeypatch.setattr(chat.openclaw, "chat_stream", gateway)
    request_id = send(conversation)[-1]["request_id"]
    client, _, _ = conversation
    stranger = client.post("/api/auth/guest").json()["access_token"]
    for action in ("resume", "cancel"):
        response = client.post(
            f"/api/chat/protocol/{request_id}/{action}", headers={"Authorization": f"Bearer {stranger}"}, json={},
        )
        assert response.status_code == 404


async def insert_attachment(session_id, path):
    from app.models.session import Session

    async with async_session() as db:
        session = await db.get(Session, session_id)
        file = File(user_id=session.user_id, filename=path.name, storage_path=str(path))
        db.add(file)
        await db.commit()
        return file.id


def test_missing_attachment_completes_request(conversation, monkeypatch, tmp_path):
    client, _, session_id = conversation
    monkeypatch.setattr(protocol_run, "retrieve_protocol_evidence", ranked_fixture)

    async def gateway(_, **kwargs):
        assert "附件不可读取" in kwargs["system_prompt"]
        yield "Answer [S1]."

    monkeypatch.setattr(chat.openclaw, "chat_stream", gateway)
    file_id = client.portal.call(insert_attachment, session_id, Path(tmp_path, "missing.pdf"))
    done = send(conversation, file_ids=[file_id])[-1]
    assert done["status"] == "complete"


def test_protocol_gateway_detects_eof_after_partial_tokens(monkeypatch):
    client_class = httpx.AsyncClient
    def reply(request):
        assert request.headers["Authorization"] == f"Bearer {openclaw_client.openclaw.api_key}"
        return httpx.Response(200, content=b'data: {"choices":[{"delta":{"content":"partial"}}]}\n\n')

    transport = httpx.MockTransport(reply)
    monkeypatch.setattr(openclaw_client.httpx, "AsyncClient", lambda **kwargs: client_class(transport=transport, **kwargs))

    async def verify():
        acknowledge = AsyncMock()
        stream = openclaw_client.openclaw.chat_stream([], require_complete=True, on_accepted=acknowledge)
        assert await anext(stream) == "partial"
        acknowledge.assert_awaited_once()
        with pytest.raises(RuntimeError, match="without a completion marker"):
            await anext(stream)

    asyncio.run(verify())
