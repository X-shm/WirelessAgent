"""Registry-backed MCP catalog for every public wireless-toolbox CLI."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
TOOL_NAME = re.compile(r"[a-z][a-z0-9_]*\Z")
SUPPORTED_TYPES = {"string", "integer", "number", "boolean", "enum", "float"}


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    script: Path
    inputs: dict[str, dict[str, Any]]
    subcommands: dict[str, dict[str, Any]]
    input_schema: dict[str, Any]


def _property(name: str, field: dict[str, Any]) -> dict[str, Any]:
    kind = field.get("type")
    if kind not in SUPPORTED_TYPES:
        raise ValueError(f"unsupported input type for {name}: {kind}")
    enum = field.get("enum", field.get("values"))
    if kind == "enum":
        if not isinstance(enum, list) or not enum:
            raise ValueError(f"enum input {name} has no values")
        kind = "integer" if all(isinstance(item, int) and not isinstance(item, bool) for item in enum) else "string"
    elif kind == "float":
        kind = "number"
    prop: dict[str, Any] = {"type": kind}
    if field.get("description"):
        prop["description"] = field["description"]
    if enum is not None:
        prop["enum"] = enum
    if "default" in field:
        prop["default"] = field["default"]
    if kind == "string":
        prop["maxLength"] = 16_000
    return prop


def _input_schema(
    name: str, inputs: dict[str, dict[str, Any]], subcommands: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    properties = {field_name: _property(field_name, field) for field_name, field in inputs.items()}
    required = [field_name for field_name, field in inputs.items() if field.get("required")]
    schema: dict[str, Any] = {"type": "object", "properties": properties, "additionalProperties": False}

    # Bluetooth schemas mark --input required, while their CLIs accept exactly
    # one of --input and --input_file.
    if "input" in inputs and "input_file" in inputs:
        required = [item for item in required if item != "input"]
        schema.setdefault("allOf", []).append({"oneOf": [{"required": ["input"]}, {"required": ["input_file"]}]})
    if name == "awgn":
        schema.setdefault("allOf", []).append(
            {"oneOf": [{"required": ["signal"]}, {"required": ["signal_file"]}]}
        )
    for first, second in (("state", "state_file"), ("grid", "grid_file"), ("waveform", "waveform_file")):
        if first in inputs and second in inputs:
            schema.setdefault("allOf", []).append({"not": {"required": [first, second]}})

    if subcommands:
        properties["command"] = {
            "type": "string",
            "enum": list(subcommands),
            "description": "CLI 位置子命令；决定本次调用使用的子操作。",
        }
        required.append("command")
        for definition in subcommands.values():
            command_inputs = definition.get("inputs", {})
            for field_name, field in command_inputs.items():
                prop = _property(field_name, field)
                if field_name in properties:
                    if properties[field_name]["type"] != prop["type"]:
                        raise ValueError(f"conflicting {name}.{field_name} types")
                else:
                    properties[field_name] = prop
        command_schemas: list[dict[str, Any]] = []
        for command, definition in subcommands.items():
            command_inputs = definition.get("inputs", {})
            allowed = set(inputs) | set(command_inputs) | {"command"}
            variant: dict[str, Any] = {
                "properties": {"command": {"const": command}},
                "required": [key for key, field in command_inputs.items() if field.get("required")],
            }
            disallowed = [key for key in properties if key not in allowed]
            if disallowed:
                variant["not"] = {"anyOf": [{"required": [key]} for key in disallowed]}
            command_schemas.append(variant)
        schema.setdefault("allOf", []).append({"oneOf": command_schemas})
    schema["required"] = required
    return schema


def load_catalog(only: set[str] | None = None) -> dict[str, ToolSpec]:
    registry = json.loads((ROOT / "tool_registry.json").read_text(encoding="utf-8"))
    entries = registry["tools"]
    registered_names = {item["name"] for item in entries}
    if len(registered_names) != len(entries):
        raise ValueError("duplicate tool name in registry")
    if only is not None:
        missing = only - registered_names
        if missing:
            raise ValueError(f"unknown selected tools: {', '.join(sorted(missing))}")
    catalog: dict[str, ToolSpec] = {}
    for entry in entries:
        name = entry["name"]
        if only is not None and name not in only:
            continue
        if not TOOL_NAME.fullmatch(name):
            raise ValueError(f"invalid tool name in registry: {name}")
        expected_schema = f"tools/{name}.schema.json"
        if entry["schema"].replace("\\", "/") != expected_schema:
            raise ValueError(f"unexpected registry schema for {name}")
        schema = json.loads((ROOT / expected_schema).read_text(encoding="utf-8"))
        if schema["name"] != name or schema["script"] != f"{name}.py":
            raise ValueError(f"unexpected tool contract for {name}")
        script = TOOLS_DIR / f"{name}.py"
        if not script.is_file():
            raise FileNotFoundError(script)
        inputs = schema.get("inputs", {})
        subcommands = schema.get("subcommands", {})
        if not isinstance(inputs, dict) or not isinstance(subcommands, dict):
            raise ValueError(f"invalid inputs or subcommands for {name}")
        catalog[name] = ToolSpec(
            name=name,
            description=schema["description"],
            script=script,
            inputs=inputs,
            subcommands=subcommands,
            input_schema=_input_schema(name, inputs, subcommands),
        )
    return catalog
