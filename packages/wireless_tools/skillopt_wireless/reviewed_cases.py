"""Validate human-reviewed business cases and freeze isolated data splits."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import tempfile
from collections import Counter
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path
from typing import Any

from mcp.client import Client

from mcp_server.catalog import ROOT, load_catalog
from mcp_server.server import create_server

from .build_dataset import canonical_result
from .scoring import equivalent, json_pointer, valid_answer_paths, workflow_arguments


SPLIT_DIRS = {"train": "train", "selection": "val", "holdout": "test"}
CASE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{1,99}\Z")


def _required_text(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{row.get('id', '<unknown>')}: {key} must be non-empty text")
    return value.strip()


def _load_rows(input_path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, raw in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_no}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"line {line_no}: each line must be a JSON object")
        rows.append(row)
    if not rows:
        raise ValueError("input JSONL has no cases")
    return rows


def _validate_rows(rows: list[dict[str, Any]], *, draft: bool = False) -> list[dict[str, Any]]:
    catalog = load_catalog()
    registry = json.loads((ROOT / "tool_registry.json").read_text(encoding="utf-8"))
    products = {entry["name"]: entry["product"] for entry in registry["tools"]}
    seen_ids: set[str] = set()
    scenario_splits: dict[str, str] = {}
    question_splits: dict[str, str] = {}
    normalized = []
    for row in rows:
        task_id = _required_text(row, "id")
        if not CASE_ID.fullmatch(task_id) or task_id in seen_ids:
            raise ValueError(f"invalid or duplicate case id: {task_id}")
        seen_ids.add(task_id)
        split = _required_text(row, "split")
        if split not in SPLIT_DIRS:
            raise ValueError(f"{task_id}: split must be train, selection, or holdout")
        scenario_id = _required_text(row, "scenario_id")
        if not CASE_ID.fullmatch(scenario_id):
            raise ValueError(f"{task_id}: invalid scenario_id")
        prior_split = scenario_splits.setdefault(scenario_id, split)
        if prior_split != split:
            raise ValueError(f"{task_id}: scenario_id appears in both {prior_split} and {split}")
        question = _required_text(row, "question")
        fingerprint = hashlib.sha256(" ".join(question.split()).casefold().encode("utf-8")).hexdigest()
        if fingerprint in question_splits:
            raise ValueError(f"{task_id}: duplicate question; first seen in {question_splits[fingerprint]}")
        question_splits[fingerprint] = split
        _required_text(row, "source_ref")
        _required_text(row, "reviewer")
        expected_status = "draft" if draft else "approved"
        if row.get("review_status") != expected_status:
            raise ValueError(f"{task_id}: review_status must be {expected_status}")
        origin_type = row.get("origin_type")
        if origin_type not in {"user_query", "expert_authored", "public_example"}:
            raise ValueError(f"{task_id}: origin_type must be user_query, expert_authored, or public_example")
        if draft and origin_type != "expert_authored":
            raise ValueError(f"{task_id}: draft experiment only accepts expert_authored cases")
        kind = row.get("kind", "tool_call")
        if kind not in {"tool_call", "tool_workflow", "ask_clarification"}:
            raise ValueError(f"{task_id}: unsupported kind {kind!r}")
        if kind == "tool_workflow":
            raw_steps = row.get("steps")
            if not isinstance(raw_steps, list) or not 2 <= len(raw_steps) <= 5 or not isinstance(raw_steps[0], dict):
                raise ValueError(f"{task_id}: tool_workflow requires 2–5 steps")
            tool = _required_text(raw_steps[0], "tool")
            if row.get("tool") not in (None, tool):
                raise ValueError(f"{task_id}: top-level tool must match the first workflow step")
        else:
            tool = _required_text(row, "tool")
        if tool not in catalog:
            raise ValueError(f"{task_id}: unknown MCP tool {tool}")
        expected_product = products[tool]
        if row.get("task_type") not in (None, expected_product):
            raise ValueError(f"{task_id}: task_type does not match registry product")
        output = {
            "id": task_id,
            "scenario_id": scenario_id,
            "split": split,
            "kind": kind,
            "tool": tool,
            "task_type": expected_product,
            "question": question,
            "source": "expert_draft" if draft else "reviewed_business",
            "origin_type": origin_type,
            "source_ref": row["source_ref"],
            "reviewer": row["reviewer"],
        }
        if kind == "tool_call":
            if not isinstance(row.get("arguments"), dict) or not isinstance(row.get("expected"), dict):
                raise ValueError(f"{task_id}: tool_call requires object arguments and expected")
            if not valid_answer_paths(row["expected"], row.get("answer_paths")):
                raise ValueError(f"{task_id}: answer_paths must be non-empty JSON Pointers into expected")
            output["arguments"] = row["arguments"]
            output["expected"] = row["expected"]
            output["answer_paths"] = row["answer_paths"]
        elif kind == "tool_workflow":
            steps = []
            for index, raw_step in enumerate(raw_steps):
                if not isinstance(raw_step, dict):
                    raise ValueError(f"{task_id}: step {index} must be an object")
                step_tool = _required_text(raw_step, "tool")
                if step_tool not in catalog:
                    raise ValueError(f"{task_id}: unknown step tool {step_tool}")
                arguments, expected = raw_step.get("arguments"), raw_step.get("expected")
                if not isinstance(arguments, dict) or not isinstance(expected, dict):
                    raise ValueError(f"{task_id}: step {index} requires arguments and expected objects")
                bindings = raw_step.get("bindings", [])
                if not isinstance(bindings, list):
                    raise ValueError(f"{task_id}: step {index} bindings must be a list")
                bound_arguments: set[str] = set()
                for binding in bindings:
                    if not isinstance(binding, dict):
                        raise ValueError(f"{task_id}: step {index} binding must be an object")
                    argument = binding.get("argument")
                    source = binding.get("from_step")
                    path = binding.get("path")
                    if (not isinstance(argument, str) or argument not in arguments or argument in bound_arguments
                            or not isinstance(source, int) or isinstance(source, bool) or source < 0 or source >= index
                            or not isinstance(path, str) or not path.startswith("/")
                            or binding.get("format", "identity") not in {"identity", "string", "json", "csv"}):
                        raise ValueError(f"{task_id}: invalid binding in step {index}")
                    bound_arguments.add(argument)
                step = {"tool": step_tool, "arguments": arguments, "expected": expected, "bindings": bindings}
                try:
                    resolved = workflow_arguments(step, [prior["expected"] for prior in steps])
                except (ValueError, KeyError, TypeError) as exc:
                    raise ValueError(f"{task_id}: invalid binding in step {index}: {exc}") from exc
                if not equivalent(resolved, arguments):
                    raise ValueError(f"{task_id}: step {index} arguments disagree with prior result binding")
                steps.append(step)
            answer_fields = row.get("answer_fields")
            if not isinstance(answer_fields, dict) or not answer_fields:
                raise ValueError(f"{task_id}: tool_workflow requires answer_fields")
            for field, spec in answer_fields.items():
                if (not isinstance(field, str) or not field.strip() or not isinstance(spec, dict)
                        or not isinstance(spec.get("step"), int) or isinstance(spec.get("step"), bool)
                        or not 0 <= spec["step"] < len(steps)
                        or not isinstance(spec.get("path"), str) or not spec["path"].startswith("/")):
                    raise ValueError(f"{task_id}: invalid answer field {field!r}")
                value = json_pointer(steps[spec["step"]]["expected"], spec["path"])
                if value is None or value == {} or value == [] or not valid_answer_paths(
                    steps[spec["step"]]["expected"], [spec["path"]]
                ):
                    raise ValueError(f"{task_id}: answer field {field!r} is absent from its step result")
            if row.get("arguments") is not None or row.get("expected") is not None:
                raise ValueError(f"{task_id}: tool_workflow uses per-step arguments and expected results")
            output["steps"] = steps
            output["answer_fields"] = answer_fields
        else:
            if row.get("arguments") not in (None, {}) or row.get("expected") is not None:
                raise ValueError(f"{task_id}: clarification must not contain a tool result")
            terms = row.get("answer_terms")
            if not isinstance(terms, list) or not terms or any(
                not isinstance(term, str) or not term.strip() for term in terms
            ):
                raise ValueError(f"{task_id}: clarification requires non-empty answer_terms")
            output["answer_terms"] = [term.strip() for term in terms]
            output["arguments"] = {}
            output["expected"] = None
        normalized.append(output)
    for split in SPLIT_DIRS:
        if not any(row["split"] == split for row in normalized):
            raise ValueError(f"reviewed dataset requires at least one {split} case")
    return normalized


def cross_split_near_duplicates(rows: list[dict[str, Any]], *, threshold: float = 0.85) -> list[dict[str, Any]]:
    """Find high-overlap question templates routed through the same tool sequence."""
    def route(row: dict[str, Any]) -> tuple[str, ...]:
        return tuple(step["tool"] for step in row["steps"]) if row["kind"] == "tool_workflow" else (row["tool"],)

    def template(question: str) -> str:
        return re.sub(r"\s+", "", re.sub(r"[-+]?\d+(?:\.\d+)?", "#", question.casefold()))

    findings = []
    for left, right in combinations(rows, 2):
        if left["split"] == right["split"] or route(left) != route(right):
            continue
        similarity = SequenceMatcher(None, template(left["question"]), template(right["question"]), autojunk=False).ratio()
        if similarity >= threshold:
            findings.append({"left": left["id"], "right": right["id"], "similarity": round(similarity, 3)})
    return findings


async def _verify_mcp(rows: list[dict[str, Any]], data_root: Path) -> None:
    failure = None
    async with Client(create_server(data_root=data_root), read_timeout_seconds=45) as client:
        visible = {tool.name for tool in (await client.list_tools()).tools}
        for row in rows:
            if row["kind"] == "ask_clarification":
                continue
            task_id = row["id"]
            steps = row["steps"] if row["kind"] == "tool_workflow" else [row]
            prior_results: list[dict[str, Any]] = []
            for index, step in enumerate(steps):
                if step["tool"] not in visible:
                    failure = f"{task_id}: step {index} tool absent from MCP tools/list"
                    break
                arguments = workflow_arguments(step, prior_results) if row["kind"] == "tool_workflow" else step["arguments"]
                if not equivalent(arguments, step["arguments"]):
                    failure = f"{task_id}: step {index} arguments disagree with live binding"
                    break
                result = await client.call_tool(step["tool"], arguments)
                if result.is_error or not isinstance(result.structured_content, dict):
                    failure = f"{task_id}: step {index} reference MCP call failed"
                    break
                actual = canonical_result(result.structured_content, data_root)
                if not equivalent(actual, step["expected"]):
                    failure = f"{task_id}: step {index} expected result differs from the actual MCP result"
                    break
                prior_results.append(actual)
            if failure:
                break
    if failure:
        raise ValueError(failure)


def _freeze(input_path: Path, output_dir: Path, *, data_root: Path | None, draft: bool) -> dict[str, Any]:
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"frozen output directory is not empty: {output_dir}")
    rows = _validate_rows(_load_rows(input_path), draft=draft)
    if draft:
        overlaps = cross_split_near_duplicates(rows)
        if overlaps:
            raise ValueError(f"draft experiment has cross-split near-duplicate questions: {overlaps}")
    if data_root is None:
        with tempfile.TemporaryDirectory(prefix="wireless-reviewed-verify-") as temp:
            asyncio.run(_verify_mcp(rows, Path(temp)))
    else:
        asyncio.run(_verify_mcp(rows, data_root.resolve()))
    by_split = {split: [row for row in rows if row["split"] == split] for split in SPLIT_DIRS}
    coverage = {
        split: {
            "by_product": dict(sorted(Counter(row["task_type"] for row in cases).items())),
            "by_kind": dict(sorted(Counter(row["kind"] for row in cases).items())),
            "by_origin": dict(sorted(Counter(row["origin_type"] for row in cases).items())),
            "tool_count": len({step["tool"] for row in cases for step in
                               (row["steps"] if row["kind"] == "tool_workflow" else [row])}),
            "scenario_count": len({row["scenario_id"] for row in cases}),
            "workflow_count": sum(row["kind"] == "tool_workflow" for row in cases),
        }
        for split, cases in by_split.items()
    }
    manifest = {
        "kind": "draft_experiment" if draft else "reviewed_business",
        "publishable": not draft,
        "review_status": "draft" if draft else "approved",
        "complete": True,
        "registry_sha256": hashlib.sha256((ROOT / "tool_registry.json").read_bytes()).hexdigest(),
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "cases_by_split": {split: len(cases) for split, cases in by_split.items()},
        "coverage": coverage,
        "scenario_count": len({row["scenario_id"] for row in rows}),
        "max_workflow_steps": max((len(row["steps"]) for row in rows if row["kind"] == "tool_workflow"), default=0),
        "holdout_frozen": True,
        "split_sha256": {
            SPLIT_DIRS[split]: hashlib.sha256(
                json.dumps(cases, ensure_ascii=False, indent=2).encode("utf-8")
            ).hexdigest()
            for split, cases in by_split.items()
        },
        "note": (
            "Expert-authored draft for non-publishable local experiments; no product or user-data approval."
            if draft else
            "Questions have human approval and local MCP verification; permission and de-identification remain the provider's responsibility."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for split, cases in by_split.items():
        folder = output_dir / SPLIT_DIRS[split]
        folder.mkdir()
        (folder / "items.json").write_bytes(
            json.dumps(cases, ensure_ascii=False, indent=2).encode("utf-8")
        )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def freeze(input_path: Path, output_dir: Path, *, data_root: Path | None = None) -> dict[str, Any]:
    """Freeze an approved JSONL file after validation and real local MCP calls."""
    return _freeze(input_path, output_dir, data_root=data_root, draft=False)


def freeze_draft(input_path: Path, output_dir: Path, *, data_root: Path | None = None) -> dict[str, Any]:
    """Freeze draft expert cases for an explicitly non-publishable experiment."""
    return _freeze(input_path, output_dir, data_root=data_root, draft=True)
