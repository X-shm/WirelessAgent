"""Shared JSON CLI helpers for standalone NR extension tools."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


def bits(value, name="bits") -> np.ndarray:
    raw = np.asarray(value)
    if raw.size == 0 or not np.all((raw == 0) | (raw == 1)):
        raise ValueError(f"{name} must be a nonempty binary vector")
    return raw.reshape(-1).astype(np.uint8)


def complex_array(value, name="samples") -> np.ndarray:
    if isinstance(value, dict) and "real" in value:
        real = np.asarray(value["real"], dtype=float)
        imag = np.asarray(value.get("imag", np.zeros_like(real)), dtype=float)
        if real.shape != imag.shape:
            raise ValueError(f"{name} real/imag shapes differ")
        return real + 1j * imag
    return np.asarray(value, dtype=complex)


def json_ready(value):
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return {"real": value.real.tolist(), "imag": value.imag.tolist()}
        return value.tolist()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    return value


def run_cli(description: str, functions: dict[str, object]) -> None:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--function", required=True, choices=sorted(functions))
    parser.add_argument("--params", required=True, help="JSON object of function parameters")
    args = parser.parse_args()
    try:
        payload = sys.stdin.read() if args.params == "-" else args.params
        params = json.loads(payload)
        if not isinstance(params, dict):
            raise ValueError("params must be a JSON object")
        result = functions[args.function](**params)
        print(json.dumps({"function": args.function, "result": json_ready(result)}, allow_nan=False))
    except (ValueError, TypeError, KeyError, IndexError, OverflowError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)
