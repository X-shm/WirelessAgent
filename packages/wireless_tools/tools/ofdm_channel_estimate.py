"""Pilot-aided least-squares OFDM channel estimation with 2-D interpolation."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def channel_estimate(received_grid, pilot_symbols, pilot_indices, smoothing: int = 1):
    received = np.asarray(received_grid, dtype=complex)
    pilots = np.asarray(pilot_symbols, dtype=complex).reshape(-1)
    indices = np.asarray(pilot_indices, dtype=int)
    if received.ndim != 2 or indices.ndim != 2 or indices.shape[1] != 2 or len(indices) != len(pilots):
        raise ValueError("grid must be 2-D; pilot_indices must be N-by-2 and match pilot_symbols")
    if len(pilots) == 0 or np.any(pilots == 0) or smoothing < 1:
        raise ValueError("pilots must be nonempty/nonzero and smoothing positive")
    if np.any(indices < 0) or np.any(indices[:, 0] >= received.shape[0]) or np.any(indices[:, 1] >= received.shape[1]):
        raise ValueError("pilot index outside received grid")
    estimates = received[indices[:, 0], indices[:, 1]] / pilots
    if smoothing > 1:
        kernel = np.ones(smoothing) / smoothing
        smooth_real = np.convolve(estimates.real, kernel, mode="same")
        smooth_imag = np.convolve(estimates.imag, kernel, mode="same")
        estimates = smooth_real + 1j * smooth_imag
    nsc, nsym = received.shape
    grid = np.full((nsc, nsym), np.nan + 1j*np.nan, complex)
    for symbol in range(nsym):
        mask = indices[:, 1] == symbol
        if not np.any(mask):
            continue
        carriers = indices[mask, 0]
        order = np.argsort(carriers)
        carriers = carriers[order]
        values = estimates[mask][order]
        unique, first = np.unique(carriers, return_index=True)
        values = values[first]
        grid[:, symbol] = np.interp(np.arange(nsc), unique, values.real) + 1j*np.interp(np.arange(nsc), unique, values.imag)
    known_symbols = np.flatnonzero(np.any(np.isfinite(grid.real), axis=0))
    if len(known_symbols) == 0:
        raise ValueError("no usable pilot symbols")
    for carrier in range(nsc):
        values = grid[carrier, known_symbols]
        grid[carrier] = np.interp(np.arange(nsym), known_symbols, values.real) + 1j*np.interp(np.arange(nsym), known_symbols, values.imag)
    residual = received[indices[:, 0], indices[:, 1]] - pilots * grid[indices[:, 0], indices[:, 1]]
    noise_variance = float(np.mean(np.abs(residual) ** 2))
    return grid, estimates, noise_variance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--received_grid", required=True)
    parser.add_argument("--pilot_symbols", required=True)
    parser.add_argument("--pilot_indices", required=True)
    parser.add_argument("--smoothing", type=int, default=1)
    args = parser.parse_args()
    try:
        indices = json.loads(args.pilot_indices)
        estimate, pilots, noise = channel_estimate(parse_complex(args.received_grid), parse_complex(args.pilot_symbols), indices, args.smoothing)
        print(json.dumps({"channel_estimate": complex_json(estimate), "pilot_estimates": complex_json(pilots), "noise_variance": noise}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
