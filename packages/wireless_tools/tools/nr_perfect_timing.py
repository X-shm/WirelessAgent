"""Standalone perfect timing from path gains and path impulse filters."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from _complex_io import parse_complex


def perfect_timing(path_gains: np.ndarray, path_filters: np.ndarray) -> tuple[int, np.ndarray]:
    gains = np.asarray(path_gains, dtype=complex)
    filters = np.asarray(path_filters, dtype=float)
    if gains.ndim != 4 or min(gains.shape) < 1:
        raise ValueError("path_gains must be NCS x NPaths x NTx x NRx")
    if filters.ndim != 2 or filters.shape[1] != gains.shape[1] or filters.shape[0] < 1:
        raise ValueError("path_filters must be NH x NPaths")
    if not np.all(np.isfinite(gains)) or not np.all(np.isfinite(filters)):
        raise ValueError("path gains and filters must be finite")
    impulse = np.einsum("sptr,hp->shtr", gains, filters, optimize=True)
    magnitude = np.abs(impulse.mean(axis=0).sum(axis=1))
    offset = int(np.argmax(magnitude.sum(axis=1)))
    return offset, magnitude


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent perfect NR timing estimate")
    parser.add_argument("--path_gains", required=True, help="Complex JSON NCS x NPaths x NTx x NRx")
    parser.add_argument("--path_filters", required=True, help="JSON NH x NPaths real matrix")
    args = parser.parse_args()
    try:
        offset, magnitude = perfect_timing(parse_complex(args.path_gains),
                                            np.asarray(json.loads(args.path_filters)))
        print(json.dumps({"offset": offset, "magnitude": magnitude.tolist()}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
