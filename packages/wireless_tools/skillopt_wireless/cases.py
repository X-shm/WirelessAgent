"""Build independent tool-use cases from executable tool examples."""

from __future__ import annotations

import json
import re
import shlex
from collections.abc import Iterator
from copy import deepcopy
from pathlib import Path
from typing import Any

from mcp_server.catalog import ROOT, ToolSpec, load_catalog

SPLITS = ("train", "val", "test")
EMBEDDED_FILES = {"session_file", "output_path", "waveform_file"}
OUTPUT_FILES = {"output_file", "state_file"}

# Some examples have no arguments, constrained numeric domains, or structured
# input strings whose useful variants cannot be inferred from the JSON schema.
# These are still verified by an actual MCP invocation in build_dataset.py.
MANUAL_ARGUMENTS: dict[str, list[dict[str, Any]]] = {
    "interleaver": [{"kind": "random", "seed": 42}, {"kind": "random", "seed": 43}],
    "lte_ofdm": [{"nrb": "15"}, {"nrb": "25"}],
    "lte_scfdma": [{"nrb": 15}, {"nrb": 25}],
    "nr_layer_map": [
        {"symbols": "[2+1j,3+1.5j,4+2j,5+2.5j]"},
        {"symbols": "[3+1.5j,4+2j,5+2.5j,6+3j]"},
    ],
    "nr_mcs_tables": [{"mcs": 0}, {"mcs": 1}],
    "zadoff_chu_seq": [{"root": 5}, {"root": 11}],
}

# The schema example for wireless_utils is unseeded AWGN, so it cannot serve
# as a repeatable target. Use three deterministic subcommands instead.
DETERMINISTIC_CASES: dict[str, list[dict[str, Any]]] = {
    "wireless_utils": [
        {"command": "biterr", "x": "0,1,0,1", "y": "0,1,1,1"},
        {"command": "biterr", "x": "1,0,1,0", "y": "1,0,0,0"},
        {"command": "berawgn", "ebn0": 8.0, "mod": "BPSK"},
    ],
}

MANUAL_INPUTS: dict[str, list[dict[str, Any]]] = {
    "ble_cs_waveform": [
        {"properties": {"step_mode": 2, "tone_duration": 20}, "tone_extension_bit": 1},
        {"properties": {"step_mode": 2, "tone_duration": 10}, "tone_extension_bit": 1},
    ],
    "ble_att": [
        {"operation": "encode", "configuration": {"opcode": "Read request", "attribute_handle": "0002"}},
        {"operation": "encode", "configuration": {"opcode": "Read request", "attribute_handle": "0003"}},
    ],
    "ble_gap_data": [
        {"operation": "encode", "configuration": {"advertising_data_types": ["Flags"], "le_discoverability": "Limited"}},
        {"operation": "encode", "configuration": {"advertising_data_types": ["Flags"], "le_discoverability": "None"}},
    ],
    "ble_l2cap": [
        {"operation": "encode", "configuration": {"channel_identifier": "0004"}, "sdu": "0A0200"},
        {"operation": "encode", "configuration": {"channel_identifier": "0004"}, "sdu": "0A0300"},
    ],
    "ble_ll_advertising": [
        {"operation": "encode", "configuration": {"advertising_data": "020105"}},
        {"operation": "encode", "configuration": {"advertising_data": "020104"}},
    ],
    "ble_ll_data": [
        {"operation": "encode", "configuration": {"nesn": 1}},
        {"operation": "encode", "configuration": {"sequence_number": 1}},
    ],
    "ble_network_config": [
        {"kind": "bluetoothLEGAPConfig", "properties": {"max_connections": 6}},
        {"kind": "bluetoothLEGAPConfig", "properties": {"max_connections": 5}},
    ],
    "ble_packet_decode_status": [{"status": "Success"}, {"status": "InvalidLLID"}],
    "ble_pcap_writer": [
        {"file_extension": "pcapng", "packets": [{"packet": "D6BE898E4009AB8967452301020106A8F1DF", "timestamp_us": 2}]},
        {"file_extension": "pcapng", "packets": [{"packet": "D6BE898E4009AB8967452301020106A8F1DF", "timestamp_us": 3}]},
    ],
    "bluetooth_classic_config": [
        {"kind": "phy", "properties": {"mode": "BR"}},
        {"kind": "phy", "properties": {"mode": "EDR3M"}},
    ],
    "bluetooth_frequency_hop": [
        {"clock": "2D", "configuration": {"sequence_type": "Connection basic", "device_address": "2A96EF25"}},
        {"clock": "2E", "configuration": {"sequence_type": "Connection basic", "device_address": "2A96EF25"}},
    ],
    "bluetooth_session": [
        {"operation": "create_session", "session_file": "bt_e2e_session.sqlite", "overwrite": True},
        {"operation": "create_session", "session_file": "bt_e2e_session.sqlite", "overwrite": False},
    ],
}


