"""LTE Gold-sequence PRBS from 3GPP TS 36.211 section 7.2."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


NC = 1600
MAX_CINIT = 2**31 - 1


def lte_prbs(cinit, length, start=0, mapping="binary"):
    cinit, length, start = int(cinit), int(length), int(start)
    if not 0 <= cinit <= MAX_CINIT:
        raise ValueError(f"cinit must be in 0..{MAX_CINIT}")
    if length < 0 or start < 0:
        raise ValueError("length and start must be nonnegative")
    total = NC + start + length + 31
    x1 = np.zeros(total, dtype=np.uint8)
    x2 = np.zeros(total, dtype=np.uint8)
    x1[0] = 1
    for bit in range(31):
        x2[bit] = (cinit >> bit) & 1
    for n in range(total - 31):
        x1[n + 31] = x1[n + 3] ^ x1[n]
        x2[n + 31] = x2[n + 3] ^ x2[n + 2] ^ x2[n + 1] ^ x2[n]
    seq = x1[NC + start:NC + start + length] ^ x2[NC + start:NC + start + length]
    mapping = mapping.lower()
    if mapping == "binary":
        return seq.astype(np.int64)
    if mapping == "signed":
        return (1 - 2 * seq.astype(np.int64))
    raise ValueError("mapping must be binary or signed")


def main():
    parser = argparse.ArgumentParser(description="Generate LTE PRBS")
    parser.add_argument("--cinit", type=int, required=True)
    parser.add_argument("--length", type=int, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--mapping", choices=("binary", "signed"), default="binary")
    args = parser.parse_args()
    try:
        seq = lte_prbs(args.cinit, args.length, args.start, args.mapping)
        print(json.dumps({"cinit": args.cinit, "start": args.start, "length": args.length,
                          "mapping": args.mapping, "sequence": seq.tolist()}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
