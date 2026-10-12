"""LTE primary synchronization signal from 3GPP TS 36.211 section 6.11.1."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


ROOTS = (25, 29, 34)


def lte_pss(ncellid, nsubframe=0, duplex_mode="FDD"):
    ncellid, nsubframe = int(ncellid), int(nsubframe)
    duplex = duplex_mode.upper()
    if not 0 <= ncellid <= 503:
        raise ValueError("ncellid must be in 0..503")
    if not 0 <= nsubframe <= 9:
        raise ValueError("nsubframe must be in 0..9")
    if duplex not in ("FDD", "TDD"):
        raise ValueError("duplex_mode must be FDD or TDD")
    valid = (0, 5) if duplex == "FDD" else (1, 6)
    if nsubframe not in valid:
        return np.zeros(0, dtype=np.complex128)
    u = ROOTS[ncellid % 3]
    n1 = np.arange(31, dtype=float)
    n2 = np.arange(31, 62, dtype=float)
    return np.concatenate([
        np.exp(-1j * np.pi * u * n1 * (n1 + 1) / 63),
        np.exp(-1j * np.pi * u * (n2 + 1) * (n2 + 2) / 63),
    ])


def main():
    parser = argparse.ArgumentParser(description="Generate LTE PSS")
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--nsubframe", type=int, default=0)
    parser.add_argument("--duplex_mode", choices=("FDD", "TDD"), default="FDD")
    args = parser.parse_args()
    try:
        seq = lte_pss(args.ncellid, args.nsubframe, args.duplex_mode)
        print(json.dumps({"ncellid": args.ncellid, "nid2": args.ncellid % 3,
                          "nsubframe": args.nsubframe, "duplex_mode": args.duplex_mode,
                          "symbols_real": seq.real.tolist(), "symbols_imag": seq.imag.tolist()}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
