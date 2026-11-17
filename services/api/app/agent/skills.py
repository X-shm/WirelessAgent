"""Skills 库：扫描 SKILL.md → 解析 frontmatter → 提供目录注入与按需加载全文。

纯提示词技能层，不绑定外部工具执行。与 tools 池解耦：技能是「何时/如何做」的领域指令，
工具是「可调用的函数」。LLM 需要某技能详细指令时，通过 use_skill 工具按名加载全文。
"""
import re
from dataclasses import dataclass
from pathlib import Path

from app.config import settings


@dataclass
class Skill:
    name: str
    description: str
    body: str
    user_invocable: bool = True


def _parse_skill_md(text: str) -> tuple[dict, str]:
    """解析 SKILL.md 的 frontmatter（轻量 YAML 子集），返回 (meta, body)。

    支持 `key: value` 与 `description: |` 块标量（缩进续行）。不依赖 pyyaml。
    """
    meta: dict = {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return meta, text.strip()

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return meta, text.strip()

    front = lines[1:end]
    body = "\n".join(lines[end + 1:]).strip()

    current_key: str | None = None
    current_val: list[str] = []

    def flush() -> None:
        nonlocal current_key, current_val
        if current_key is not None:
            meta[current_key] = "\n".join(current_val).strip()
        current_key = None
        current_val = []

    for line in front:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            flush()
            current_key = m.group(1)
            val = m.group(2)
            current_val = [] if val in {"", "|", ">"} else [val]
        else:
            if current_key is not None:
                current_val.append(line.strip())

    flush()
    return meta, body


class SkillLibrary:
    """技能库：惰性扫描多个目录下的 */SKILL.md。"""

    def __init__(self, dirs: list[str] | None = None) -> None:
        self._dirs = dirs  # None 表示用默认 settings.agent_skills_dir
        self._skills: dict[str, Skill] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        dirs = self._dirs if self._dirs is not None else [settings.agent_skills_dir]
        for d in dirs:
            self._load_dir(Path(d))

    def _load_dir(self, root: Path) -> None:
        if not root.exists():
            return
        for md in root.rglob("SKILL.md"):
            try:
                text = md.read_text(encoding="utf-8", errors="ignore")
                meta, body = _parse_skill_md(text)
                name = (meta.get("name") or "").strip() or md.parent.name
                description = (meta.get("description") or "").strip()
                user_invocable = str(meta.get("user-invocable", "true")).strip().lower() not in {"false", "0", "no"}
                self._skills[name] = Skill(
                    name=name,
                    description=description,
                    body=body,
                    user_invocable=user_invocable,
                )
            except Exception:  # noqa: BLE001 单个文件解析失败不应中断整体
                continue

    def list(self) -> list[Skill]:
        self._ensure_loaded()
        return list(self._skills.values())

    def get(self, name: str) -> Skill | None:
        self._ensure_loaded()
        return self._skills.get(name)

    def names(self) -> list[str]:
        self._ensure_loaded()
        return list(self._skills.keys())

    def directory_prompt(self) -> str:
        """生成给 LLM 看的技能目录文本（仅名称 + 描述摘要）。"""
        self._ensure_loaded()
        if not self._skills:
            return ""
        lines = ["可用技能："]
        for s in self._skills.values():
            desc = " ".join(s.description.split())
            lines.append(f"- {s.name}: {desc}")
        return "\n".join(lines)

    @staticmethod
    def body_prompt(skill: Skill) -> str:
        """技能全文注入文本。"""
        parts = [f"## 技能：{skill.name}"]
        if skill.description:
            parts.append(f"（{skill.description.strip()}）")
        parts.append("")
        parts.append(skill.body)
        return "\n".join(parts)


# 单例（与 memory_store 同款模式）
skill_library = SkillLibrary()
