"""Deterministic scoring of MCP routing, arguments and tool output."""

from __future__ import annotations

import json
import math
from copy import deepcopy
from typing import Any


def equivalent(actual: Any, expected: Any) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isclose(float(actual), float(expected), rel_tol=1e-7, abs_tol=1e-9)
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            equivalent(actual[key], expected[key]) for key in expected
        )
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(
            equivalent(a, b) for a, b in zip(actual, expected)
        )
    return actual == expected


def parse_answer(text: str) -> Any:
    raw = (text or "").strip()
    if "<answer>" in raw.lower():
        start = raw.lower().rfind("<answer>") + len("<answer>")
        end = raw.lower().find("</answer>", start)
        raw = raw[start:end if end >= 0 else None].strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if len(lines) >= 3:
            raw = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def grounded_subset(answer: Any, result: Any) -> bool:
    """Accept a faithful excerpt so long tool outputs need not be recopied."""
    if isinstance(answer, dict) and isinstance(result, dict):
        return all(
            key in result and grounded_subset(value, result[key])
            for key, value in answer.items()
        )
    if isinstance(answer, list) and isinstance(result, list):
        return len(answer) <= len(result) and all(
            grounded_subset(value, reference)
            for value, reference in zip(answer, result)
        )
    return equivalent(answer, result)


def has_substantive_field(answer: Any, path: tuple[str, ...] = ()) -> bool:
    excluded = {"ok", "tool", "metadata", "warnings", "artifacts", "state", "session_id"}
    if isinstance(answer, dict):
        return any(
            has_substantive_field(value, (*path, key))
            for key, value in answer.items() if key not in excluded
        )
    if isinstance(answer, list):
        return bool(answer) and any(has_substantive_field(value, path) for value in answer)
    return bool(path) and answer is not None


_MISSING = object()


def json_pointer(value: Any, pointer: str) -> Any:
    """Read a JSON Pointer; return a sentinel when the path is absent."""
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        return _MISSING
    current = value
    for raw_segment in pointer[1:].split("/"):
        if "~" in raw_segment and any(
            raw_segment[index + 1:index + 2] not in {"0", "1"}
            for index, char in enumerate(raw_segment) if char == "~"
        ):
            return _MISSING
        segment = raw_segment.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            current = current.get(segment, _MISSING)
        elif isinstance(current, list) and segment.isdigit() and (segment == "0" or not segment.startswith("0")):
            index = int(segment)
            current = current[index] if index < len(current) else _MISSING
        else:
            return _MISSING
        if current is _MISSING:
            return _MISSING
    return current


def valid_answer_paths(expected: Any, paths: Any) -> bool:
    return (
        isinstance(paths, list) and bool(paths)
        and all(
            isinstance(path, str)
            and (value := json_pointer(expected, path)) is not _MISSING
            and value is not None and value != {} and value != []
            for path in paths
        )
        and len(set(paths)) == len(paths)
    )


