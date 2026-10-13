"""Materialize three verified, distinct-input MCP tasks for each registered tool."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from mcp.client import Client

from mcp_server.catalog import ROOT, load_catalog
from mcp_server.server import create_server
from .cases import (
    DETERMINISTIC_CASES, SPLITS, candidate_arguments, example_arguments,
    isolated_arguments, question_for,
)


def canonical_result(value: Any, data_root: Path) -> Any:
    if isinstance(value, str):
        return value.replace(str(data_root), "<DATA_ROOT>").replace(str(data_root).replace("\\", "/"), "<DATA_ROOT>")
    if isinstance(value, list):
        return [canonical_result(item, data_root) for item in value]
    if isinstance(value, dict):
        return {
            key: "<SESSION_ID>" if key == "session_id" else canonical_result(item, data_root)
            for key, item in value.items()
        }
    return value


def _fingerprint() -> str:
    return hashlib.sha256((ROOT / "tool_registry.json").read_bytes()).hexdigest()


async def build(output: Path, *, max_attempts: int = 100) -> dict[str, Any]:
    catalog = load_catalog()
    registry = json.loads((ROOT / "tool_registry.json").read_text(encoding="utf-8"))
    products = {entry["name"]: entry["product"] for entry in registry["tools"]}
    rows: dict[str, list[dict[str, Any]]] = {split: [] for split in SPLITS}
    gaps: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="wireless-skillopt-fixtures-") as temp:
        data_root = Path(temp)
        async with Client(create_server(data_root=data_root), read_timeout_seconds=45) as client:
            names = {tool.name for tool in (await client.list_tools()).tools}
            if names != set(catalog):
                raise RuntimeError("MCP tools/list differs from tool_registry.json")
            for spec in catalog.values():
                base = example_arguments(spec)
                variants = list(candidate_arguments(spec, base))[:max_attempts]
                candidates = variants if spec.name in DETERMINISTIC_CASES else [base, *variants]
                accepted: list[dict[str, Any]] = []
                attempted = 0
                seen: set[str] = set()
                for raw_arguments in candidates:
                    normalized = json.dumps(raw_arguments, ensure_ascii=False, sort_keys=True)
                    if normalized in seen:
                        continue
                    seen.add(normalized)
                    attempted += 1
                    split = SPLITS[len(accepted)]
                    case_id = f"{spec.name}_{split}"
                    arguments = isolated_arguments(raw_arguments, case_id)
                    result = await client.call_tool(spec.name, arguments)
                    if result.is_error or not isinstance(result.structured_content, dict):
                        continue
                    accepted.append({
                        "id": case_id,
                        "tool": spec.name,
                        "task_type": products[spec.name],
                        "question": question_for(spec, arguments, split),
                        "arguments": arguments,
                        "expected": canonical_result(result.structured_content, data_root),
                        "source": (
                            "deterministic_subcommand" if spec.name in DETERMINISTIC_CASES
                            else "schema_example" if raw_arguments == base else "verified_mutation"
                        ),
                    })
                    if len(accepted) == 3:
                        break
                for split, item in zip(SPLITS, accepted):
                    rows[split].append(item)
                if len(accepted) != 3:
                    gaps[spec.name] = f"{len(accepted)}/3 verified cases after {attempted} attempts"
    output.mkdir(parents=True, exist_ok=True)
    for split, items in rows.items():
        folder = output / split
        folder.mkdir(exist_ok=True)
        (folder / "items.json").write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    report = {
        "registry_sha256": _fingerprint(),
        "registered_tools": len(catalog),
        "cases_by_split": {name: len(items) for name, items in rows.items()},
        "gaps": gaps,
        "complete": not gaps and all(len(items) == len(catalog) for items in rows.values()),
    }
    (output / "manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "skillopt_data" / "splits")
    parser.add_argument("--max-attempts", type=int, default=100)
    args = parser.parse_args()
    report = asyncio.run(build(args.output, max_attempts=args.max_attempts))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["complete"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
