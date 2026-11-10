"""Agent 编排层单测：工具解析 / 系统提示 / 记忆读写 / 编排循环（mock OpenClaw）。"""
import asyncio

import pytest

import app.models  # noqa: F401 确保全部模型注册进 Base.metadata
from app.agent.orchestrator import (
    _build_system_prompt,
    _extract_tool_calls,
    run_agent,
)
from app.agent.memory import memory_store
from app.agent.tools import build_default_registry
from app.database import engine
from app.models.base import Base


@pytest.fixture(scope="module", autouse=True)
def _create_tables():
    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create())
    yield


def test_extract_single_tool_call():
    content = 'x\n<tool_call>\n{"name": "rag_search", "args": {"q": "MIMO"}}\n</tool_call>\ny'
    assert _extract_tool_calls(content) == [{"name": "rag_search", "args": {"q": "MIMO"}}]


def test_extract_multiple_and_malformed():
    content = (
        '<tool_call>\n{"name":"a","args":{}}\n</tool_call>'
        '<tool_call>\n{"name":"b","args":{"x":1}}\n</tool_call>'
    )
    assert [c["name"] for c in _extract_tool_calls(content)] == ["a", "b"]

    assert _extract_tool_calls("no tool call") == []
    assert _extract_tool_calls("<tool_call>\n{not json\n</tool_call>") == []


def test_system_prompt_includes_tools_and_memory():
    sp = _build_system_prompt(build_default_registry(), "- 研究方向: 5G NR")
    assert "rag_search" in sp
    assert "save_memory" in sp
    assert "5G NR" in sp


def test_memory_store_roundtrip():
    async def _run():
        await memory_store.add("u_agent_test", "研究方向", "5G NR", importance=5)
        mems = await memory_store.list("u_agent_test", top_k=10)
        assert any(m["key"] == "研究方向" and m["content"] == "5G NR" for m in mems)
        assert memory_store.to_prompt(mems) != ""

    asyncio.run(_run())


def test_run_agent_tool_loop(monkeypatch):
    from app.services.openclaw_client import openclaw

    rounds = {"n": 0}

    async def fake_chat(messages, system_prompt=None, user_id=None, **kwargs):
        rounds["n"] += 1
        if rounds["n"] == 1:
            return {"choices": [{"message": {"content": '<tool_call>\n{"name":"project_list","args":{}}\n</tool_call>'}}]}
        return {"choices": [{"message": {"content": "你有 0 个项目。"}}]}

    monkeypatch.setattr(openclaw, "chat", fake_chat)

    async def _run():
        return await run_agent("u_agent_test", "s_agent_test", [{"role": "user", "content": "列出项目"}])

    res = asyncio.run(_run())
    assert res.answer == "你有 0 个项目。"
    assert rounds["n"] == 2
    assert len(res.tool_calls) == 1
    assert res.tool_calls[0]["name"] == "project_list"
    assert res.tool_calls[0]["result"] == {"projects": []}


def test_run_agent_unknown_tool(monkeypatch):
    from app.services.openclaw_client import openclaw

    async def fake_chat(messages, system_prompt=None, user_id=None, **kwargs):
        return {"choices": [{"message": {"content": '<tool_call>\n{"name":"nope","args":{}}\n</tool_call>'}}]}

    monkeypatch.setattr(openclaw, "chat", fake_chat)

    async def _run():
        return await run_agent("u_agent_test", "s_agent_test", [{"role": "user", "content": "x"}])

    res = asyncio.run(_run())
    assert res.tool_calls, "应该记录了工具调用轨迹"
    assert res.tool_calls[0]["result"] == {"error": "未知工具 nope"}
