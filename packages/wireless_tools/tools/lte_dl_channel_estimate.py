"""LTE downlink CRS-based least-squares channel estimation."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex
from lte_cell_rs import cell_rs


def _interpolate(shape, indices, estimates):
    nsc, nsym = shape
    grid = np.full((nsc, nsym), np.nan + 1j*np.nan, complex)
    for symbol in np.unique(indices[:, 1]):
        mask = indices[:, 1] == symbol
        carriers = indices[mask, 0]
        order = np.argsort(carriers)
        carriers, values = carriers[order], estimates[mask][order]
        grid[:, symbol] = np.interp(np.arange(nsc), carriers, values.real) + 1j*np.interp(np.arange(nsc), carriers, values.imag)
    known = np.flatnonzero(np.any(np.isfinite(grid.real), axis=0))
    for carrier in range(nsc):
        values = grid[carrier, known]
        grid[carrier] = np.interp(np.arange(nsym), known, values.real) + 1j*np.interp(np.arange(nsym), known, values.imag)
    return grid


def dl_channel_estimate(received_grid, nrb, ncellid, nsubframe=0, cyclic_prefix="Normal", ports=(0,), smoothing=1):
    received = np.asarray(received_grid, dtype=complex)
    if received.ndim == 2:
        received = received[:, :, None]
    expected_symbols = 14 if cyclic_prefix.lower() == "normal" else 12
    if received.ndim != 3 or received.shape[:2] != (12*int(nrb), expected_symbols) or smoothing < 1:
        raise ValueError("received_grid must be 12*nrb by 14/12 symbols by receive antennas")
    references = cell_rs(nrb, ncellid, nsubframe, cyclic_prefix, ports)
    estimate = np.zeros((received.shape[0], received.shape[1], received.shape[2], len(ports)), complex)
    residual_powers = []
    for port_index, port in enumerate(ports):
        indices = references[int(port)]["indices"][:, :2]
        symbols = references[int(port)]["symbols"]
        for rx in range(received.shape[2]):
            ls = received[indices[:, 0], indices[:, 1], rx] / symbols
            if smoothing > 1:
                smoothed = ls.copy()
                for symbol in np.unique(indices[:, 1]):
                    mask = indices[:, 1] == symbol
                    values = ls[mask]
                    kernel = np.ones(smoothing)/smoothing
                    smoothed[mask] = np.convolve(values.real, kernel, mode="same") + 1j*np.convolve(values.imag, kernel, mode="same")
                ls = smoothed
            estimate[:, :, rx, port_index] = _interpolate(received.shape[:2], indices, ls)
            predicted = symbols * estimate[indices[:, 0], indices[:, 1], rx, port_index]
            residual_powers.extend(np.abs(received[indices[:, 0], indices[:, 1], rx] - predicted) ** 2)
    noise = float(np.mean(residual_powers)) if residual_powers else 0.0
    return estimate, noise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--received_grid", required=True)
    parser.add_argument("--nrb", type=int, required=True)
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--nsubframe", type=int, default=0)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--ports", default="0")
    parser.add_argument("--smoothing", type=int, default=1)
    args = parser.parse_args()
    try:
        ports = [int(value) for value in args.ports.split(",") if value.strip()]
        estimate, noise = dl_channel_estimate(parse_complex(args.received_grid), args.nrb, args.ncellid, args.nsubframe, args.cyclic_prefix, ports, args.smoothing)
        print(json.dumps({"channel_estimate": complex_json(estimate), "noise_variance": noise, "ports": ports}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
