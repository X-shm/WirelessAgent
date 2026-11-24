"""Agent 编排器：组装上下文 + 工具循环 + 返回最终答案。"""
import asyncio
import json
import re
from dataclasses import dataclass, field

from app.agent.memory import memory_store
from app.agent.skills import skill_library
from app.agent.tools import build_default_registry
from app.agent.tools.registry import ToolContext, ToolRegistry
from app.agent.tools.wireless import get_wireless_spec, wireless_directory_prompt
from app.config import settings
from app.services.openclaw_client import openclaw
from app.services.model_router import ModelSpec, model_router
from app.services.wireless_tool_runner import run_tool

TOOL_CALL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)


@dataclass
class AgentResult:
    answer: str
    tool_calls: list[dict] = field(default_factory=list)


def _build_system_prompt(
    reg: ToolRegistry,
    memory_block: str,
    base_prompt: str | None = None,
    skill_directory: str = "",
    wireless_directory: str = "",
) -> str:
    parts = [base_prompt or settings.wireless_prompt]
    parts.append(
        "\n\n## 可用工具\n"
        "你可以调用以下工具获取信息或执行操作。需要调用时，输出一个 <tool_call> 块，内容是 JSON：\n"
        "<tool_call>\n{\"name\": \"工具名\", \"args\": {参数}}\n</tool_call>\n"
        "一次可输出多个 <tool_call> 块。调用后你会收到 <tool_result>，请基于结果继续，或直接给出最终回答。\n"
        "如果不需要工具，直接正常回答即可，不要输出 <tool_call>。"
    )
    parts.append("\n工具清单：\n" + reg.describe())
    if skill_directory:
        parts.append(
            "\n\n## 可用技能\n"
            + skill_directory
            + "\n需要某技能的详细指令时，调用 use_skill 工具加载其全文并遵循。"
        )
    if wireless_directory:
        parts.append(
            "\n\n## 无线工具（5G NR）\n"
            + wireless_directory
            + "\n需要调用某无线工具但不确定其参数时，先调用 use_tool 工具加载该工具的完整参数说明。"
        )
    if memory_block:
        parts.append("\n\n" + memory_block)
    return "\n".join(parts)


def _extract_tool_calls(content: str) -> list[dict]:
    calls = []
    for m in TOOL_CALL_RE.finditer(content):
        raw = m.group(1).strip()
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("name"):
            calls.append({"name": obj["name"], "args": obj.get("args") or {}})
    return calls


def _last_message(resp: dict) -> str:
    return (resp.get("choices") or [{}])[0].get("message", {}).get("content") or ""


async def _chat_with_fallback(
    messages: list[dict],
    system_prompt: str,
    user_id: str,
    candidates: list[ModelSpec],
) -> dict:
    """按候选顺序调用模型，失败自动降级到下一个；全失败抛最后一个异常。"""
    last_error: Exception | None = None
    for spec in candidates:
        try:
            return await openclaw.chat(
                messages,
                system_prompt=system_prompt,
                user_id=user_id,
                model=spec.model,
                api_base_url=spec.base_url,
                api_key=spec.api_key,
            )
        except Exception as e:  # noqa: BLE001
            last_error = e
    assert last_error is not None
    raise last_error


async def run_agent(
    user_id: str,
    session_id: str,
    messages: list[dict],
    base_system_prompt: str | None = None,
    model: str | None = None,
    api_base_url: str | None = None,
    api_key: str | None = None,
    mode: str = "talk",
    tool: str | None = None,
) -> AgentResult:
    """执行 Agent 编排循环。

    `messages` 已包含当前用户消息（含短期会话历史）。返回最终答案与工具调用轨迹。
    `base_system_prompt` 为上游（chat 路由）拼好的系统提示（模式/工具/检索/文件上下文），
    编排器在此基础上追加工具清单与长期记忆块。
    `mode`/`tool` 用于模型路由；`model`/`api_base_url`/`api_key` 为手动覆盖（优先）。
    """
    reg = build_default_registry()
    ctx = ToolContext(user_id=user_id)

    memories = await memory_store.list(user_id, settings.memory_top_k)
    memory_block = memory_store.to_prompt(memories)
    skill_directory = skill_library.directory_prompt()
    wireless_directory = wireless_directory_prompt()
    system_prompt = _build_system_prompt(reg, memory_block, base_system_prompt, skill_directory, wireless_directory)

    tool_calls: list[dict] = []
    candidates = model_router.resolve(mode, tool, model, api_base_url, api_key)

    for _ in range(settings.agent_max_tool_rounds):
        resp = await _chat_with_fallback(messages, system_prompt, session_id, candidates)
        content = _last_message(resp)
        calls = _extract_tool_calls(content)

        if not calls:
            return AgentResult(answer=content, tool_calls=tool_calls)

        for call in calls:
            name = call["name"]
            args = call.get("args", {}) or {}
            tool = reg.get(name)
            if tool is not None:
                try:
                    result = await tool.handler(args, ctx)
                except Exception as e:  # noqa: BLE001
                    result = {"error": f"工具执行失败: {e}"}
            else:
                spec = get_wireless_spec(name)
                if spec is not None:
                    try:
                        result = await asyncio.to_thread(run_tool, spec, args, settings.wireless_tool_timeout)
                    except Exception as e:  # noqa: BLE001
                        result = {"error": f"工具执行失败: {e}"}
                else:
                    result = {"error": f"未知工具 {name}"}
            tool_calls.append({"name": name, "args": args, "result": result})
            messages.append(
                {"role": "assistant", "content": f"<tool_call>\n{json.dumps(call, ensure_ascii=False)}\n</tool_call>"}
            )
            messages.append(
                {"role": "user", "content": f"<tool_result>\n{json.dumps(result, ensure_ascii=False)}\n</tool_result>"}
            )

    # 达到最大轮次仍要工具：让模型基于已有信息给出回答
    resp = await _chat_with_fallback(messages, system_prompt, session_id, candidates)
    return AgentResult(answer=_last_message(resp), tool_calls=tool_calls)
