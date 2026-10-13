"""End-to-end checks for the MCP adapter, including both transports."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

from mcp_server.catalog import ROOT, load_catalog
from mcp_server.server import create_server
from scripts.test_agent_e2e import extract_example_cmd


CASES = {
    "q_function": {"mode": "qfunc", "values": "[0,1]"},
    "ber_awgn": {"ebno_db": "0,5", "modulation": "bpsk"},
    "convert_snr": {"x": "6", "input_mode": "ebno", "bits_per_symbol": 2},
    "nr_tbs": {"modulation": "QPSK", "nlayers": 1, "nprb": 52, "nre-per-prb": 120, "tcr": 0.5},
    "lte_mcs": {"imcs": "17"},
    "link_capacity": {"snr_db": 0, "bandwidth_hz": 1_000_000},
}


def example_arguments(name: str) -> dict:
    schema = json.loads((ROOT / "tools" / f"{name}.schema.json").read_text(encoding="utf-8"))
    tokens = extract_example_cmd(schema)
    if not tokens or not tokens[0].endswith(f"{name}.py"):
        raise ValueError(f"bad example command for {name}")
    spec = load_catalog({name})[name]
    fields = spec.input_schema["properties"]
    arguments: dict = {}
    i = 1
    while i < len(tokens):
        token = tokens[i]
        if not token.startswith("--"):
            if "command" in arguments:
                raise ValueError(f"multiple subcommands for {name}")
            arguments["command"] = token
            i += 1
            continue
        key = token[2:]
        if key not in fields:
            raise ValueError(f"unknown example flag for {name}: {key}")
        kind = fields[key]["type"]
        if kind == "boolean":
            arguments[key] = True
            i += 1
            continue
        if i + 1 >= len(tokens):
            raise ValueError(f"missing example value for {name}.{key}")
        raw = tokens[i + 1]
        arguments[key] = int(raw) if kind == "integer" else float(raw) if kind == "number" else raw
        i += 2
    return arguments


def direct_cli(name: str, arguments: dict) -> dict:
    spec = load_catalog()[name]
    cmd = [sys.executable, str(spec.script)]
    for field, value in arguments.items():
        if isinstance(value, bool):
            if value:
                cmd.append(f"--{field}")
        else:
            cmd.extend((f"--{field}", str(value)))
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


class MCPServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_registered_examples_over_mcp(self) -> None:
        catalog = load_catalog()
        self.assertEqual(len(catalog), 144)
        with tempfile.TemporaryDirectory(prefix="wireless-mcp-test-") as temp:
            async with Client(create_server(data_root=Path(temp)), read_timeout_seconds=45) as client:
                tools = (await client.list_tools()).tools
                self.assertEqual({tool.name for tool in tools}, set(catalog))
                for name in catalog:
                    with self.subTest(name=name):
                        result = await client.call_tool(name, example_arguments(name))
                        self.assertFalse(result.is_error, f"{name}: {result.content}")
                        self.assertIsInstance(result.structured_content, dict)

    async def test_pilot_tools_match_cli(self) -> None:
        async with Client(create_server()) as client:
            for name, args in CASES.items():
                with self.subTest(name=name):
                    result = await client.call_tool(name, args)
                    self.assertFalse(result.is_error)
                    self.assertEqual(result.structured_content, direct_cli(name, args))
            differential = {"ebno_db": "0", "modulation": "bpsk", "differential": True}
            result = await client.call_tool("ber_awgn", differential)
            self.assertEqual(result.structured_content, direct_cli("ber_awgn", differential))

    async def test_validation_and_tool_error(self) -> None:
        async with Client(create_server()) as client:
            invalid = await client.call_tool("link_capacity", {"snr_db": 0, "bandwidth_hz": 1, "extra": 1})
            self.assertTrue(invalid.is_error)
            self.assertEqual(json.loads(invalid.content[0].text)["code"], "INVALID_ARGUMENT")
            missing = await client.call_tool("q_function", {"mode": "qfunc"})
            self.assertTrue(missing.is_error)
            self.assertEqual(json.loads(missing.content[0].text)["code"], "INVALID_ARGUMENT")
            failed = await client.call_tool("q_function", {"mode": "qfuncinv", "values": "2"})
            self.assertTrue(failed.is_error)
            self.assertEqual(json.loads(failed.content[0].text)["code"], "TOOL_ERROR")
            infinite = await client.call_tool("q_function", {"mode": "qfuncinv", "values": "0"})
            self.assertFalse(infinite.is_error)
            self.assertEqual(infinite.structured_content, {"output": ["Infinity"]})
            subcommand = await client.call_tool("wireless_utils", {"command": "biterr", "x": "0,1", "y": "0,0"})
            self.assertFalse(subcommand.is_error)
            self.assertEqual(subcommand.structured_content["num_errors"], 1)
            for arguments in (
                {"command": "awgn", "signal": "1,0", "snr": 10},
                {"command": "berawgn", "ebn0": 0, "mod": "bpsk"},
                {"command": "bcc-interleave", "bits": "0,1,0,1", "ncbps": 4},
                {"command": "golay", "length": 32},
            ):
                with self.subTest(command=arguments["command"]):
                    result = await client.call_tool("wireless_utils", arguments)
                    self.assertFalse(result.is_error, str(result.content))
            scramble = await client.call_tool(
                "nr_dci", {"command": "scramble", "dci-bits": "1,0,1,1", "rnti": 4660, "n-id": 1}
            )
            self.assertFalse(scramble.is_error, str(scramble.content))
            inverse = await client.call_tool(
                "nr_modulation", {"mod": "BPSK", "inverse": True, "symbols": "[1]"}
            )
            self.assertFalse(inverse.is_error, str(inverse.content))
            mcs = await client.call_tool("nr_mcs_tables", {"table": "QAM256Table", "mcs": 0})
            self.assertFalse(mcs.is_error, str(mcs.content))
            bad_subcommand = await client.call_tool("wireless_utils", {"command": "biterr", "signal": "1"})
            self.assertTrue(bad_subcommand.is_error)
            self.assertEqual(json.loads(bad_subcommand.content[0].text)["code"], "INVALID_ARGUMENT")
            escaped = await client.call_tool("awgn", {"signal_file": "../secret.json", "snr": 1})
            self.assertTrue(escaped.is_error)
            self.assertEqual(json.loads(escaped.content[0].text)["code"], "INVALID_PATH")

    async def test_selected_tool_subset(self) -> None:
        async with Client(create_server(only={"q_function", "nr_tbs"})) as client:
            self.assertEqual(
                {tool.name for tool in (await client.list_tools()).tools}, {"q_function", "nr_tbs"}
            )

    async def test_negative_vector_argument(self) -> None:
        async with Client(create_server(only={"node_mobility_constant_velocity"})) as client:
            result = await client.call_tool("node_mobility_constant_velocity", {
                "initial_position": "10,5,0", "velocity": "-1,2,0", "times": "0,4,8",
            })
            self.assertFalse(result.is_error, str(result.content))
            self.assertEqual(result.structured_content["positions"], [
                [10.0, 5.0, 0.0], [6.0, 13.0, 0.0], [2.0, 21.0, 0.0],
            ])

    async def test_file_modes_stay_in_data_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wireless-mcp-files-") as temp:
            root = Path(temp)
            (root / "input.json").write_text(
                json.dumps({"distance": [1, 10], "environment": "Industrial", "standard_deviation": 0}),
                encoding="utf-8",
            )
            (root / "bad.json").write_text(
                '{"operation":"create_session","session_file":"../outside.sqlite"}', encoding="utf-8"
            )
            async with Client(create_server(data_root=root)) as client:
                loaded = await client.call_tool("bluetooth_path_loss", {"input_file": "input.json"})
                self.assertFalse(loaded.is_error, str(loaded.content))
                exported = await client.call_tool(
                    "bluetooth_classic_waveform",
                    {"input": '{"message":[1,0,1,0],"properties":{"packet_type":"NULL"}}',
                     "output_file": "wave.npz"},
                )
                self.assertFalse(exported.is_error, str(exported.content))
                self.assertTrue((root / "wave.npz").is_file())
                capture = await client.call_tool(
                    "ble_pcap_writer",
                    {"input": json.dumps({"file_extension": "pcapng", "packets": [
                        {"packet": "D6BE898E4009AB8967452301020106A8F1DF", "timestamp_us": 0}
                    ], "output_path": "capture.pcapng"})},
                )
                self.assertFalse(capture.is_error, str(capture.content))
                self.assertTrue((root / "capture.pcapng").is_file())
                escaped = await client.call_tool(
                    "bluetooth_session",
                    {"input": '{"operation":"create_session","session_file":"../outside.sqlite"}'},
                )
                self.assertTrue(escaped.is_error)
                self.assertEqual(json.loads(escaped.content[0].text)["code"], "INVALID_PATH")
                escaped_file = await client.call_tool("bluetooth_session", {"input_file": "bad.json"})
                self.assertTrue(escaped_file.is_error)
                self.assertEqual(json.loads(escaped_file.content[0].text)["code"], "INVALID_PATH")
                created = await client.call_tool(
                    "bluetooth_session",
                    {"input": '{"operation":"create_session","session_file":"state.sqlite"}'},
                )
                self.assertFalse(created.is_error, str(created.content))
                self.assertTrue((root / "state.sqlite").is_file())

    async def test_stdio_subprocess(self) -> None:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server"],
            cwd=str(ROOT),
        )
        async with Client(params) as client:
            self.assertEqual(len((await client.list_tools()).tools), 144)
            result = await client.call_tool("lte_mcs", {"imcs": "17"})
            self.assertFalse(result.is_error)
            self.assertEqual(result.structured_content["itbs"], 15)

    async def test_streamable_http(self) -> None:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        process = subprocess.Popen(
            [sys.executable, "-m", "mcp_server", "--transport", "streamable-http", "--port", str(port)],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=os.environ.copy(),
        )
        try:
            for _ in range(100):
                if process.poll() is not None:
                    self.fail(f"HTTP server exited with code {process.returncode}")
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                        break
                except OSError:
                    await asyncio.sleep(0.1)
            else:
                self.fail("HTTP server did not start")
            async with Client(f"http://127.0.0.1:{port}/mcp") as client:
                self.assertEqual(len((await client.list_tools()).tools), 144)
                result = await client.call_tool("link_capacity", CASES["link_capacity"])
                self.assertFalse(result.is_error)
                self.assertEqual(result.structured_content["capacity_bps"], 1_000_000)
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
