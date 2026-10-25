"""Standalone type-1 NR low-PAPR sequence generation (TS 38.211 5.2.2)."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np


PHASES_PATH = Path(__file__).resolve().parents[1] / "references" / "5g_low_papr_phases.json"


def _values(value: int | float | list[int] | list[float], name: str) -> list:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [value]
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a scalar or nonempty JSON array")
    return value


def _largest_prime_below(m: int) -> int:
    for candidate in range(m - 1, 1, -1):
        if all(candidate % divisor for divisor in range(2, math.isqrt(candidate) + 1)):
            return candidate
    raise ValueError("no prime below sequence length")


def low_papr_type1(u: int | list[int], v: int | list[int],
                   alpha: float | list[float], m: int) -> np.ndarray:
    """Return the complex M x NumAlpha x NumU x NumV type-1 array.

    Singleton trailing dimensions are intentionally retained for a stable JSON
    contract.  MATLAB may display those trailing dimensions as a vector/matrix.
    """
    groups, bases, shifts = _values(u, "u"), _values(v, "v"), _values(alpha, "alpha")
    if any(type(x) is not int or not 0 <= x <= 29 for x in groups):
        raise ValueError("u values must be integers in 0..29")
    if any(type(x) is not int or x not in (0, 1) for x in bases):
        raise ValueError("v values must be 0 or 1")
    if any(not isinstance(x, (int, float)) or isinstance(x, bool) or
           not math.isfinite(x) or x < 0 for x in shifts):
        raise ValueError("alpha values must be finite nonnegative numbers")
    if type(m) is not int or m < 0 or (0 < m < 30 and m not in (6, 12, 18, 24)):
        raise ValueError("m must be 0, 6, 12, 18, 24, or at least 30")
    if m < 72 and any(base != 0 for base in bases):
        raise ValueError("v=1 requires m >= 72")
    result = np.empty((m, len(shifts), len(groups), len(bases)), dtype=complex)
    if m == 0:
        return result
    n = np.arange(m, dtype=np.float64)
    short_phases = json.loads(PHASES_PATH.read_text(encoding="utf-8"))[f"m{m}"] if m < 30 else None
    prime = _largest_prime_below(m) if m >= 30 else None
    for group_index, group in enumerate(groups):
        for base_index, base in enumerate(bases):
            if short_phases is not None:
                phase = np.asarray(short_phases[group], dtype=float) * np.pi / 4
            else:
                qbar = prime * (group + 1) / 31
                q = math.floor(qbar + 0.5) + base * (-1) ** math.floor(2 * qbar)
                zc_n = n % prime
                phase = -np.pi * q * zc_n * (zc_n + 1) / prime
            for shift_index, shift in enumerate(shifts):
                result[:, shift_index, group_index, base_index] = np.exp(1j * (phase + shift * n))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR type-1 low-PAPR sequence")
    parser.add_argument("--u", required=True, help="JSON group number or array (0..29)")
    parser.add_argument("--v", required=True, help="JSON base number or array (0/1)")
    parser.add_argument("--alpha", required=True, help="JSON nonnegative phase shift or array")
    parser.add_argument("--m", type=int, required=True, help="Sequence length")
    args = parser.parse_args()
    try:
        sequence = low_papr_type1(json.loads(args.u), json.loads(args.v),
                                   json.loads(args.alpha), args.m)
        print(json.dumps({"seq_real": sequence.real.tolist(),
                          "seq_imag": sequence.imag.tolist(),
                          "shape": list(sequence.shape)}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
