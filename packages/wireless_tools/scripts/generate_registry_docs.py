"""Generate the public tool inventory from tool_registry.json.

The registry is the sole inventory authority.  This script intentionally does
not read tool implementations or schemas to describe capabilities: those
details must be recorded in the registry before documentation is refreshed.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "tool_registry.json"
TOOLS_DIR = ROOT / "tools"
VALIDATORS_DIR = ROOT / "scripts"
STATUS_ORDER = ("validated", "independent_validated", "pending_validation")


def markdown_cell(value: object) -> str:
    """Return a table-safe Markdown cell."""
    if value is None or value == "":
        return "—"
    return str(value).replace("|", r"\|").replace("\n", "<br>")


def load_registry() -> list[dict[str, object]]:
    """Load and validate the registry records needed for documentation."""
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    tools = payload.get("tools")
    if not isinstance(tools, list):
        raise ValueError("tool_registry.json must contain a tools array")

    names: set[str] = set()
    for tool in tools:
        if not isinstance(tool, dict):
            raise ValueError("Every registry entry must be an object")
        for field in ("name", "product", "status", "schema", "source_functions"):
            if field not in tool:
                raise ValueError(f"Registry entry is missing {field!r}: {tool!r}")
        name = str(tool["name"])
        if name in names:
            raise ValueError(f"Duplicate registry tool name: {name}")
        names.add(name)
        schema_path = ROOT / str(tool["schema"])
        if not schema_path.is_file():
            raise ValueError(f"{name}: registered schema is missing: {tool['schema']}")
    return tools


def ordered_products(tools: list[dict[str, object]]) -> OrderedDict[str, list[dict[str, object]]]:
    """Group tools in their registry product order, with stable name ordering."""
    products: OrderedDict[str, list[dict[str, object]]] = OrderedDict()
    for tool in tools:
        products.setdefault(str(tool["product"]), []).append(tool)
    for entries in products.values():
        entries.sort(key=lambda item: str(item["name"]))
    return products


def status_counts(tools: list[dict[str, object]]) -> Counter[str]:
    return Counter(str(tool["status"]) for tool in tools)


def status_summary(tools: list[dict[str, object]]) -> str:
    counts = status_counts(tools)
    labels = [f"`{status}`: {counts[status]}" for status in STATUS_ORDER if counts[status]]
    labels.extend(
        f"`{status}`: {count}"
        for status, count in sorted(counts.items())
        if status not in STATUS_ORDER
    )
    return "，".join(labels)


def product_summary_table(products: OrderedDict[str, list[dict[str, object]]]) -> list[str]:
    lines = ["| 产品/领域 | 工具数 | 注册状态分布 |", "|---|---:|---|"]
    for product, entries in products.items():
        lines.append(f"| {markdown_cell(product)} | {len(entries)} | {status_summary(entries)} |")
    return lines


def tool_inventory(products: OrderedDict[str, list[dict[str, object]]]) -> list[str]:
    lines: list[str] = []
    for product, entries in products.items():
        lines.extend(
            [
                f"### {product}（{len(entries)}）",
                "",
                "| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |",
                "|---|---|---|---|---|",
            ]
        )
        for tool in entries:
            source_functions = tool["source_functions"]
            source = "<br>".join(f"`{item}`" for item in source_functions) if source_functions else "—"
            schema = f"`{tool['schema']}`"
            lines.append(
                "| "
                + " | ".join(
                    (
                        f"`{tool['name']}`",
                        source,
                        f"`{tool['status']}`",
                        markdown_cell(tool.get("coverage")),
                        schema,
                    )
                )
                + " |"
            )
        lines.append("")
    return lines


def status_inventory(tools: list[dict[str, object]]) -> list[str]:
    grouped: OrderedDict[str, list[str]] = OrderedDict()
    for status in STATUS_ORDER:
        grouped[status] = []
    for tool in tools:
        grouped.setdefault(str(tool["status"]), []).append(str(tool["name"]))

    lines: list[str] = []
    for status, names in grouped.items():
        if not names:
            continue
        lines.append(f"### `{status}`（{len(names)}）")
        lines.append("")
        lines.append(", ".join(f"`{name}`" for name in sorted(names)) + "。");
        lines.append("")
    return lines


def generated_notice() -> list[str]:
    return [
        "> 此文件由 `scripts/generate_registry_docs.py` 从 `tool_registry.json` 自动生成。",
        "> 请先更新注册表，再执行 `python scripts/generate_registry_docs.py --write`；不要直接编辑本文件。",
        "",
    ]


def bluetooth_scope_note(tools: list[dict[str, object]]) -> str:
    bluetooth = [tool for tool in tools if tool["product"] == "Bluetooth Toolbox"]
    sources = {source for tool in bluetooth for source in tool["source_functions"]}
    return (
        f"Bluetooth Toolbox 当前由 `{len(bluetooth)}` 个 CLI 映射 `{len(sources)}` 个顶层 MATLAB 名称。"
        "`validated` 仅表示各工具 `coverage` 所述功能切片通过验证，"
        "不代表该名称的全部参数、对象方法、网络仿真或 MATLAB 完整行为均已实现；"
        "逐项完成状态和剩余缺口见 `bluetooth_capabilities.json`。"
    )


def build_readme(tools: list[dict[str, object]]) -> str:
    products = ordered_products(tools)
    counts = status_counts(tools)
    lines = ["# Wireless Toolbox", ""]
    lines.extend(generated_notice())
    lines.extend(
        [
            "## 项目范围",
            "",
            f"当前注册 `{len(tools)}` 个 Python CLI 工具、`{len(tools)}` 份 schema。"
            f"状态分布：{status_summary(tools)}。",
            "工具名称、产品归属、标准源函数、状态、覆盖范围和 schema 路径均以"
            " `tool_registry.json` 为唯一事实来源。",
            bluetooth_scope_note(tools),
            "",
            "## 工具概览",
            "",
            *product_summary_table(products),
            "",
            "## 使用方式",
            "",
            "所有工具均以 JSON 输出。先查看实际 CLI，再按对应 schema 提供参数：",
            "",
            "```bash",
            "python tools/nr_pdsch.py --help",
            "python tools/nr_modulation.py --mod QPSK --bits 1,1,0,1",
            "python tools/wlan_bcc.py --bits 1,1,0,1,0,0,0,1 --rate 1/2 --decode",
            "```",
            "",
            "工具的完整输入/输出契约位于 `tools/<tool>.schema.json`。"
            "位置子命令（例如 `wireless_utils` 与 `nr_dci`）由 schema 的 `subcommands` 字段描述。",
            "",
            "MCP 服务需要安装 `requirements-mcp.txt`；它从注册表公开全部工具，"
            "5G Toolbox 的 45 个新增入口通过 10 个分组工具的 `function` 参数选择。",
            "这些分组的大段 `params` JSON 在 MCP 内通过标准输入转发，"
            "避免 Windows 命令行长度限制；直接使用 CLI 时可通过 `--params -` 从标准输入读取。",
            "",
            "```bash",
            "python -m pip install -r requirements-mcp.txt",
            "python -m mcp_server --transport stdio",
            "```",
            "",
            "## 验证",
            "",
            "验证流程、契约检查范围与当前注册状态清单见 [VALIDATION.md](VALIDATION.md)。",
            "",
            "```bash",
            "python scripts/generate_registry_docs.py --check",
            "python scripts/check_contracts.py",
            "python scripts/validate_all.py",
            "```",
            "",
            "## 注册工具清单",
            "",
        ]
    )
    lines.extend(tool_inventory(products))
    lines.extend(
        [
            "## 参考",
            "",
            "- 3GPP TS 36.211 / 36.212（LTE）",
            "- 3GPP TS 38.211 / 38.212 / 38.214（5G NR）",
            "- MATLAB 5G / LTE / Communications / WLAN Toolbox",
            "",
        ]
    )
    return "\n".join(lines)


def build_main_skill(tools: list[dict[str, object]]) -> str:
    products = ordered_products(tools)
    lines = [
        "---",
        "name: wireless-toolbox",
        "description: |",
        "  注册表驱动的无线通信工具目录，覆盖 5G NR、LTE、WLAN、通用通信、无线网络和优化工作流。",
        f"  当前登记 {len(tools)} 个工具；调用前按 tool_registry.json 的状态、覆盖范围和 schema 选择。",
        "user-invocable: true",
        "---",
        "",
        "# Wireless Toolbox",
        "",
        *generated_notice(),
        "## 选择与调用规则",
        "",
        "1. 先按产品/领域选择工具，并确认其注册 `status` 和 `coverage`。",
        "2. 再读取 `schema` 指定的输入/输出契约；不要从工具名推测支持范围。",
        "3. 调用前执行 `python tools/<tool>.py --help`，特别是有位置子命令的工具。",
        "4. `pending_validation` 只表示注册表中的当前状态，不能当作标准一致性的承诺。",
        "5. " + bluetooth_scope_note(tools),
        "",
        "## 注册概览",
        "",
        *product_summary_table(products),
        "",
        "## 注册工具目录",
        "",
    ]
    lines.extend(tool_inventory(products))
    lines.extend(
        [
            "## 回归与契约检查",
            "",
            "```bash",
            "python scripts/generate_registry_docs.py --check",
            "python scripts/check_contracts.py",
            "python scripts/validate_all.py",
            "```",
            "",
            "详细说明见仓库根目录的 `VALIDATION.md`。",
            "",
        ]
    )
    return "\n".join(lines)


def build_validation_guide(tools: list[dict[str, object]]) -> str:
    products = ordered_products(tools)
    pending_tools = [tool["name"] for tool in tools if tool["status"] == "pending_validation"]
    validator_count = len(
        [
            path for path in VALIDATORS_DIR.glob("validate_*.py")
            if path.name != "validate_all.py"
        ]
    )
    lines = ["# 验证说明", ""]
    lines.extend(generated_notice())
    pending_note = (
        "其中仍为 `pending_validation` 的工具若尚未检入 MATLAB 黄金样本，"
        "其专项验证器会以 `SKIP` 状态退出；`validate_all.py` 将它与失败区分开来，"
        "且不会因此提升注册状态。当前可在具备 5G Toolbox 的 MATLAB 环境运行"
        "`matlab_oracle/gen_samples_nr_pending.m` 生成 DM-RS、CSI-RS、DCI 和 PDCCH 样本。"
        if pending_tools
        else "当前注册表没有 `pending_validation` 工具；所有已登记的 MATLAB 黄金样本验证器都会作为回归的一部分执行。"
    )
    lines.extend(
        [
            "## 事实来源与范围",
            "",
            f"`tool_registry.json` 当前登记 `{len(tools)}` 个工具，且每项均引用一份 schema。"
            f"注册状态分布：{status_summary(tools)}。",
            "本文件不把注册状态扩大解释为额外的标准符合性结论；具体覆盖边界以每项 `coverage` 字段为准。",
            "`independent_validated` 表示所声明的 Python 功能切片通过独立数值/性质检查、"
            "接口契约和调用回归；`validated` 还具有相应的 MATLAB 对照证据。"
            "两者都不表示 MATLAB 原函数的全部参数和行为已实现。",
            bluetooth_scope_note(tools),
            "",
            "## 必跑命令",
            "",
            "```bash",
            "# 文档是否仍由注册表生成",
            "python scripts/generate_registry_docs.py --check",
            "",
            "# 全部 JSON 语法和 schema 基本结构",
            "python scripts/check_json.py",
            "",
            "# 已检入 MATLAB oracle 样本的哈希和结构是否未漂移",
            "python scripts/generate_sample_manifest.py --check",
            "",
            "# 注册表、schema 名称、脚本名、CLI flag、子命令和 --help",
            "python scripts/check_contracts.py",
            "",
            "# 自动发现并运行全部 validate_*.py 回归脚本",
            "python scripts/validate_all.py",
            "",
            "# 确定性的 PDSCH 无噪端到端收发回环（4 组配置）",
            "python scripts/test_nr_pdsch_e2e.py --perfect-only",
            "",
            "# Python 语法编译检查",
            "python -m compileall -q tools scripts",
            "```",
            "",
            "MCP 端到端验证需先在所选 Python 环境安装 `requirements-mcp.txt`。"
            "第一项覆盖全部注册工具示例及 stdio/HTTP 传输，第二项逐一执行新增的 45 个 5G 入口：",
            "",
            "```bash",
            "python -m pip install -r requirements-mcp.txt",
            "python -m unittest scripts.test_mcp_server scripts.test_nr_remaining_mcp",
            "```",
            "",
            "这 10 个 5G 分组工具的 `independent_validated` 仅覆盖注册表列出的 Python 功能切片："
            "45 个映射入口均经过 MCP 调用，且具备固定数值、性质和边界回归。"
            "没有 MATLAB 对照的切片不宣称与 MATLAB 原函数等价。",
            "新增的 `matlab_oracle/gen_samples_nr_remaining.m` 可重建 BCH、UCI、UMa 路损和"
            "PUCCH 格式 1 的完整 MATLAB R2026a 对照向量；"
            "`validate_nr_remaining_oracle.py` 用检入样本执行无 MATLAB 依赖的回归。",
            "",
            "具备 MATLAB R2026a 与 Bluetooth Toolbox 时，还可核查 52 个注册名称是否在本机真实解析：",
            "",
            "```bash",
            "matlab -batch \"addpath('matlab_oracle'); verify_bluetooth_inventory\"",
            "```",
            "",
            f"`validate_all.py` 当前会自动发现 `{validator_count}` 个专项验证器；"
            "该数量由文件系统发现，不应手工写死。",
            "",
            pending_note,
            "",
            "## 契约检查内容",
            "",
            "`check_contracts.py` 以注册表和 `tools/*.schema.json` 交叉检查：",
            "",
            "- 每个注册工具都有同名 schema，且 schema 指向同名 Python 脚本；",
            "- Bluetooth Toolbox 恰好映射 52 个不同的顶层 MATLAB 名称，且每项说明覆盖边界；",
            "- schema 的输入字段与 CLI 的 `--flag` 精确一致；",
            "- schema 的 `subcommands` 与位置子命令及其 flag 一致；",
            "- 每个注册工具的 `--help` 可执行；",
            "- 由 `tool_registry.json` 生成的 README、技能文档和本验证说明未漂移；",
            "- `tools/SKILL.md` 的 frontmatter 完整。",
            "",
            "## 注册状态快照",
            "",
            *product_summary_table(products),
            "",
            "## 按注册状态列出的工具",
            "",
        ]
    )
    lines.extend(status_inventory(tools))
    lines.extend(
        [
            "## 变更流程",
            "",
            "1. 先在 `tool_registry.json` 新增或修改工具的产品、状态、覆盖范围、源函数和 schema 路径。",
            "2. 同步新增/修改 `tools/<name>.schema.json` 和实际 CLI。",
            "3. 执行 `python scripts/generate_registry_docs.py --write`。",
            "4. 依次运行文档检查、契约检查、专项验证和全量验证。",
            "",
        ]
    )
    return "\n".join(lines)


def registry_record(tool: dict[str, object]) -> list[str]:
    source_functions = tool["source_functions"]
    source = ", ".join(f"`{item}`" for item in source_functions) if source_functions else "—"
    return [
        "## 注册记录",
        "",
        f"- 工具：`{tool['name']}`",
        f"- 产品/领域：{tool['product']}",
        f"- 状态：`{tool['status']}`",
        f"- 注册源函数：{source}",
        f"- 覆盖范围：{tool.get('coverage') or '—'}",
        f"- Schema：`{tool['schema']}`",
        "",
        "## 调用",
        "",
        f"```bash\npython tools/{tool['name']}.py --help\n```",
        "",
        "参数、子命令和 JSON 输出以对应 schema 及 CLI 帮助为准。",
        "",
    ]


def build_single_tool_skill(tool: dict[str, object], skill_name: str, title: str) -> str:
    lines = [
        "---",
        f"name: {skill_name}",
        "description: |",
        f"  {tool['name']} 的注册表驱动调用说明。调用前读取 schema 并确认注册状态和覆盖范围。",
        "user-invocable: true",
        "---",
        "",
        f"# {title}",
        "",
        *generated_notice(),
    ]
    lines.extend(registry_record(tool))
    return "\n".join(lines)


def build_additional_tools_skill(index: dict[str, dict[str, object]]) -> str:
    tool_names = ("nr_crc", "wlan_bcc", "nr_ldpc_rm")
    lines = [
        "---",
        "name: nr_ldpc_bcc",
        "description: |",
        "  NR CRC、WLAN BCC 与 NR LDPC 速率匹配的注册表驱动调用说明。",
        "user-invocable: true",
        "---",
        "",
        "# Additional Wireless Tools",
        "",
        *generated_notice(),
        "## 注册工具",
        "",
        "| 工具 | 产品/领域 | 状态 | 覆盖范围 | Schema |",
        "|---|---|---|---|---|",
    ]
    for tool_name in tool_names:
        tool = index[tool_name]
        lines.append(
            f"| `{tool['name']}` | {tool['product']} | `{tool['status']}` | "
            f"{markdown_cell(tool.get('coverage'))} | `{tool['schema']}` |"
        )
    lines.extend(
        [
            "",
            "```bash",
            "python tools/nr_crc.py --help",
            "python tools/wlan_bcc.py --help",
            "python tools/nr_ldpc_rm.py --help",
            "```",
            "",
            "参数和输出以各自 schema 及 CLI 帮助为准。",
            "",
        ]
    )
    return "\n".join(lines)


def generated_documents(tools: list[dict[str, object]]) -> dict[Path, str]:
    index = {str(tool["name"]): tool for tool in tools}
    required_skill_tools = {"nr_modulation", "nr_ldpc", "nr_crc", "nr_ldpc_rm", "wlan_bcc"}
    missing = required_skill_tools - index.keys()
    if missing:
        raise ValueError(f"Registry lacks tool(s) referenced by skill docs: {sorted(missing)}")

    return {
        ROOT / "README.md": build_readme(tools),
        TOOLS_DIR / "SKILL.md": build_main_skill(tools),
        ROOT / "VALIDATION.md": build_validation_guide(tools),
        TOOLS_DIR / "SKILL_nr_modulation.md": build_single_tool_skill(
            index["nr_modulation"], "nr_modulation", "NR Modulation"
        ),
        TOOLS_DIR / "SKILL_nr_ldpc.md": build_single_tool_skill(
            index["nr_ldpc"], "nr_ldpc", "NR LDPC"
        ),
        TOOLS_DIR / "SKILL_nr_crc.md": build_single_tool_skill(
            index["nr_crc"], "nr_crc", "NR CRC"
        ),
        TOOLS_DIR / "SKILL_addl_tools.md": build_additional_tools_skill(index),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate registry-derived Markdown documentation")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write generated documentation")
    mode.add_argument("--check", action="store_true", help="fail if generated documentation is stale")
    args = parser.parse_args()

    tools = load_registry()
    documents = generated_documents(tools)
    stale = [path for path, content in documents.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]

    if args.check:
        if stale:
            for path in stale:
                print(f"STALE {path.relative_to(ROOT).as_posix()}")
            return 1
        print(f"PASS {len(documents)} registry-derived documentation files are current")
        return 0

    for path, content in documents.items():
        path.write_text(content, encoding="utf-8")
        print(f"WROTE {path.relative_to(ROOT).as_posix()}")
    print(f"Generated {len(documents)} documents from {len(tools)} registry tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
