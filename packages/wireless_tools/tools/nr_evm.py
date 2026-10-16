"""Direct-grid NR EVM measurement in Python (nrEVM(eqGrid,refGrid))."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def measure_evm(eq_grid: np.ndarray, ref_grid: np.ndarray) -> tuple[float, float, np.ndarray]:
    eq = np.asarray(eq_grid, dtype=np.complex128)
    ref = np.asarray(ref_grid, dtype=np.complex128)
    if eq.shape != ref.shape or eq.size == 0:
        raise ValueError("equalized and reference grids must have the same nonempty shape")
    active = ref != 0
    if not np.any(active):
        raise ValueError("reference grid must contain a nonzero symbol")
    norm = np.sqrt(np.mean(np.abs(ref[active]) ** 2))
    error = np.zeros(eq.shape, dtype=np.complex128)
    error[active] = (eq[active] - ref[active]) / norm
    magnitudes = np.abs(error[active])
    rms = float(np.sqrt(np.mean(magnitudes ** 2)))
    peak = float(np.max(magnitudes))
    return rms, peak, error


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR EVM from equalized and reference grids")
    parser.add_argument("--eq_grid", required=True, help="Equalized complex grid JSON {real,imag}")
    parser.add_argument("--ref_grid", required=True, help="Reference complex grid JSON {real,imag}")
    args = parser.parse_args()
    try:
        rms, peak, error = measure_evm(parse_complex(args.eq_grid), parse_complex(args.ref_grid))
        print(json.dumps({"rms_evm": rms, "peak_evm": peak, "error_vector_grid": complex_json(error)}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
