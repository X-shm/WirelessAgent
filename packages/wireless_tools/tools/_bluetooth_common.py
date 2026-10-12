"""Shared JSON, state, and artifact support for Bluetooth CLI tools.

The Bluetooth tools deliberately keep their process boundary stateless.  A
caller that needs to continue a whitening, hopping, or network simulation
passes the returned ``state`` object to the next invocation.  This module is
small and dependency-free apart from NumPy so every tool emits the same,
machine-readable result envelope.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np


INLINE_LIMIT_DEFAULT = 4096
STATE_VERSION = 1


class InputError(ValueError):
    """A request cannot be represented by the public CLI contract."""


def json_object(value: str | None, path: str | None, field: str) -> dict[str, Any]:
    if (value is None) == (path is None):
        raise InputError(f"provide exactly one of --{field} or --{field}_file")
    try:
        text = Path(path).read_text(encoding="utf-8") if path else value
        decoded = json.loads(text or "")
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"invalid {field} JSON: {exc}") from exc
    if not isinstance(decoded, dict):
        raise InputError(f"{field} must be a JSON object")
    return decoded


def add_common_arguments(parser: argparse.ArgumentParser, *, stateful: bool = False, artifacts: bool = False) -> None:
    request = parser.add_mutually_exclusive_group(required=True)
    request.add_argument("--input", help="JSON request object")
    request.add_argument("--input_file", help="UTF-8 JSON request file")
    if stateful:
        state = parser.add_mutually_exclusive_group()
        state.add_argument("--state", help="previous JSON state object")
        state.add_argument("--state_file", help="UTF-8 JSON state file")
    if artifacts:
        parser.add_argument("--output_file", help="NPZ or PCAP destination for a large result")
        parser.add_argument("--inline_limit", type=int, default=INLINE_LIMIT_DEFAULT,
                            help=f"maximum scalar values returned inline (default: {INLINE_LIMIT_DEFAULT})")
        parser.add_argument("--overwrite", action="store_true", help="allow replacement of --output_file")


def load_request(args: argparse.Namespace) -> dict[str, Any]:
    return json_object(args.input, args.input_file, "input")


def load_state(args: argparse.Namespace, kind: str) -> dict[str, Any] | None:
    if not hasattr(args, "state") or (args.state is None and args.state_file is None):
        return None
    state = json_object(args.state, args.state_file, "state")
    if state.get("schema_version") != STATE_VERSION or state.get("kind") != kind:
        raise InputError(f"state must be a version {STATE_VERSION} {kind!r} state object")
    payload = state.get("value")
    if not isinstance(payload, dict):
        raise InputError("state.value must be a JSON object")
    return payload


def make_state(kind: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": STATE_VERSION, "kind": kind, "value": value}


def complex_to_json(values: Any) -> dict[str, Any]:
    array = np.asarray(values)
    return {"real": array.real.tolist(), "imag": array.imag.tolist()}


def complex_from_json(value: Any, field: str) -> np.ndarray:
    if not isinstance(value, dict) or "real" not in value:
        raise InputError(f"{field} must be {{'real': [...], 'imag': [...]}}")
    real = np.asarray(value["real"], dtype=float)
    imag = np.asarray(value.get("imag", np.zeros_like(real)), dtype=float)
    if real.shape != imag.shape:
        raise InputError(f"{field}.real and {field}.imag must have the same shape")
    return real + 1j * imag


def bit_vector(value: Any, field: str, *, max_length: int | None = None) -> np.ndarray:
    if not isinstance(value, list) or any(bit not in (0, 1, False, True) for bit in value):
        raise InputError(f"{field} must be a JSON array of 0/1 bits")
    if max_length is not None and len(value) > max_length:
        raise InputError(f"{field} must contain at most {max_length} bits")
    return np.asarray(value, dtype=np.uint8)


def artifact(path_text: str, arrays: dict[str, np.ndarray], overwrite: bool) -> dict[str, Any]:
    path = Path(path_text).expanduser().resolve()
    if path.exists() and not overwrite:
        raise InputError(f"output file already exists: {path}; pass --overwrite to replace it")
    if path.suffix.lower() != ".npz":
        raise InputError("large array output must use a .npz path")
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "path": str(path), "format": "npz", "sha256": digest,
        "bytes": path.stat().st_size,
        "arrays": {name: {"shape": list(value.shape), "dtype": str(value.dtype)} for name, value in arrays.items()},
    }


def array_result(name: str, values: np.ndarray, args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    values = np.asarray(values)
    if values.size <= args.inline_limit:
        encoded: Any = complex_to_json(values) if np.iscomplexobj(values) else values.tolist()
        return {name: encoded}, []
    if not args.output_file:
        raise InputError(f"{name} has {values.size} values; provide --output_file or raise --inline_limit")
    return {name: None}, [artifact(args.output_file, {name: values}, args.overwrite)]


def envelope(tool: str, result: dict[str, Any], *, state: dict[str, Any] | None = None,
             artifacts: list[dict[str, Any]] | None = None, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "ok": True, "tool": tool, "result": result, "state": state,
        "artifacts": artifacts or [], "warnings": warnings or [],
        "metadata": {"implementation": "pure_python", "state_protocol": STATE_VERSION},
    }


def run_cli(tool: str, handler: Callable[[argparse.Namespace, dict[str, Any]], dict[str, Any]],
            *, stateful: bool = False, artifacts: bool = False, description: str = "") -> None:
    parser = argparse.ArgumentParser(description=description or tool)
    add_common_arguments(parser, stateful=stateful, artifacts=artifacts)
    args = parser.parse_args()
    try:
        answer = handler(args, load_request(args))
        print(json.dumps(envelope(tool, **answer), ensure_ascii=False, allow_nan=False))
    except InputError as exc:
        print(json.dumps({"ok": False, "tool": tool, "error": {"code": "invalid_input", "message": str(exc)}}), file=sys.stdout)
        raise SystemExit(2)
    except Exception as exc:  # CLI users must never receive a traceback as the response body.
        print(json.dumps({"ok": False, "tool": tool, "error": {"code": "runtime_error", "message": str(exc)}}), file=sys.stdout)
        raise SystemExit(1)
