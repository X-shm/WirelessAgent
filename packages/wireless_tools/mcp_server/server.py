"""MCP transport and strict adapter for the existing wireless-toolbox CLIs."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from mcp.server import Server, ServerRequestContext
from mcp.server.stdio import stdio_server
from mcp import types

from .catalog import ROOT, ToolSpec, load_catalog
from .file_policy import FilePolicy, FilePolicyError


MAX_OUTPUT_BYTES = 1_000_000


def _error(code: str, message: str) -> types.CallToolResult:
    payload = {"code": code, "message": message}
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))],
        isError=True,
    )


def _validate(spec: ToolSpec, arguments: dict[str, Any]) -> str | None:
    errors = sorted(Draft202012Validator(spec.input_schema).iter_errors(arguments), key=lambda e: str(e.path))
    if errors:
        return errors[0].message
    for name, value in arguments.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isfinite(value):
            return f"{name} must be finite"
        if isinstance(value, str) and "\x00" in value:
            return f"{name} contains a NUL character"
    return None


def _flags(inputs: dict[str, dict[str, Any]], arguments: dict[str, Any]) -> list[str]:
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
            # argparse treats a leading '-' in comma-separated vectors as a
            # new option unless the value is attached to its flag.
            if rendered.startswith("-"):
                args.append(f"--{name}={rendered}")
            else:
                args.extend((f"--{name}", rendered))
    return args


def _cli_args(spec: ToolSpec, arguments: dict[str, Any]) -> list[str]:
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


def _run_cli(spec: ToolSpec, arguments: dict[str, Any], timeout: float) -> types.CallToolResult:
    stdin_fields = [name for name, field in spec.inputs.items()
                    if field.get("mcp_stdin") and name in arguments]
    if len(stdin_fields) > 1:
        return _error("EXECUTION_FAILED", f"{spec.name} has multiple stdin inputs")
    cli_arguments = dict(arguments)
    stdin_payload = None
    if stdin_fields:
        field_name = stdin_fields[0]
        stdin_payload = arguments[field_name]
        cli_arguments[field_name] = "-"
    args = [sys.executable, str(spec.script), *_cli_args(spec, cli_arguments)]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
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
        return _error("TIMEOUT", f"{spec.name} exceeded {timeout:g} seconds")
    except OSError as exc:
        return _error("EXECUTION_FAILED", f"could not start {spec.name}: {exc.strerror or exc}")

    if len(result.stdout.encode("utf-8")) > MAX_OUTPUT_BYTES:
        return _error("OUTPUT_TOO_LARGE", f"{spec.name} output exceeded {MAX_OUTPUT_BYTES} bytes")
    try:
        # Python CLI tools can emit Infinity/NaN; encode them as strings so the
        # MCP result remains valid JSON on every transport.
        output = json.loads(result.stdout, parse_constant=lambda value: value)
    except json.JSONDecodeError:
        return _error("INVALID_OUTPUT", f"{spec.name} did not return one JSON value")
    if result.returncode != 0:
        message = output.get("error") if isinstance(output, dict) else None
        return _error("TOOL_ERROR", str(message or f"{spec.name} exited with code {result.returncode}"))
    if not isinstance(output, dict):
        return _error("INVALID_OUTPUT", f"{spec.name} returned a non-object JSON value")
    encoded = json.dumps(output, ensure_ascii=False, allow_nan=False)
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=encoded)],
        structuredContent=output,
    )


def create_server(
    *, timeout: float = 30.0, only: set[str] | None = None, data_root: Path | None = None
) -> Server[Any]:
    catalog = load_catalog(only)
    file_policy = FilePolicy(data_root)
    semaphore = asyncio.Semaphore(2)

    async def list_tools(
        _context: ServerRequestContext[Any], _params: types.PaginatedRequestParams | None
    ) -> types.ListToolsResult:
        return types.ListToolsResult(
            tools=[
                types.Tool(name=spec.name, description=spec.description, inputSchema=spec.input_schema)
                for spec in catalog.values()
            ]
        )

    async def call_tool(
        _context: ServerRequestContext[Any], params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        spec = catalog.get(params.name)
        if spec is None:
            return _error("UNKNOWN_TOOL", f"unknown tool: {params.name}")
        arguments = params.arguments or {}
        if not isinstance(arguments, dict):
            return _error("INVALID_ARGUMENT", "arguments must be an object")
        message = _validate(spec, arguments)
        if message:
            return _error("INVALID_ARGUMENT", message)
        try:
            arguments = file_policy.prepare(arguments)
        except FilePolicyError as exc:
            return _error("INVALID_PATH", str(exc))
        async with semaphore:
            return await asyncio.to_thread(_run_cli, spec, arguments, timeout)

    return Server(
        "wireless-toolbox",
        version="0.2.0",
        title="Wireless Toolbox",
        description="Validated wireless communications calculations from local Python CLI tools.",
        on_list_tools=list_tools,
        on_call_tool=call_tool,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Wireless Toolbox MCP server")
    parser.add_argument("--transport", choices=("stdio", "streamable-http"), default="stdio")
    parser.add_argument("--port", type=int, default=8765, help="HTTP port (loopback only)")
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-tool timeout in seconds")
    parser.add_argument("--data-root", type=Path, help="Directory permitted for agent-supplied file paths")
    parser.add_argument("--tools", help="Optional comma-separated subset of registered tool names")
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be a positive finite number")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be in 1..65535")
    selected = {name.strip() for name in args.tools.split(",")} if args.tools else None
    if selected is not None and "" in selected:
        parser.error("--tools contains an empty name")
    try:
        server = create_server(timeout=args.timeout, only=selected, data_root=args.data_root)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))
    if args.transport == "stdio":
        async def run_stdio() -> None:
            async with stdio_server() as streams:
                await server.run(streams[0], streams[1], server.create_initialization_options())

        asyncio.run(run_stdio())
    else:
        import uvicorn

        uvicorn.run(server.streamable_http_app(host="127.0.0.1"), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
