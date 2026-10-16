"""Independent NR transform precoding and deprecoding (TS 38.211)."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def transform(symbols: np.ndarray, mrb: int, inverse: bool = False) -> np.ndarray:
    """Apply a unitary DFT to each 12*mrb row block of each layer."""
    if not isinstance(mrb, int) or mrb <= 0:
        raise ValueError("mrb must be a positive integer")
    values = np.asarray(symbols, dtype=np.complex128)
    if values.ndim not in (1, 2) or values.shape[0] == 0:
        raise ValueError("symbols must be a nonempty vector or matrix")
    block = 12 * mrb
    if values.shape[0] % block:
        raise ValueError("the number of symbol rows must be divisible by 12*mrb")
    matrix = values.reshape(-1, 1) if values.ndim == 1 else values
    blocks = matrix.reshape(-1, block, matrix.shape[1])
    if inverse:
        result = np.fft.ifft(blocks, axis=1) * np.sqrt(block)
    else:
        result = np.fft.fft(blocks, axis=1) / np.sqrt(block)
    result = result.reshape(matrix.shape)
    return result[:, 0] if values.ndim == 1 else result


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR DFT transform precode/deprecode")
    parser.add_argument("--operation", choices=("precode", "deprecode"), required=True)
    parser.add_argument("--mrb", type=int, required=True)
    parser.add_argument("--symbols", required=True, help="Complex JSON vector/matrix: {real,imag}")
    args = parser.parse_args()
    try:
        result = transform(parse_complex(args.symbols), args.mrb, args.operation == "deprecode")
        print(json.dumps({"symbols": complex_json(result), "shape": list(result.shape)}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
