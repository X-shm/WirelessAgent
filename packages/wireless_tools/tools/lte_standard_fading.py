"""LTE EPA/EVA/ETU tapped-delay profiles and reproducible fading application."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


_PROFILES = {
    "EPA": ([0, 30, 70, 90, 110, 190, 410], [0, -1, -2, -3, -8, -17.2, -20.8]),
    "EVA": ([0, 30, 150, 310, 370, 710, 1090, 1730, 2510], [0, -1.5, -1.4, -3.6, -0.6, -9.1, -7, -12, -16.9]),
    "ETU": ([0, 50, 120, 200, 230, 500, 1600, 2300, 5000], [-1, -1, -1, 0, 0, 0, -3, -5, -7]),
}


def channel_profile(name):
    key = name.upper()
    if key not in _PROFILES:
        raise ValueError("profile must be EPA, EVA or ETU")
    delays, gains = _PROFILES[key]
    powers = 10**(np.asarray(gains)/10.0)
    powers /= np.sum(powers)
    return {"profile": key, "delays_ns": delays, "average_path_gains_db": gains, "normalized_path_powers": powers.tolist()}


def apply_fading(waveform, sample_rate, profile="EPA", max_doppler=0.0, seed=0):
    signal = np.asarray(waveform, dtype=complex)
    if signal.ndim == 1:
        signal = signal[:, None]
    sample_rate, max_doppler = float(sample_rate), float(max_doppler)
    if signal.ndim != 2 or sample_rate <= 0 or max_doppler < 0:
        raise ValueError("waveform must be [samples,channels], sample_rate positive and Doppler nonnegative")
    info = channel_profile(profile)
    delays = np.asarray(info["delays_ns"])*1e-9*sample_rate
    powers = np.asarray(info["normalized_path_powers"])
    rng = np.random.default_rng(seed)
    gains = np.empty((len(signal), len(delays)), complex)
    initial = (rng.normal(size=len(delays))+1j*rng.normal(size=len(delays)))*np.sqrt(powers/2)
    gains[0] = initial
    rho = math.exp(-math.sqrt(2)*math.pi*max_doppler/sample_rate) if max_doppler else 1.0
    for sample in range(1, len(signal)):
        if rho == 1.0:
            gains[sample] = gains[0]
        else:
            innovation = (rng.normal(size=len(delays))+1j*rng.normal(size=len(delays)))*np.sqrt(powers/2)
            gains[sample] = rho*gains[sample-1]+math.sqrt(1-rho*rho)*innovation
    output = np.zeros_like(signal)
    for path, delay in enumerate(delays):
        lower, fraction = int(math.floor(delay)), float(delay-math.floor(delay))
        for sample in range(lower, len(signal)):
            source = (1-fraction)*signal[sample-lower]
            if fraction and sample-lower-1 >= 0:
                source += fraction*signal[sample-lower-1]
            output[sample] += gains[sample, path]*source
    return output, gains, info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["profile", "apply"], required=True)
    parser.add_argument("--profile", choices=["EPA", "EVA", "ETU"], default="EPA")
    parser.add_argument("--waveform")
    parser.add_argument("--sample_rate", type=float)
    parser.add_argument("--max_doppler", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    try:
        if args.mode == "profile":
            result = channel_profile(args.profile)
        else:
            if args.waveform is None or args.sample_rate is None:
                raise ValueError("apply mode requires waveform and sample_rate")
            output, gains, info = apply_fading(parse_complex(args.waveform), args.sample_rate, args.profile, args.max_doppler, args.seed)
            result = {"waveform": complex_json(output), "path_gains": complex_json(gains), "info": info}
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
