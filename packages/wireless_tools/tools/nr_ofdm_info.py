"""Standalone 5G NR OFDM geometry for an explicit window size."""
from __future__ import annotations

import argparse
import json
import math
import sys


def ofdm_info(nrb: int, scs: int, nfft: int | None = None,
              cyclic_prefix: str = "normal", windowing: int = 0) -> dict:
    if not 1 <= nrb <= 275 or scs not in (15, 30, 60, 120, 240, 480, 960):
        raise ValueError("nrb must be 1..275 and scs must be a supported NR spacing")
    if cyclic_prefix not in ("normal", "extended") or (cyclic_prefix == "extended" and scs != 60):
        raise ValueError("extended cyclic prefix requires 60 kHz SCS")
    if nfft is None:
        minimum = max(128, math.ceil(12 * nrb / 0.85))
        nfft = 1 << (minimum - 1).bit_length()
    if nfft < 128 or 12 * nrb > nfft:
        raise ValueError("nfft must be at least 128 and fit all active subcarriers")
    slots_per_subframe = scs // 15
    symbols_per_slot = 12 if cyclic_prefix == "extended" else 14
    count = symbols_per_slot * slots_per_subframe
    if cyclic_prefix == "extended":
        if nfft % 4:
            raise ValueError("extended CP requires nfft divisible by 4")
        cp = [nfft // 4] * count
    else:
        if nfft % 128:
            raise ValueError("normal CP requires nfft divisible by 128")
        short = 9 * nfft // 128
        cp = [short] * count
        extra = nfft * slots_per_subframe // 128
        cp[0] += extra
        cp[count // 2] += extra
    if not 0 <= windowing <= min(cp):
        raise ValueError("windowing must be between 0 and the shortest cyclic prefix")
    return {
        "Nfft": nfft,
        "SampleRate": nfft * scs * 1000,
        "CyclicPrefixLengths": cp,
        "SymbolLengths": [nfft + length for length in cp],
        "Windowing": windowing,
        "SymbolPhases": [0.0] * count,
        "SymbolsPerSlot": symbols_per_slot,
        "SlotsPerSubframe": slots_per_subframe,
        "SlotsPerFrame": 10 * slots_per_subframe,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR OFDM geometry and CP lengths")
    parser.add_argument("--nrb", type=int, required=True)
    parser.add_argument("--scs", type=int, required=True)
    parser.add_argument("--nfft", type=int)
    parser.add_argument("--cyclic_prefix", choices=("normal", "extended"), default="normal")
    parser.add_argument("--windowing", type=int, required=True, help="Explicit overlap window, 0 for rectangular")
    args = parser.parse_args()
    try:
        print(json.dumps(ofdm_info(args.nrb, args.scs, args.nfft, args.cyclic_prefix, args.windowing)))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
