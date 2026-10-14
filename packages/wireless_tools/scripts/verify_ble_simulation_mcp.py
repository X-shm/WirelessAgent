"""Smoke-check the two BLE simulation tools through the deployed stdio MCP path."""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters


TOOLBOX_ROOT = Path(__file__).resolve().parents[1]
TOOLS = {"bluetooth_path_loss", "bluetooth_session"}


async def verify() -> None:
    with tempfile.TemporaryDirectory(prefix="ble-mcp-smoke-") as data_root:
        server = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server", "--tools", ",".join(sorted(TOOLS)),
                  "--data-root", data_root, "--timeout", "30"],
            cwd=str(TOOLBOX_ROOT),
        )
        async with Client(server, read_timeout_seconds=45) as client:
            available = {tool.name for tool in (await client.list_tools()).tools}
            if available != TOOLS:
                raise RuntimeError(f"unexpected MCP tool set: {sorted(available)}")

            async def call(name: str, request: dict) -> dict:
                response = await client.call_tool(
                    name, {"input": json.dumps(request, ensure_ascii=False, separators=(",", ":"))}
                )
                body = response.structured_content
                if response.is_error or not isinstance(body, dict) or body.get("ok") is not True:
                    raise RuntimeError(f"{name} tools/call failed: {response.content}")
                result = body.get("result")
                if not isinstance(result, dict):
                    raise RuntimeError(f"{name} returned no result object")
                return result

            loss = await call("bluetooth_path_loss", {
                "distance": [1, 10], "environment": "Industrial",
                "path_loss_exponent": 2, "standard_deviation": 0,
            })
            values = loss.get("path_loss_db")
            if not isinstance(values, list) or len(values) != 2 or not values[1] > values[0]:
                raise RuntimeError("path-loss tools/call returned unexpected values")
            session = await call("bluetooth_session", {
                "operation": "create_session", "session_file": "smoke.sqlite",
            })
            if session.get("created") is not True:
                raise RuntimeError("Bluetooth session tools/call did not create a session")
            print(json.dumps({"ok": True, "tools": sorted(available), "path_loss_db": values}))


if __name__ == "__main__":
    asyncio.run(verify())
