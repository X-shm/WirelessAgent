"""Cyclic-prefix frequency-offset estimation and waveform correction."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def estimate_frequency_offset(waveform, sample_rate: float, nfft: int, cp_length: int):
    signal = np.asarray(waveform, dtype=complex)
    if signal.ndim == 1:
        signal = signal[:, None]
    if signal.ndim != 2 or sample_rate <= 0 or nfft < 1 or cp_length < 1:
        raise ValueError("waveform must be samples-by-antennas and parameters must be positive")
    if len(signal) < nfft + cp_length:
        raise ValueError("waveform must contain at least nfft+cp_length samples")
    product = signal[:-nfft] * np.conj(signal[nfft:])
    correlations = np.stack([np.convolve(product[:, antenna], np.ones(cp_length), mode="valid") for antenna in range(signal.shape[1])], axis=1)
    timing_index = int(np.argmax(np.sum(np.abs(correlations), axis=1)))
    peak = np.sum(correlations[timing_index])
    frequency = -float(np.angle(peak)) * float(sample_rate) / (2.0 * math.pi * nfft)
    return frequency, correlations, timing_index


def correct_frequency_offset(waveform, sample_rate: float, frequency_offset: float):
    signal = np.asarray(waveform, dtype=complex)
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    phase = np.exp(-1j * 2.0 * math.pi * float(frequency_offset) * np.arange(signal.shape[0]) / sample_rate)
    if signal.ndim > 1:
        phase = phase[:, None]
    return signal * phase


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["estimate", "correct"], required=True)
    parser.add_argument("--waveform", required=True)
    parser.add_argument("--sample_rate", type=float, required=True)
    parser.add_argument("--nfft", type=int)
    parser.add_argument("--cp_length", type=int)
    parser.add_argument("--frequency_offset", type=float)
    args = parser.parse_args()
    try:
        waveform = parse_complex(args.waveform)
        if args.mode == "estimate":
            if args.nfft is None or args.cp_length is None:
                raise ValueError("estimate mode requires nfft and cp_length")
            frequency, correlation, timing = estimate_frequency_offset(waveform, args.sample_rate, args.nfft, args.cp_length)
            result = {"frequency_offset_hz": frequency, "timing_index": timing, "correlation": complex_json(correlation)}
        else:
            if args.frequency_offset is None:
                raise ValueError("correct mode requires frequency_offset")
            result = {"output": complex_json(correct_frequency_offset(waveform, args.sample_rate, args.frequency_offset))}
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
