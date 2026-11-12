"""Tool 抽象与注册表。"""
import json
from dataclasses import dataclass
from typing import Awaitable, Callable

# 工具 handler 签名：async def handler(args: dict, ctx: ToolContext) -> dict
ToolHandler = Callable[[dict, "ToolContext"], Awaitable[dict]]


@dataclass
class ToolContext:
    """工具执行上下文（不含 DB 会话，工具内部自行开会话）。"""

    user_id: str


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict  # JSON Schema (object)
    handler: ToolHandler


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def schemas(self) -> list[dict]:
        """OpenAI function-calling 风格的 schema 列表（预留，暂未启用）。"""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    def describe(self) -> str:
        """生成给 LLM 看的工具清单文本（文本协议用）。"""
        lines = []
        for t in self._tools.values():
            params = json.dumps(t.parameters, ensure_ascii=False)
            lines.append(f"- {t.name}: {t.description}\n  参数 schema: {params}")
        return "\n".join(lines)
