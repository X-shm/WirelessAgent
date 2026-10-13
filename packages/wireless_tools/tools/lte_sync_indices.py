"""FDD LTE PSS/SSS resource-element indices."""
from __future__ import annotations
import argparse
import json
import sys


def sync_indices(nrb: int, nsubframe: int = 0, cyclic_prefix: str = "Normal", signal: str = "both", index_base: int = 0):
    nrb, nsubframe = int(nrb), int(nsubframe)
    cp, signal = cyclic_prefix.lower(), signal.lower()
    if not 6 <= nrb <= 110 or not 0 <= nsubframe <= 9 or cp not in ("normal", "extended"):
        raise ValueError("nrb 6..110, nsubframe 0..9 and Normal/Extended CP required")
    if signal not in ("pss", "sss", "both") or index_base not in (0, 1):
        raise ValueError("signal must be pss/sss/both and index_base 0/1")
    if nsubframe not in (0, 5):
        return {"pss": [], "sss": []}
    carriers = list(range(6*nrb-31, 6*nrb+31))
    symbols_per_slot = 7 if cp == "normal" else 6
    pss_symbol = symbols_per_slot - 1
    sss_symbol = pss_symbol - 1
    add = index_base
    return {
        "pss": [[carrier+add, pss_symbol+add, add] for carrier in carriers] if signal in ("pss", "both") else [],
        "sss": [[carrier+add, sss_symbol+add, add] for carrier in carriers] if signal in ("sss", "both") else [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nrb", type=int, required=True)
    parser.add_argument("--nsubframe", type=int, default=0)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--signal", choices=["pss", "sss", "both"], default="both")
    parser.add_argument("--index_base", type=int, choices=[0, 1], default=0)
    args = parser.parse_args()
    try:
        result = sync_indices(args.nrb, args.nsubframe, args.cyclic_prefix, args.signal, args.index_base)
        result["index_base"] = args.index_base
        print(json.dumps(result))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
