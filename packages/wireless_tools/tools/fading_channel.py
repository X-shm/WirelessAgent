"""Memoryless/block flat Rayleigh and Rician fading channel."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np


def flat_fading(signal, model: str = "rayleigh", k_factor: float = 0.0, seed: int | None = None, block_length: int = 1):
    x = np.asarray(signal, dtype=complex).reshape(-1)
    model = model.lower()
    if model not in ("rayleigh", "rician"):
        raise ValueError("model must be rayleigh or rician")
    if k_factor < 0 or block_length < 1:
        raise ValueError("k_factor must be nonnegative and block_length positive")
    rng = np.random.default_rng(seed)
    blocks = (len(x) + block_length - 1) // block_length
    diffuse = (rng.normal(size=blocks) + 1j * rng.normal(size=blocks)) / math.sqrt(2.0)
    if model == "rayleigh":
        coefficients = diffuse
    else:
        coefficients = math.sqrt(k_factor / (k_factor + 1.0)) + diffuse / math.sqrt(k_factor + 1.0)
    gains = np.repeat(coefficients, block_length)[:len(x)]
    return x * gains, gains


def _complex_values(text: str) -> np.ndarray:
    value = json.loads(text)
    if isinstance(value, dict):
        real = np.asarray(value.get("real", []), dtype=float)
        imag = np.asarray(value.get("imag", np.zeros_like(real)), dtype=float)
        if real.shape != imag.shape:
            raise ValueError("real and imag arrays must have equal length")
        return real + 1j * imag
    return np.asarray(value, dtype=float).astype(complex)


def _complex_json(values) -> dict:
    values = np.asarray(values)
    return {"real": values.real.tolist(), "imag": values.imag.tolist()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--signal", required=True)
    parser.add_argument("--model", choices=["rayleigh", "rician"], default="rayleigh")
    parser.add_argument("--k_factor", type=float, default=0.0)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--block_length", type=int, default=1)
    args = parser.parse_args()
    try:
        output, gains = flat_fading(_complex_values(args.signal), args.model, args.k_factor, args.seed, args.block_length)
        print(json.dumps({"output": _complex_json(output), "path_gains": _complex_json(gains), "average_gain_power": float(np.mean(np.abs(gains)**2)) if len(gains) else 0.0}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
