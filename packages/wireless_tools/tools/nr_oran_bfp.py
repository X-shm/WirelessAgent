"""Standalone O-RAN block floating point compression for NR resource grids."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def _as_grid(values: np.ndarray) -> tuple[np.ndarray, int]:
    grid = np.asarray(values, dtype=np.complex128)
    if grid.ndim not in (1, 2, 3) or grid.shape[0] == 0 or grid.shape[0] % 12:
        raise ValueError("grid must be a 1-D/2-D/3-D array with subcarrier count divisible by 12")
    ndim = grid.ndim
    if ndim == 1:
        grid = grid[:, None, None]
    elif ndim == 2:
        grid = grid[:, :, None]
    return grid, ndim


def _restore(values: np.ndarray, ndim: int) -> np.ndarray:
    return values if ndim == 3 else values[..., 0] if ndim == 2 else values[:, 0, 0]


def bfp_compress(grid: np.ndarray, ciq_width: int) -> tuple[np.ndarray, np.ndarray]:
    if not 1 <= ciq_width <= 16:
        raise ValueError("ciq_width must be 1..16")
    values, ndim = _as_grid(grid)
    if not np.all(np.isfinite(values)) or not np.all(values.real == np.trunc(values.real)) or not np.all(values.imag == np.trunc(values.imag)):
        raise ValueError("grid must contain finite integer-valued IQ samples")
    nrb, nsym, nport = values.shape[0] // 12, values.shape[1], values.shape[2]
    result = np.empty_like(values)
    exponents = np.zeros((nrb, nsym, nport), dtype=int)
    for rb in range(nrb):
        for symbol in range(nsym):
            for port in range(nport):
                block = values[12 * rb:12 * (rb + 1), symbol, port]
                peak = int(max(np.max(np.abs(block.real)), np.max(np.abs(block.imag))))
                exponent = max(0, peak.bit_length() - (ciq_width - 1))
                scale = 2 ** exponent
                result[12 * rb:12 * (rb + 1), symbol, port] = (
                    np.trunc(block.real / scale) + 1j * np.trunc(block.imag / scale)
                )
                exponents[rb, symbol, port] = exponent
    return _restore(result, ndim), _restore(exponents, ndim)


def bfp_decompress(grid: np.ndarray, parameters: np.ndarray) -> np.ndarray:
    values, ndim = _as_grid(grid)
    nrb, nsym, nport = values.shape[0] // 12, values.shape[1], values.shape[2]
    params = np.asarray(parameters)
    expected = (nrb, nsym, nport)
    if params.size != nrb * nsym * nport or not np.all(params == np.trunc(params)):
        raise ValueError(f"parameters must contain one integer exponent per PRB/symbol/port: {expected}")
    params = params.reshape(expected)
    if np.any(params < 0) or np.any(params > 31):
        raise ValueError("BFP exponents must be 0..31")
    scales = 2.0 ** np.repeat(params.astype(int), 12, axis=0)
    return _restore(values * scales, ndim)


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent O-RAN BFP IQ compression/decompression")
    parser.add_argument("--operation", choices=("compress", "decompress"), required=True)
    parser.add_argument("--grid", required=True, help="Complex integer IQ grid JSON {real,imag}")
    parser.add_argument("--ciq_width", type=int, default=9, help="Compressed IQ bit width")
    parser.add_argument("--parameters", help="JSON BFP exponent array for decompression")
    args = parser.parse_args()
    try:
        grid = parse_complex(args.grid)
        if args.operation == "compress":
            result, params = bfp_compress(grid, args.ciq_width)
            payload = {"grid": complex_json(result), "parameters": np.asarray(params).tolist()}
        else:
            if args.parameters is None:
                raise ValueError("decompress requires --parameters")
            result = bfp_decompress(grid, np.asarray(json.loads(args.parameters)))
            payload = {"grid": complex_json(result)}
        print(json.dumps(payload))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
