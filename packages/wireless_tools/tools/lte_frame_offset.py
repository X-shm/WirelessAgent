"""LTE DL/UL frame or subframe offset from an explicit standard reference waveform."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import parse_complex
from signal_timing_estimate import timing_estimate


def frame_offset(waveform, reference, period_samples: int, reference_offset: int = 0, threshold: float = 0.2, window_length: int = 1):
    if period_samples < 1 or reference_offset < 0:
        raise ValueError("period_samples must be positive and reference_offset nonnegative")
    lag, correlation = timing_estimate(waveform, reference, threshold, window_length)
    if lag is None:
        return None, correlation
    return int((lag-reference_offset) % period_samples), correlation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--link", choices=["downlink", "uplink"], required=True)
    parser.add_argument("--waveform", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--period_samples", type=int, required=True)
    parser.add_argument("--reference_offset", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.2)
    parser.add_argument("--window_length", type=int, default=1)
    args = parser.parse_args()
    try:
        offset, correlation = frame_offset(parse_complex(args.waveform), parse_complex(args.reference), args.period_samples, args.reference_offset, args.threshold, args.window_length)
        print(json.dumps({"link": args.link, "offset": offset, "correlation_peak": float(np.max(correlation)), "normalized_correlation": correlation.tolist()}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
