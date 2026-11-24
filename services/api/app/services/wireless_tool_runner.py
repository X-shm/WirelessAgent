"""5G NR 无线工具执行器：加载 nr_* 工具目录 + subprocess 执行 CLI。

复用 packages/wireless_tools 已验证的 catalog 加载与 CLI 执行逻辑（去掉 MCP 协议层），
把 5G NR Toolbox 的 58 个 nr_* 工具暴露给编排层调用。
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import settings

# 5G Toolbox 工具名均以 nr_ 开头；链路工作流工具 product 为 WirelessAgent Workflow
NR_PREFIX = "nr_"
WORKFLOW_PRODUCT = "WirelessAgent Workflow"
# 链路仿真核心通信工具（加噪 / 误码 / 理论误码率 / SNR 换算 / Q 函数）
COMM_TOOLS = {"awgn", "biterr", "symerr", "ber_awgn", "ber_fading", "fading_channel", "convert_snr", "q_function"}
MAX_OUTPUT_BYTES = 1_000_000
SUPPORTED_TYPES = {"string", "integer", "number", "boolean", "enum", "float"}


@dataclass(frozen=True)
class WirelessToolSpec:
    name: str
    description: str
    script: Path
    inputs: dict[str, dict[str, Any]]
    subcommands: dict[str, dict[str, Any]]
    input_schema: dict[str, Any]


def _wireless_root() -> Path:
    return Path(settings.wireless_tools_dir)


def _property(name: str, field: dict[str, Any]) -> dict[str, Any]:
    """字段定义 → JSON Schema property（复用 catalog._property 逻辑）。"""
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
        max_length = field.get("max_length", 16_000)
        if type(max_length) is not int or not 1 <= max_length <= 1_000_000:
            raise ValueError(f"invalid max_length for {name}: {max_length!r}")
        prop["maxLength"] = max_length
    return prop


def _input_schema(
    name: str, inputs: dict[str, dict[str, Any]], subcommands: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """inputs + subcommands → JSON Schema（复用 catalog._input_schema 逻辑）。"""
    properties = {field_name: _property(field_name, field) for field_name, field in inputs.items()}
    required = [field_name for field_name, field in inputs.items() if field.get("required")]
    schema: dict[str, Any] = {"type": "object", "properties": properties, "additionalProperties": False}

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


def load_wireless_catalog() -> dict[str, WirelessToolSpec]:
    """加载 5G NR（nr_*）+ 链路工作流 + 通信工具目录。"""
    root = _wireless_root()
    registry = json.loads((root / "tool_registry.json").read_text(encoding="utf-8"))
    entries = [
        item for item in registry["tools"]
        if item["name"].startswith(NR_PREFIX)
        or item.get("product") == WORKFLOW_PRODUCT
        or item["name"] in COMM_TOOLS
    ]

    catalog: dict[str, WirelessToolSpec] = {}
    for entry in entries:
        name = entry["name"]
        schema = json.loads((root / f"tools/{name}.schema.json").read_text(encoding="utf-8"))
        script = root / "tools" / f"{name}.py"
        if not script.is_file():
            raise FileNotFoundError(script)
        inputs = schema.get("inputs", {})
        subcommands = schema.get("subcommands", {})
        catalog[name] = WirelessToolSpec(
            name=name,
            description=schema.get("description", ""),
            script=script,
            inputs=inputs,
            subcommands=subcommands,
            input_schema=_input_schema(name, inputs, subcommands),
        )
    return catalog


def _flags(inputs: dict[str, dict[str, Any]], arguments: dict[str, Any]) -> list[str]:
    """参数 → CLI flags（复用 server._flags 逻辑）。"""
    args: list[str] = []
    for name, field in inputs.items():
        if name not in arguments:
            continue
        value = arguments[name]
        if field["type"] == "boolean":
            if value:
                args.append(f"--{name}")
        else:
            rendered = str(value)
            if rendered.startswith("-"):
                args.append(f"--{name}={rendered}")
            else:
                args.extend((f"--{name}", rendered))
    return args


def _cli_args(spec: WirelessToolSpec, arguments: dict[str, Any]) -> list[str]:
    """参数 → 完整 CLI 参数（复用 server._cli_args 逻辑）。"""
    args = _flags(spec.inputs, arguments)
    if spec.subcommands:
        command = arguments["command"]
        args.append(command)
        command_inputs = {
            name: field for name, field in spec.subcommands[command].get("inputs", {}).items()
            if name not in spec.inputs
        }
        args.extend(_flags(command_inputs, arguments))
    return args


def run_tool(spec: WirelessToolSpec, arguments: dict[str, Any], timeout: float) -> dict[str, Any]:
    """subprocess 执行 CLI，返回 JSON dict（复用 server._run_cli 逻辑，去掉 MCP 层）。"""
    if not isinstance(arguments, dict):
        return {"error": "arguments must be an object"}
    for name, value in arguments.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isfinite(value):
            return {"error": f"{name} must be finite"}
        if isinstance(value, str) and "\x00" in value:
            return {"error": f"{name} contains a NUL character"}

    # mcp_stdin 参数：值经 stdin 传入，命令行该参数传 "-"
    stdin_fields = [name for name, field in spec.inputs.items() if field.get("mcp_stdin") and name in arguments]
    cli_arguments = dict(arguments)
    stdin_payload = None
    if stdin_fields:
        field_name = stdin_fields[0]
        raw = arguments[field_name]
        stdin_payload = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
        cli_arguments[field_name] = "-"
    args = [sys.executable, str(spec.script), *_cli_args(spec, cli_arguments)]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            args,
            cwd=_wireless_root(),
            env=env,
            shell=False,
            capture_output=True,
            input=stdin_payload,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"error": f"{spec.name} exceeded {timeout:g} seconds"}
    except OSError as exc:
        return {"error": f"could not start {spec.name}: {exc.strerror or exc}"}

    if len(result.stdout.encode("utf-8")) > MAX_OUTPUT_BYTES:
        return {"error": f"{spec.name} output exceeded {MAX_OUTPUT_BYTES} bytes"}
    try:
        output = json.loads(result.stdout, parse_constant=lambda value: value)
    except json.JSONDecodeError:
        return {"error": f"{spec.name} did not return one JSON value"}
    if result.returncode != 0:
        message = output.get("error") if isinstance(output, dict) else None
        return {"error": str(message or f"{spec.name} exited with code {result.returncode}")}
    if not isinstance(output, dict):
        return {"error": f"{spec.name} returned a non-object JSON value"}
    return output
