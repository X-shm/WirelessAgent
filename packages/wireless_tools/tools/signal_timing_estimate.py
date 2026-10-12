"""Reference-correlation timing estimation and perfect channel delay."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def timing_estimate(waveform, reference, threshold: float = 0.2, window_length: int = 1):
    wave = np.asarray(waveform, dtype=complex)
    ref = np.asarray(reference, dtype=complex)
    if wave.ndim == 1:
        wave = wave[:, None]
    if ref.ndim == 1:
        ref = ref[:, None]
    if wave.ndim != 2 or ref.ndim != 2 or len(wave) < len(ref):
        raise ValueError("waveform/reference must be 1-D or 2-D and waveform cannot be shorter")
    if not 0 <= threshold <= 1 or window_length < 1:
        raise ValueError("threshold must be 0..1 and window_length positive")
    total = len(wave) + len(ref) - 1
    correlations = np.zeros((total, wave.shape[1], ref.shape[1]), float)
    lags = np.arange(-(len(ref) - 1), len(wave))
    for rxi in range(wave.shape[1]):
        for txi in range(ref.shape[1]):
            for out_index, lag in enumerate(lags):
                w_start = max(0, lag)
                w_end = min(len(wave), lag + len(ref))
                if w_end <= w_start:
                    continue
                r_start = w_start - lag
                r_end = r_start + (w_end - w_start)
                wpart = wave[w_start:w_end, rxi]
                rpart = ref[r_start:r_end, txi]
                denominator = np.linalg.norm(wpart) * np.linalg.norm(ref[:, txi])
                if denominator:
                    correlations[out_index, rxi, txi] = abs(np.vdot(rpart, wpart)) / denominator
    if float(np.max(correlations)) < threshold:
        return None, correlations
    energy = np.sum(correlations ** 2, axis=(1, 2))
    if window_length > len(energy):
        raise ValueError("window_length is longer than the correlation output")
    if window_length == 1:
        index = int(np.argmax(energy))
    else:
        index = int(np.argmax(np.convolve(energy, np.ones(window_length), mode="valid")))
    return int(lags[index]), correlations


def channel_delay(path_gains, path_filters):
    gains = np.asarray(path_gains, dtype=complex)
    filters = np.asarray(path_filters, dtype=complex)
    if gains.ndim == 1:
        gains = gains[None, :, None, None]
    elif gains.ndim == 2:
        gains = gains[:, :, None, None]
    elif gains.ndim == 3:
        gains = gains[:, :, :, None]
    if gains.ndim != 4 or filters.ndim != 2 or gains.shape[1] != filters.shape[0]:
        raise ValueError("path_gains must be snapshots-by-paths-by-tx-by-rx and filters paths-by-samples")
    average = np.nan_to_num(np.mean(gains, axis=0))
    impulse = np.einsum("ph,ptr->htr", filters, average)
    combined = np.sum(impulse, axis=1)
    magnitude = np.abs(combined)
    delay = int(np.argmax(np.sum(magnitude, axis=1)))
    return delay, magnitude, combined


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["correlation", "perfect_channel"], required=True)
    parser.add_argument("--waveform")
    parser.add_argument("--reference")
    parser.add_argument("--threshold", type=float, default=0.2)
    parser.add_argument("--window_length", type=int, default=1)
    parser.add_argument("--path_gains")
    parser.add_argument("--path_filters")
    args = parser.parse_args()
    try:
        if args.mode == "correlation":
            if args.waveform is None or args.reference is None:
                raise ValueError("correlation mode requires waveform and reference")
            offset, correlation = timing_estimate(parse_complex(args.waveform), parse_complex(args.reference), args.threshold, args.window_length)
            result = {"offset": offset, "normalized_correlation": correlation.tolist(), "peak": float(np.max(correlation))}
        else:
            if args.path_gains is None or args.path_filters is None:
                raise ValueError("perfect_channel mode requires path_gains and path_filters")
            delay, magnitude, impulse = channel_delay(parse_complex(args.path_gains), parse_complex(args.path_filters))
            result = {"delay": delay, "magnitude": magnitude.tolist(), "impulse_response": complex_json(impulse)}
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
