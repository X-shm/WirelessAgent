"""LTE PUSCH transport-data scrambling and soft descrambling."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from lte_prbs import lte_prbs


def scrambling_sequence(length: int, nsubframe: int, ncellid: int, rnti: int, codeword: int = 0):
    if length < 0 or not 0 <= nsubframe <= 9 or not 0 <= ncellid <= 503 or not 0 <= rnti <= 65535 or codeword not in (0, 1):
        raise ValueError("invalid length, subframe, cell ID, RNTI or codeword")
    cinit = (int(rnti) << 14) + (int(codeword) << 13) + (int(nsubframe) << 9) + int(ncellid)
    return lte_prbs(cinit, length), cinit


def scramble(bits, nsubframe, ncellid, rnti, codeword=0):
    data = np.asarray(bits, dtype=int).reshape(-1)
    if np.any((data != 0) & (data != 1)):
        raise ValueError("transport-data scramble mode accepts binary bits only")
    sequence, cinit = scrambling_sequence(len(data), nsubframe, ncellid, rnti, codeword)
    return data ^ sequence, cinit


def descramble_soft(values, nsubframe, ncellid, rnti, codeword=0):
    data = np.asarray(values, dtype=float).reshape(-1)
    sequence, cinit = scrambling_sequence(len(data), nsubframe, ncellid, rnti, codeword)
    return data * (1 - 2*sequence), cinit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["scramble", "descramble_soft", "sequence"], required=True)
    parser.add_argument("--values", required=True)
    parser.add_argument("--nsubframe", type=int, required=True)
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--rnti", type=int, required=True)
    parser.add_argument("--codeword", type=int, choices=[0, 1], default=0)
    args = parser.parse_args()
    try:
        values = json.loads(args.values)
        if args.mode == "scramble":
            output, cinit = scramble(values, args.nsubframe, args.ncellid, args.rnti, args.codeword)
        elif args.mode == "descramble_soft":
            output, cinit = descramble_soft(values, args.nsubframe, args.ncellid, args.rnti, args.codeword)
        else:
            output, cinit = scrambling_sequence(len(values), args.nsubframe, args.ncellid, args.rnti, args.codeword)
        print(json.dumps({"output": output.tolist(), "cinit": cinit}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
