"""DeepSeek -> MCP tool calls -> SkillOpt trajectory and scores."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Protocol

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

from . import ROOT
from .build_dataset import canonical_result
from .scoring import grade_case, json_pointer


class Target(Protocol):
    def complete(
        self, messages: list[dict[str, Any]], functions: list[dict[str, Any]],
        *, required: bool, item: dict[str, Any]
    ) -> dict[str, Any]: ...


class DeepSeekTarget:
    """Non-thinking Chat Completions so first-turn tool_choice=required is valid."""

    def __init__(self) -> None:
        from openai import OpenAI

        key = os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("DEEPSEEK_API_KEY is required for live rollout")
        self.client = OpenAI(
            api_key=key, base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )
        self.model = os.environ.get("DEEPSEEK_TARGET_MODEL", "deepseek-flash")

    def complete(
        self, messages: list[dict[str, Any]], functions: list[dict[str, Any]],
        *, required: bool, item: dict[str, Any]
    ) -> dict[str, Any]:
        del item
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=functions,
            tool_choice="required" if required else "auto",
            temperature=0,
            max_tokens=4096,
            extra_body={"thinking": {"type": "disabled"}},
        )
        message = response.choices[0].message
        return {
            "content": message.content or "",
            "tool_calls": [
                call.model_dump(mode="json") for call in (message.tool_calls or [])
            ],
            "usage": response.usage.model_dump(mode="json") if response.usage else {},
        }


class MockTarget:
    """No-network target for testing the adapter and full MCP catalogue."""

    def complete(
        self, messages: list[dict[str, Any]], functions: list[dict[str, Any]],
        *, required: bool, item: dict[str, Any]
    ) -> dict[str, Any]:
        del functions
        if item.get("kind") == "tool_workflow":
            completed = sum(message.get("role") == "tool" for message in messages)
            steps = item["steps"]
            if completed < len(steps):
                step = steps[completed]
                return {
                    "content": "",
                    "tool_calls": [{"id": f"mock-call-{completed}", "type": "function", "function": {
                        "name": step["tool"],
                        "arguments": json.dumps(step["arguments"], ensure_ascii=False),
                    }}],
                    "usage": {},
                }
            answer = {
                field: json_pointer(steps[spec["step"]]["expected"], spec["path"])
                for field, spec in item["answer_fields"].items()
            }
            return {"content": "<answer>" + json.dumps(answer, ensure_ascii=False) + "</answer>",
                    "tool_calls": [], "usage": {}}
        if required or (item.get("source") in {"reviewed_business", "expert_draft"} and item.get("kind") == "tool_call" and not any(message["role"] == "tool" for message in messages)):
            return {
                "content": "",
                "tool_calls": [{
                    "id": "mock-call",
                    "type": "function",
                    "function": {
                        "name": item["tool"],
                        "arguments": json.dumps(item["arguments"], ensure_ascii=False),
                    },
                }],
                "usage": {},
            }
        if item.get("kind") == "ask_clarification":
            content = "请补充" + "、".join(item["answer_terms"]) + "。"
        else:
            content = "<answer>" + json.dumps(item["expected"], ensure_ascii=False) + "</answer>"
        return {
            "content": content,
            "tool_calls": [],
            "usage": {},
        }


def system_prompt(skill_content: str) -> str:
    return (
        "你是无线通信计算助手。以下技能正文是操作规则：\n"
        + skill_content
        + "\n本题需要工具计算。最终用 <answer> 包住 JSON 结果：从工具返回对象中"
        "准确摘录至少一个有业务含义的字段，保留原始嵌套键名；大数组可只给前几项。"
        "不要改写数值，也不要臆造字段。"
    )


def prompt_for_case(skill_content: str, item: dict[str, Any]) -> str:
    if item.get("source") not in {"reviewed_business", "expert_draft"}:
        return system_prompt(skill_content)
    return (
        "你是无线通信助手。遵循以下技能规则：\n" + skill_content +
        "\n根据用户问题判断是否具备调用工具所需参数。信息不足时先询问，"
        "不要猜测参数；具备条件时调用合适的工具。若需多个工具，先读取前一工具结果，"
        "再将其中的结果传给下一工具。调用后最终用 <answer> 包住 JSON 结果，"
        "准确摘录工具返回中至少一个有业务含义的字段，保留原始嵌套键名；"
        "大数组可只给前几项，不要改写数值或臆造字段。"
    )


async def _one(
    client: Client, functions: list[dict[str, Any]], item: dict[str, Any],
    skill_content: str, prediction_dir: Path, data_root: Path, target: Target,
    max_turns: int,
) -> dict[str, Any]:
    task_id = str(item["id"])
    system = prompt_for_case(skill_content, item)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": item["question"]},
    ]
    conversation: list[dict[str, Any]] = list(messages)
    calls: list[dict[str, Any]] = []
    answer = ""
    failure = ""
    token_usage: list[dict[str, Any]] = []
    for turn in range(max_turns):
        try:
            message = await asyncio.to_thread(
                target.complete, messages, functions,
                required=turn == 0 and item.get("source") not in {"reviewed_business", "expert_draft"}, item=item
            )
        except Exception as exc:
            failure = f"model_error: {type(exc).__name__}: {exc}"
            break
        token_usage.append(message.get("usage") or {})
        assistant = {
            "role": "assistant",
            "content": message.get("content") or "",
        }
        tool_calls = message.get("tool_calls") or []
        if tool_calls:
            assistant["tool_calls"] = tool_calls
        messages.append(assistant)
        conversation.append(assistant)
        if not tool_calls:
            answer = assistant["content"]
            break
        for tool_call in tool_calls:
            name = tool_call.get("function", {}).get("name", "")
            raw = tool_call.get("function", {}).get("arguments", "{}")
            try:
                arguments = json.loads(raw)
                if not isinstance(arguments, dict):
                    raise ValueError("tool arguments must be an object")
                result = await client.call_tool(name, arguments)
                payload = result.structured_content
                if payload is None:
                    payload = json.loads(result.content[0].text)
                normalized = canonical_result(payload, data_root)
                is_error = bool(result.is_error)
            except Exception as exc:
                arguments = {}
                normalized = {"code": "INVALID_TOOL_CALL", "message": str(exc)}
                is_error = True
            calls.append({
                "name": name, "arguments": arguments,
                "result": normalized, "is_error": is_error, "turn": turn,
            })
            observation = json.dumps(normalized, ensure_ascii=False, allow_nan=False)
            tool_message = {
                "role": "tool", "tool_call_id": tool_call.get("id", ""),
                "content": observation,
            }
            messages.append(tool_message)
            # SkillOpt's trajectory formatter reads explicit tool_call records;
            # plain Chat Completions messages hide the selected name and args.
            conversation.append({
                "type": "tool_call",
                "cmd": json.dumps({"name": name, "arguments": arguments}, ensure_ascii=False),
                "obs": observation,
            })
    else:
        failure = "exceeded tool-turn budget"
    scores = grade_case(item, calls, answer)
    if failure:
        scores["hard"] = 0
    case_dir = prediction_dir / task_id
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "conversation.json").write_text(
        json.dumps(conversation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "id": task_id,
        "hard": scores["hard"],
        "soft": scores["soft"],
        "predicted_answer": answer,
        "question": item["question"],
        "task_description": item["question"],
        "task_type": item["task_type"],
        "kind": item.get("kind", "tool_call"),
        "reference_text": json.dumps(
            {"expected_steps": [{"tool": step["tool"], "arguments": step["arguments"],
                                  "bindings": step.get("bindings", [])} for step in item["steps"]],
             "answer_fields": item["answer_fields"]}
            if item.get("kind") == "tool_workflow" else
            {"expected_tool": item["tool"], "expected_arguments": item["arguments"]},
            ensure_ascii=False,
        ),
        "fail_reason": failure or ",".join(
            key for key in ("route_ok", "arguments_ok", "result_ok", "answer_ok")
            if not scores[key]
        ),
        "tool_calls": calls,
        "token_usage": token_usage,
        "target_system_prompt": system,
        "target_user_prompt": item["question"],
        "target_model": getattr(target, "model", "mock"),
        "n_turns": len(token_usage),
        **scores,
    }


async def _batch(
    items: list[dict[str, Any]], skill_content: str, out_root: Path,
    target: Target, max_turns: int,
) -> list[dict[str, Any]]:
    out_root.mkdir(parents=True, exist_ok=True)
    # A batch may be retried in the same output directory. Isolate session and
    # artifact state so a previous rollout cannot change a subsequent result.
    # The MCP server resolves its data root to an absolute path. Keep the same
    # absolute form here so file/session paths normalize to <DATA_ROOT>.
    data_root = (out_root / "mcp-data" / uuid.uuid4().hex).resolve()
    prediction_dir = out_root / "predictions"
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server", "--data-root", str(data_root)],
        cwd=str(ROOT),
    )
    async with Client(params, read_timeout_seconds=45) as client:
        tools = (await client.list_tools()).tools
        if len(tools) != 144:
            raise RuntimeError(f"expected 144 MCP tools, found {len(tools)}")
        functions = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        } for tool in tools]
        results = []
        for item in items:
            results.append(await _one(
                client, functions, item, skill_content, prediction_dir,
                data_root, target, max_turns,
            ))
    (out_root / "rollouts.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return results


def run_batch(
    items: list[dict[str, Any]], skill_content: str, out_root: str | Path,
    *, mock: bool = False, max_turns: int = 3,
) -> list[dict[str, Any]]:
    target: Target = MockTarget() if mock else DeepSeekTarget()
    return asyncio.run(_batch(items, skill_content, Path(out_root), target, max_turns))
