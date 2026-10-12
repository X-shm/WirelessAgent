"""nr_pss - 5G NR Primary Synchronization Signal.

Implements TS 38.211 Section 7.4.2.2 PSS generation.
MATLAB equivalent: nrPSS(ncellid)
"""
from __future__ import annotations
import argparse
import json
import sys
import numpy as np

# ── PSS m-sequence d_PSS (x^7 + x^4 + 1, length 127) ──
# Generated from the polynomial g(x) = x^7 + x^4 + 1
# Initial state: all ones
# This is the master sequence from TS 38.211 7.4.2.2.1


def _gen_pss_mseq() -> np.ndarray:
    """Generate the base PSS m-sequence of length 127 using x^7 + x^4 + 1.
    Initial state per TS 38.211 7.4.2.2.1: [0,1,1,0,1,1,1]
    """
    state = np.array([0, 1, 1, 0, 1, 1, 1], dtype=np.int8)
    seq = np.zeros(127, dtype=np.int8)
    for i in range(127):
        seq[i] = state[0]
        feedback = state[0] ^ state[4]
        state = np.roll(state, -1)
        state[-1] = feedback
    return seq


# Pre-compute the master sequence
_D_PSS = _gen_pss_mseq()


def pss(ncellid: int) -> np.ndarray:
    """Generate PSS for given physical cell ID.

    Args:
        ncellid: physical cell identity (0..1007)

    Returns:
        127 BPSK symbols (+1/-1) as float64 array
    """
    if ncellid < 0 or ncellid > 1007:
        raise ValueError(f"ncellid must be 0..1007, got {ncellid}")

    n2 = ncellid % 3
    # Cyclic shift: d_PSS((m + 43*n2) mod 127) for m = 0..126
    indices = (np.arange(127) + 43 * n2) % 127
    seq = _D_PSS[indices]

    # BPSK mapping: 0 → +1, 1 → -1
    return np.where(seq == 0, 1.0, -1.0)


def pss_indices(index_base: str = "1based") -> np.ndarray:
    """Get PSS RE indices within SS/PBCH block (240x4 grid).

    Args:
        index_base: '1based' or '0based'

    Returns:
        127 linear indices (column-major within 240x4 grid)
    """
    k = np.arange(56, 183)  # subcarriers 56..182
    symbol = 0
    indices = k + symbol * 240  # linear index in 240x4 grid (column-major)
    if index_base == "1based":
        indices = indices + 1
    return indices.astype(np.uint32)


def main():
    parser = argparse.ArgumentParser(description="5G NR PSS generator (TS 38.211 Sec 7.4.2.2)")
    parser.add_argument("--ncellid", type=int, required=True, help="Physical cell ID (0..1007)")
    args = parser.parse_args()

    try:
        sym = pss(args.ncellid)
        result = {
            "ncellid": args.ncellid,
            "n2": args.ncellid % 3,
            "sym": sym.tolist(),
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
