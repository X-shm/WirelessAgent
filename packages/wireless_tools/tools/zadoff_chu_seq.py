"""Generate odd-length root Zadoff-Chu sequences."""
from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np


def zadoff_chu_seq(root, length):
    root, length = int(root), int(length)
    if root <= 0 or length <= 0 or length % 2 == 0:
        raise ValueError("root must be positive and length must be positive odd")
    if math.gcd(root, length) != 1:
        raise ValueError("root and length must be relatively prime")
    m = np.arange(length, dtype=float)
    return np.exp(-1j * np.pi * root * m * (m + 1) / length)


def main():
    parser = argparse.ArgumentParser(description="Generate a Zadoff-Chu sequence")
    parser.add_argument("--root", type=int, required=True)
    parser.add_argument("--length", type=int, required=True)
    args = parser.parse_args()
    try:
        seq = zadoff_chu_seq(args.root, args.length)
        print(json.dumps({"root": args.root, "length": args.length,
                          "symbols_real": seq.real.tolist(), "symbols_imag": seq.imag.tolist()}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