def example_arguments(spec: ToolSpec) -> dict[str, Any]:
    source = json.loads((ROOT / "tools" / f"{spec.name}.schema.json").read_text(encoding="utf-8"))
    example = source.get("example") or {}
    command = example.get("cmd")
    if not isinstance(command, str) or not command:
        raise ValueError(f"{spec.name}: schema has no executable example")
    tokens = shlex.split(command, posix=True)
    if tokens and tokens[0].lower() in {"python", "python3", "py"}:
        tokens.pop(0)
    if not tokens or Path(tokens.pop(0)).name != f"{spec.name}.py":
        raise ValueError(f"{spec.name}: example names the wrong script")
    fields = spec.input_schema["properties"]
    arguments: dict[str, Any] = {}
    while tokens:
        token = tokens.pop(0)
        if not token.startswith("--"):
            if "command" in arguments:
                raise ValueError(f"{spec.name}: multiple subcommands")
            arguments["command"] = token
            continue
        name = token[2:]
        if name not in fields:
            raise ValueError(f"{spec.name}: unknown example field {name}")
        kind = fields[name]["type"]
        if kind == "boolean":
            arguments[name] = True
            continue
        if not tokens:
            raise ValueError(f"{spec.name}: missing example value for {name}")
        raw = tokens.pop(0)
        arguments[name] = int(raw) if kind == "integer" else float(raw) if kind == "number" else raw
    return arguments


def _numeric_variants(value: int | float) -> list[int | float]:
    if value in (0, 1):
        return [1 - value, value + 1]
    return [value + 1, value - 1, 0]


def _mutate_json(value: Any) -> Iterator[Any]:
    if isinstance(value, bool):
        yield not value
    elif isinstance(value, (int, float)):
        yield from _numeric_variants(value)
    elif isinstance(value, list):
        for index, item in enumerate(value[:4]):
            for changed in _mutate_json(item):
                clone = deepcopy(value)
                clone[index] = changed
                yield clone
    elif isinstance(value, dict):
        for key, item in list(value.items())[:12]:
            if key in EMBEDDED_FILES or key.endswith("_file"):
                continue
            for changed in _mutate_json(item):
                clone = deepcopy(value)
                clone[key] = changed
                yield clone


def _string_variants(value: str) -> Iterator[str]:
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        decoded = None
    if isinstance(decoded, (dict, list)):
        for changed in _mutate_json(decoded):
            yield json.dumps(changed, ensure_ascii=False, separators=(",", ":"))
        return
    if re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        number = float(value) if "." in value else int(value)
        for changed in _numeric_variants(number):
            yield str(changed)
        return
    if re.fullmatch(r"[01]{3,}", value):
        yield ("1" if value[0] == "0" else "0") + value[1:]
        yield value[:-1] + ("1" if value[-1] == "0" else "0")
        return
    if "," in value:
        pieces = value.split(",")
        for index in range(min(len(pieces), 3)):
            raw = pieces[index].strip()
            if not re.fullmatch(r"-?\d+(?:\.\d+)?", raw):
                continue
            number = float(raw) if "." in raw else int(raw)
            for changed in _numeric_variants(number):
                clone = pieces.copy()
                clone[index] = str(changed)
                yield ",".join(clone)


def candidate_arguments(spec: ToolSpec, base: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield deterministic one-field mutations; callers keep only successful MCP calls."""
    if spec.name in DETERMINISTIC_CASES:
        yield from DETERMINISTIC_CASES[spec.name]
        return
    for override in MANUAL_ARGUMENTS.get(spec.name, []):
        yield {**base, **override}
    for request in MANUAL_INPUTS.get(spec.name, []):
        yield {**base, "input": json.dumps(request, ensure_ascii=False, separators=(",", ":"))}
    fields = spec.input_schema["properties"]
    for name, value in base.items():
        if name == "command" or name in OUTPUT_FILES or name.endswith("_file"):
            continue
        field = fields[name]
        values: list[Any] = []
        if "enum" in field:
            values.extend(item for item in field["enum"] if item != value)
        elif isinstance(value, bool):
            values.append(not value)
        elif isinstance(value, (int, float)):
            values.extend(_numeric_variants(value))
        elif isinstance(value, str):
            values.extend(_string_variants(value))
        for changed in values:
            clone = dict(base)
            clone[name] = changed
            yield clone


def _rewrite_embedded_paths(value: Any, case_id: str) -> Any:
    if isinstance(value, dict):
        return {
            key: f"{case_id}_{Path(item).name}" if
            (key in EMBEDDED_FILES or key.endswith("_file")) and isinstance(item, str)
            else _rewrite_embedded_paths(item, case_id)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_rewrite_embedded_paths(item, case_id) for item in value]
    return value


def isolated_arguments(arguments: dict[str, Any], case_id: str) -> dict[str, Any]:
    """Keep side-effectful examples from sharing generated artifact paths."""
    result = dict(arguments)
    for name, value in arguments.items():
        if name in OUTPUT_FILES and isinstance(value, str):
            result[name] = f"{case_id}_{Path(value).name}"
        elif name in {"input", "state"} and isinstance(value, str):
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                continue
            rewritten = _rewrite_embedded_paths(decoded, case_id)
            if rewritten != decoded:
                result[name] = json.dumps(rewritten, ensure_ascii=False, separators=(",", ":"))
    return result


def question_for(spec: ToolSpec, arguments: dict[str, Any], split: str) -> str:
    task = spec.description.split("。", 1)[0].strip()
    task = re.sub(re.escape(spec.name), "对应计算", task, flags=re.IGNORECASE)
    presented = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
    if split == "train":
        return f"请完成无线通信计算：{task}。给定参数：{presented}。请调用合适的工具并返回 JSON 结果。"
    if split == "val":
        return f"我需要{task}；输入参数为 {presented}。请用工具计算，按结果回答。"
    return f"根据以下输入求{task}：{presented}。给出实际工具计算所得的 JSON。"


def registry_names() -> set[str]:
    return set(load_catalog())
