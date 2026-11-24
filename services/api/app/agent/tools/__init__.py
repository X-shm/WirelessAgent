"""工具池：Tool 抽象 + 注册表 + 业务工具（含记忆工具）。"""
from app.agent.tools.registry import Tool, ToolContext, ToolRegistry
from app.agent.tools.builtin import register_builtin


def build_default_registry() -> ToolRegistry:
    """构建包含全部业务工具 + 记忆工具的注册表。"""
    reg = ToolRegistry()
    register_builtin(reg)
    return reg


__all__ = ["Tool", "ToolContext", "ToolRegistry", "build_default_registry"]
