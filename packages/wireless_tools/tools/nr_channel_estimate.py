"""Standalone sparse LS NR channel estimate with interpolation disabled."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from _complex_io import complex_json, parse_complex


def channel_estimate_sparse(rx_grid: np.ndarray, ref_grid: np.ndarray) -> tuple[np.ndarray, float, dict]:
    rx = np.asarray(rx_grid, dtype=complex)
    ref = np.asarray(ref_grid, dtype=complex)
    if rx.ndim == 2:
        rx = rx[:, :, np.newaxis]
    if rx.ndim != 3 or ref.ndim != 2 or rx.shape[:2] != ref.shape:
        raise ValueError("rx_grid must be NSc x NSym x NRx and ref_grid must be NSc x NSym")
    if rx.shape[0] < 12 or rx.shape[0] % 12 != 0 or rx.shape[1] not in (12, 14):
        raise ValueError("grid must contain a whole number of RBs and one normal/extended CP slot")
    if not np.all(np.isfinite(rx)) or not np.all(np.isfinite(ref)):
        raise ValueError("grid values must be finite")
    pilot_locations = ref != 0
    if not np.any(pilot_locations):
        raise ValueError("ref_grid must contain nonzero reference symbols")
    estimate = np.zeros_like(rx)
    estimate[pilot_locations, :] = rx[pilot_locations, :] / ref[pilot_locations, np.newaxis]
    return estimate, 0.0, {"AveragingWindow": [1, 1]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR sparse LS channel estimate")
    parser.add_argument("--rx_grid", required=True, help="Complex JSON NSc x NSym x NRx grid")
    parser.add_argument("--ref_grid", required=True, help="Complex JSON NSc x NSym reference grid")
    args = parser.parse_args()
    try:
        h, nvar, info = channel_estimate_sparse(parse_complex(args.rx_grid),
                                                 parse_complex(args.ref_grid))
        print(json.dumps({"h": complex_json(h), "shape": list(h.shape),
                          "n_var": nvar, "info": info}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
