"""Pure-Python counterpart of Communications Toolbox awgn."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def _complex_array(value):
    if isinstance(value, dict):
        return np.asarray(value["real"], dtype=float) + 1j * np.asarray(value["imag"], dtype=float)
    return np.asarray(value, dtype=float)


def add_awgn(signal, snr, signal_power=0.0, power_type="db", seed=None):
    x = _complex_array(signal)
    if x.size == 0:
        raise ValueError("signal must not be empty")
    power_type = power_type.lower()
    if power_type not in ("db", "linear"):
        raise ValueError("power_type must be db or linear")
    if isinstance(signal_power, str):
        if signal_power.lower() != "measured":
            raise ValueError("signal_power string must be measured")
        signal_watts = float(np.mean(np.abs(x) ** 2))
    else:
        signal_watts = 10.0 ** (float(signal_power) / 10.0) if power_type == "db" else float(signal_power)
    snr_linear = 10.0 ** (float(snr) / 10.0) if power_type == "db" else float(snr)
    if signal_watts < 0 or snr_linear <= 0:
        raise ValueError("signal power must be nonnegative and SNR must be positive")
    variance = signal_watts / snr_linear
    rng = np.random.default_rng(seed)
    if np.iscomplexobj(x):
        noise = np.sqrt(variance / 2.0) * (rng.standard_normal(x.shape) + 1j * rng.standard_normal(x.shape))
    else:
        noise = np.sqrt(variance) * rng.standard_normal(x.shape)
    return x + noise, float(variance)


def main():
    parser = argparse.ArgumentParser(description="Add white Gaussian noise")
    parser.add_argument("--signal", help='JSON array or {"real":...,"imag":...}')
    parser.add_argument("--signal_file", help="JSON file containing signal")
    parser.add_argument("--snr", type=float, required=True)
    parser.add_argument("--signal_power", default="0", help="numeric power or measured")
    parser.add_argument("--power_type", choices=("db", "linear"), default="db")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    try:
        if bool(args.signal) == bool(args.signal_file):
            raise ValueError("provide exactly one of --signal or --signal_file")
        raw = json.loads(Path(args.signal_file).read_text(encoding="utf-8")) if args.signal_file else json.loads(args.signal)
        power = args.signal_power if args.signal_power.lower() == "measured" else float(args.signal_power)
        y, variance = add_awgn(raw, args.snr, power, args.power_type, args.seed)
        print(json.dumps({"signal_real": np.real(y).tolist(), "signal_imag": np.imag(y).tolist(), "noise_variance": variance}))
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
