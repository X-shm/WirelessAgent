"""SNR-mode conversion matching Communications Toolbox convertSNR formulas."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


MODES = ("ebno", "esno", "snr", "snrsc")


def convert_snr(x, input_mode, output_mode="snr", bits_per_symbol=1, coding_rate=1.0,
                samples_per_symbol=1, fft_length=64, num_active_subcarriers=64):
    values = np.asarray(x, dtype=float)
    i = input_mode.lower()
    o = output_mode.lower()
    if i not in MODES or o not in MODES:
        raise ValueError(f"modes must be one of {MODES}")
    bps, rate, sps = float(bits_per_symbol), float(coding_rate), float(samples_per_symbol)
    nfft, nsc = int(fft_length), int(num_active_subcarriers)
    if bps <= 0 or not 0 < rate <= 1 or sps <= 0 or nfft <= 0 or not 0 < nsc <= nfft:
        raise ValueError("invalid conversion parameters")
    if i == o:
        return values.copy()
    if "snrsc" in (i, o):
        if {i, o} != {"snr", "snrsc"}:
            raise ValueError(f"conversion {i} -> {o} is not supported")
        delta = 10 * np.log10(nsc / nfft)
        return values + delta if i == "snrsc" else values - delta
    # Convert through Es/No; all quantities are dB.
    if i == "ebno":
        esno = values + 10 * np.log10(bps * rate)
    elif i == "snr":
        esno = values + 10 * np.log10(sps)
    else:
        esno = values
    if o == "ebno":
        return esno - 10 * np.log10(bps * rate)
    if o == "snr":
        return esno - 10 * np.log10(sps)
    return esno


def main():
    parser = argparse.ArgumentParser(description="Convert SNR representations")
    parser.add_argument("--x", required=True, help="comma-separated dB values")
    parser.add_argument("--input_mode", required=True, choices=MODES)
    parser.add_argument("--output_mode", default="snr", choices=MODES)
    parser.add_argument("--bits_per_symbol", type=float, default=1)
    parser.add_argument("--coding_rate", type=float, default=1.0)
    parser.add_argument("--samples_per_symbol", type=float, default=1)
    parser.add_argument("--fft_length", type=int, default=64)
    parser.add_argument("--num_active_subcarriers", type=int, default=64)
    args = parser.parse_args()
    try:
        values = [float(v) for v in args.x.split(",")]
        out = convert_snr(values, args.input_mode, args.output_mode, args.bits_per_symbol,
                          args.coding_rate, args.samples_per_symbol, args.fft_length,
                          args.num_active_subcarriers)
        result = out.tolist()
        print(json.dumps({"input_mode": args.input_mode, "output_mode": args.output_mode,
                          "values_db": result[0] if len(result) == 1 else result}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
