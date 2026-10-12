"""LTE PDSCH scrambling PRBS and initialization."""
from __future__ import annotations
import argparse
import json
import sys

from lte_prbs import lte_prbs


def pdsch_prbs(ncellid, nsubframe, rnti, codeword, length, start=0, mapping="binary"):
    values = [int(value) for value in (ncellid, nsubframe, rnti, codeword, length, start)]
    ncellid, nsubframe, rnti, codeword, length, start = values
    if not 0 <= ncellid <= 503 or not 0 <= nsubframe <= 9 or not 0 <= rnti <= 65535 or codeword not in (0, 1):
        raise ValueError("invalid cell ID, subframe, RNTI or codeword")
    if length < 0 or start < 0 or mapping not in ("binary", "signed"):
        raise ValueError("length/start must be nonnegative and mapping binary/signed")
    cinit = (rnti << 14) + (codeword << 13) + (nsubframe << 9) + ncellid
    sequence = lte_prbs(cinit, start+length)[start:]
    if mapping == "signed":
        sequence = 1-2*sequence.astype(int)
    return sequence, cinit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--nsubframe", type=int, required=True)
    parser.add_argument("--rnti", type=int, required=True)
    parser.add_argument("--codeword", type=int, choices=[0, 1], required=True)
    parser.add_argument("--length", type=int, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--mapping", choices=["binary", "signed"], default="binary")
    args = parser.parse_args()
    try:
        sequence, cinit = pdsch_prbs(args.ncellid, args.nsubframe, args.rnti, args.codeword, args.length, args.start, args.mapping)
        print(json.dumps({"sequence": sequence.tolist(), "cinit": cinit, "start": args.start}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
