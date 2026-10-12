"""nr_sss - 5G NR Secondary Synchronization Signal.

Implements TS 38.211 Section 7.4.2.3 SSS generation.
MATLAB equivalent: nrSSS(ncellid)
"""
from __future__ import annotations
import argparse
import json
import sys
import numpy as np

# SSS base sequences — hardcoded from MATLAB nrSSS.m (d_SSS0 and d_SSS1)
# These are pre-computed m-sequence BPSK symbols (±1), length 127 each
_D_SSS0 = np.array([
    -1,  1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1,  1, -1, -1,  1, -1,
     1,  1, -1, -1, -1, -1,  1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1,
    -1, -1, -1, -1,  1,  1,  1, -1, -1, -1,  1, -1, -1,  1,  1,  1, -1,
     1, -1,  1,  1, -1,  1, -1, -1, -1, -1, -1,  1, -1,  1, -1,  1, -1,
     1,  1,  1,  1, -1,  1, -1, -1,  1, -1, -1, -1, -1,  1,  1, -1, -1,
    -1,  1,  1, -1,  1, -1,  1, -1, -1,  1,  1, -1, -1,  1,  1,  1,  1,
     1, -1, -1,  1, -1, -1,  1, -1,  1, -1, -1, -1,  1, -1,  1,  1,  1,
    -1, -1,  1,  1, -1,  1,  1,  1,
], dtype=np.float64)

_D_SSS1 = np.array([
    -1,  1,  1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1,  1,
     1,  1, -1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1,  1, -1,  1,  1,
     1, -1,  1, -1, -1,  1,  1, -1, -1, -1,  1, -1,  1, -1,  1,  1, -1,
    -1, -1, -1, -1,  1, -1,  1,  1,  1,  1, -1, -1, -1,  1,  1,  1, -1,
     1,  1, -1,  1,  1, -1, -1,  1, -1, -1,  1, -1,  1, -1, -1,  1, -1,
    -1, -1, -1,  1, -1, -1,  1,  1,  1, -1, -1,  1, -1,  1,  1, -1,  1,
    -1, -1, -1,  1, -1, -1, -1,  1,  1, -1, -1,  1,  1, -1,  1, -1,  1,
    -1,  1, -1, -1, -1, -1, -1, -1,
], dtype=np.float64)


def sss(ncellid: int) -> np.ndarray:
    """Generate SSS for given physical cell ID.

    Args:
        ncellid: physical cell identity (0..1007)

    Returns:
        127 BPSK symbols (+1/-1) as float64 array
    """
    if ncellid < 0 or ncellid > 1007:
        raise ValueError(f"ncellid must be 0..1007, got {ncellid}")

    n1 = ncellid // 3
    n2 = ncellid % 3

    m0 = 15 * (n1 // 112) + 5 * n2
    m1 = n1 % 112

    indices = np.arange(127)
    seq0 = _D_SSS0[(m0 + indices) % 127]
    seq1 = _D_SSS1[(m1 + indices) % 127]

    return seq0 * seq1


def sss_indices(index_base: str = "1based") -> np.ndarray:
    """Get SSS RE indices within SS/PBCH block (240x4 grid).

    Args:
        index_base: '1based' or '0based'

    Returns:
        127 linear indices (column-major within 240x4 grid)
    """
    k = np.arange(56, 183)  # subcarriers 56..182
    symbol = 2
    indices = k + symbol * 240  # linear index in 240x4 grid
    if index_base == "1based":
        indices = indices + 1
    return indices.astype(np.uint32)


def main():
    parser = argparse.ArgumentParser(description="5G NR SSS generator (TS 38.211 Sec 7.4.2.3)")
    parser.add_argument("--ncellid", type=int, required=True, help="Physical cell ID (0..1007)")
    args = parser.parse_args()

    try:
        sym = sss(args.ncellid)
        result = {
            "ncellid": args.ncellid,
            "n1": args.ncellid // 3,
            "n2": args.ncellid % 3,
            "m0": 15 * (args.ncellid // 3 // 112) + 5 * (args.ncellid % 3),
            "m1": (args.ncellid // 3) % 112,
            "sym": sym.tolist(),
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
