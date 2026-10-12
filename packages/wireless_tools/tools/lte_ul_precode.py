"""LTE SC-FDMA DFT precoding/deprecoding matching public MATLAB M-file logic."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def _block_size(n, resource_type):
    n = int(n)
    if n < 1:
        raise ValueError("n must be positive")
    if resource_type.lower() == "prb":
        return 12*n
    if resource_type.lower() == "subcarrier":
        return n
    raise ValueError("resource_type must be PRB or Subcarrier")


def ul_precode(values, n, resource_type="PRB", inverse=False):
    data = np.asarray(values, dtype=complex)
    if data.ndim == 1:
        data = data[:, None]
    if data.ndim != 2:
        raise ValueError("values must be a one/two-dimensional complex array")
    block = _block_size(n, resource_type)
    if data.shape[0] % block:
        raise ValueError("first dimension must be divisible by the configured subcarrier block")
    matrix = data.reshape((block, data.size//block), order="F")
    if block == 1:
        transformed = matrix
    elif inverse:
        transformed = np.fft.ifft(matrix*math.sqrt(block), axis=0)
    else:
        transformed = np.fft.fft(matrix, axis=0)/math.sqrt(block)
    return transformed.reshape(data.shape, order="F")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["precode", "deprecode"], required=True)
    parser.add_argument("--values", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--resource_type", choices=["PRB", "Subcarrier"], default="PRB")
    args = parser.parse_args()
    try:
        output = ul_precode(parse_complex(args.values), args.n, args.resource_type, args.mode == "deprecode")
        print(json.dumps({"output": complex_json(output), "block_size": _block_size(args.n, args.resource_type)}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
