"""无线工具池：5G NR 工具目录 + use_tool 按需加载 + 供编排器执行。"""
from __future__ import annotations

from typing import Any

from app.services.wireless_tool_runner import WirelessToolSpec, load_wireless_catalog

_pool: dict[str, WirelessToolSpec] | None = None


def _ensure_loaded() -> dict[str, WirelessToolSpec]:
    global _pool
    if _pool is None:
        _pool = load_wireless_catalog()
    return _pool


def get_wireless_spec(name: str) -> WirelessToolSpec | None:
    return _ensure_loaded().get(name)


def wireless_names() -> list[str]:
    return list(_ensure_loaded().keys())


def wireless_directory_prompt() -> str:
    """生成无线工具目录文本（name + 一句话描述，不含完整参数）。"""
    pool = _ensure_loaded()
    if not pool:
        return ""
    lines = ["可用无线工具（5G NR + 链路工作流）："]
    for spec in pool.values():
        desc = " ".join(spec.description.split())
        lines.append(f"- {spec.name}: {desc}")
    return "\n".join(lines)


async def _use_tool(args: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """按需返回某个无线工具的完整参数 schema，供 LLM 下一步 <tool_call> 调用。"""
    name = (args.get("name") or "").strip()
    if not name:
        return {"error": "缺少工具名 name"}
    spec = get_wireless_spec(name)
    if spec is None:
        return {"error": f"未知无线工具 {name}，可用：{', '.join(wireless_names())}"}
    return {
        "name": spec.name,
        "description": spec.description,
        "input_schema": spec.input_schema,
    }