def workflow_arguments(step: dict[str, Any], prior_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Resolve declared links from earlier MCP results into this step's arguments."""
    arguments = deepcopy(step["arguments"])
    for binding in step.get("bindings", []):
        source = binding["from_step"]
        if not isinstance(source, int) or isinstance(source, bool) or source < 0 or source >= len(prior_results):
            raise ValueError("workflow binding must reference an earlier step")
        value = json_pointer(prior_results[source], binding["path"])
        if value is _MISSING or value is None:
            raise ValueError("workflow binding source path is missing")
        if binding.get("format", "identity") == "string":
            if isinstance(value, (dict, list, bool)):
                raise ValueError("workflow string binding requires a scalar value")
            value = str(value)
        elif binding.get("format") == "json":
            value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        elif binding.get("format") == "csv":
            if not isinstance(value, list) or not value or any(
                not isinstance(part, (str, int, float)) or isinstance(part, bool)
                for part in value
            ):
                raise ValueError("workflow csv binding requires a non-empty scalar list")
            value = ",".join(str(part) for part in value)
        elif binding.get("format", "identity") != "identity":
            raise ValueError("unsupported workflow binding format")
        arguments[binding["argument"]] = value
    return arguments


def grade_workflow(item: dict[str, Any], calls: list[dict[str, Any]], answer: str) -> dict[str, Any]:
    steps = item["steps"]
    route = len(calls) == len(steps) and all(
        call.get("name") == step["tool"] for call, step in zip(calls, steps)
    )
    arguments_ok = route
    if arguments_ok:
        for index, (call, step) in enumerate(zip(calls, steps)):
            if index and call.get("turn", -1) <= calls[index - 1].get("turn", -1):
                arguments_ok = False
                break
            try:
                resolved = workflow_arguments(step, [entry["result"] for entry in calls[:index]])
            except (ValueError, KeyError, TypeError):
                arguments_ok = False
                break
            if not equivalent(call.get("arguments"), resolved):
                arguments_ok = False
                break
            if any(call.get("turn", -1) <= calls[binding["from_step"]].get("turn", -1)
                   for binding in step.get("bindings", [])):
                arguments_ok = False
                break
    result_ok = arguments_ok and all(
        not call.get("is_error") and equivalent(call.get("result"), step["expected"])
        for call, step in zip(calls, steps)
    )
    parsed = parse_answer(answer)
    answer_ok = bool(result_ok and isinstance(parsed, dict) and all(
        field in parsed and (
            expected := json_pointer(calls[spec["step"]]["result"], spec["path"])
        ) is not _MISSING and equivalent(parsed[field], expected)
        for field, spec in item["answer_fields"].items()
    ) and all(
        any(
            field in call["result"] and grounded_subset(value, call["result"][field])
            for call in calls
        )
        for field, value in parsed.items() if field not in item["answer_fields"]
    ))
    signals = (route, arguments_ok, result_ok, answer_ok)
    return {
        "hard": int(all(signals)),
        "soft": sum(signals) / len(signals),
        "route_ok": bool(route),
        "arguments_ok": bool(arguments_ok),
        "result_ok": bool(result_ok),
        "answer_ok": bool(answer_ok),
    }


def grade(
    *,
    expected_tool: str,
    expected_arguments: dict[str, Any],
    expected_result: dict[str, Any],
    calls: list[dict[str, Any]],
    answer: str,
) -> dict[str, Any]:
    first = calls[0] if calls else {}
    route = first.get("name") == expected_tool
    arguments_ok = route and equivalent(first.get("arguments"), expected_arguments)
    tool_ok = arguments_ok and not first.get("is_error")
    result_ok = tool_ok and equivalent(first.get("result"), expected_result)
    parsed = parse_answer(answer)
    answer_ok = result_ok and grounded_subset(parsed, expected_result) and has_substantive_field(parsed)
    signals = (route, arguments_ok, result_ok, answer_ok)
    return {
        "hard": int(all(signals)),
        "soft": sum(signals) / len(signals),
        "route_ok": bool(route),
        "arguments_ok": bool(arguments_ok),
        "result_ok": bool(result_ok),
        "answer_ok": bool(answer_ok),
    }


def grade_case(item: dict[str, Any], calls: list[dict[str, Any]], answer: str) -> dict[str, Any]:
    """Score either an executable request or a request missing required input."""
    if item.get("kind") == "tool_workflow":
        return grade_workflow(item, calls, answer)
    if item.get("kind") == "ask_clarification":
        no_call = not calls
        terms = item["answer_terms"]
        asks_for_missing = bool(answer.strip()) and all(term.casefold() in answer.casefold() for term in terms)
        return {
            "hard": int(no_call and asks_for_missing),
            "soft": (int(no_call) + int(asks_for_missing)) / 2,
            "route_ok": no_call,
            "arguments_ok": no_call,
            "result_ok": no_call,
            "answer_ok": asks_for_missing,
        }
    scores = grade(
        expected_tool=item["tool"], expected_arguments=item["arguments"],
        expected_result=item["expected"], calls=calls, answer=answer,
    )
    if item.get("source") in {"reviewed_business", "expert_draft"}:
        parsed = parse_answer(answer)
        paths = item["answer_paths"]
        answer_ok = bool(
            scores["result_ok"] and grounded_subset(parsed, item["expected"])
            and all(json_pointer(parsed, path) is not _MISSING for path in paths)
        )
        scores["answer_ok"] = answer_ok
        signals = (scores["route_ok"], scores["arguments_ok"], scores["result_ok"], answer_ok)
        scores["hard"] = int(all(signals))
        scores["soft"] = sum(signals) / len(signals)
    return scores
