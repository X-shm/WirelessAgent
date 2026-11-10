"""Agent 编排器：组装上下文 + 工具循环 + 返回最终答案。"""
import json
import re
from dataclasses import dataclass, field

from app.agent.memory import memory_store
from app.agent.tools import build_default_registry
from app.agent.tools.registry import ToolContext, ToolRegistry
from app.config import settings
from app.services.openclaw_client import openclaw

TOOL_CALL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)


@dataclass
class AgentResult:
    answer: str
    tool_calls: list[dict] = field(default_factory=list)


def _build_system_prompt(reg: ToolRegistry, memory_block: str, base_prompt: str | None = None) -> str:
    parts = [base_prompt or settings.wireless_prompt]
    parts.append(
        "\n\n## 可用工具\n"
        "你可以调用以下工具获取信息或执行操作。需要调用时，输出一个 <tool_call> 块，内容是 JSON：\n"
        "<tool_call>\n{\"name\": \"工具名\", \"args\": {参数}}\n</tool_call>\n"
        "一次可输出多个 <tool_call> 块。调用后你会收到 <tool_result>，请基于结果继续，或直接给出最终回答。\n"
        "如果不需要工具，直接正常回答即可，不要输出 <tool_call>。"
    )
    parts.append("\n工具清单：\n" + reg.describe())
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


async def run_agent(
    user_id: str,
    session_id: str,
    messages: list[dict],
    base_system_prompt: str | None = None,
    model: str | None = None,
    api_base_url: str | None = None,
    api_key: str | None = None,
) -> AgentResult:
    """执行 Agent 编排循环。

    `messages` 已包含当前用户消息（含短期会话历史）。返回最终答案与工具调用轨迹。
    `base_system_prompt` 为上游（chat 路由）拼好的系统提示（模式/工具/检索/文件上下文），
    编排器在此基础上追加工具清单与长期记忆块。
    """
    reg = build_default_registry()
    ctx = ToolContext(user_id=user_id)

    memories = await memory_store.list(user_id, settings.memory_top_k)
    memory_block = memory_store.to_prompt(memories)
    system_prompt = _build_system_prompt(reg, memory_block, base_system_prompt)

    tool_calls: list[dict] = []
    call_kwargs = {"model": model, "api_base_url": api_base_url, "api_key": api_key}

    for _ in range(settings.agent_max_tool_rounds):
        resp = await openclaw.chat(messages, system_prompt=system_prompt, user_id=session_id, **call_kwargs)
        content = _last_message(resp)
        calls = _extract_tool_calls(content)

        if not calls:
            return AgentResult(answer=content, tool_calls=tool_calls)

        for call in calls:
            name = call["name"]
            args = call.get("args", {}) or {}
            tool = reg.get(name)
            if tool is None:
                result = {"error": f"未知工具 {name}"}
            else:
                try:
                    result = await tool.handler(args, ctx)
                except Exception as e:  # noqa: BLE001
                    result = {"error": f"工具执行失败: {e}"}
            tool_calls.append({"name": name, "args": args, "result": result})
            messages.append(
                {"role": "assistant", "content": f"<tool_call>\n{json.dumps(call, ensure_ascii=False)}\n</tool_call>"}
            )
            messages.append(
                {"role": "user", "content": f"<tool_result>\n{json.dumps(result, ensure_ascii=False)}\n</tool_result>"}
            )

    # 达到最大轮次仍要工具：让模型基于已有信息给出回答
    resp = await openclaw.chat(messages, system_prompt=system_prompt, user_id=session_id, **call_kwargs)
    return AgentResult(answer=_last_message(resp), tool_calls=tool_calls)
