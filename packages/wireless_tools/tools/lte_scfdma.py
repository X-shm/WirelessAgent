"""LTE uplink DFT-spread OFDM information, modulation and demodulation."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from _complex_io import complex_json, parse_complex
from lte_ofdm import lte_ofdm_info, modulate as ofdm_modulate, demodulate as ofdm_demodulate


def scfdma_info(nrb, cyclic_prefix="Normal", nfft=None):
    return lte_ofdm_info(nrb, cyclic_prefix, nfft)


def scfdma_modulate(grid, nrb, cyclic_prefix="Normal", nfft=None, windowing=0):
    data = np.asarray(grid, dtype=complex)
    if data.ndim == 2:
        data = data[:, :, None]
    if data.ndim != 3 or data.shape[0] != 12*int(nrb):
        raise ValueError("grid must be 12*nrb by whole-subframe symbols by antennas")
    spread = np.fft.fft(data, axis=0) / math.sqrt(data.shape[0])
    waveform, info = ofdm_modulate(nrb, cyclic_prefix, spread, windowing, nfft)
    half_shift = np.exp(1j*math.pi*np.arange(len(waveform))/info["nfft"])[:, None]
    return waveform*half_shift, info


def scfdma_demodulate(waveform, nrb, cyclic_prefix="Normal", nfft=None, cp_fraction=0.55):
    signal = np.asarray(waveform, dtype=complex)
    if signal.ndim == 1:
        signal = signal[:, None]
    info = lte_ofdm_info(nrb, cyclic_prefix, nfft)
    half_shift = np.exp(-1j*math.pi*np.arange(len(signal))/info["nfft"])[:, None]
    spread = ofdm_demodulate(nrb, cyclic_prefix, signal*half_shift, cp_fraction, nfft)
    return np.fft.ifft(spread, axis=0)*math.sqrt(spread.shape[0]), info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["info", "modulate", "demodulate"], required=True)
    parser.add_argument("--nrb", type=int, required=True)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--nfft", type=int)
    parser.add_argument("--windowing", type=int, default=0)
    parser.add_argument("--cp_fraction", type=float, default=0.55)
    parser.add_argument("--grid")
    parser.add_argument("--waveform")
    args = parser.parse_args()
    try:
        if args.mode == "info":
            result = {"info": scfdma_info(args.nrb, args.cyclic_prefix, args.nfft)}
        elif args.mode == "modulate":
            if args.grid is None:
                raise ValueError("modulate mode requires grid")
            waveform, info = scfdma_modulate(parse_complex(args.grid), args.nrb, args.cyclic_prefix, args.nfft, args.windowing)
            result = {"waveform": complex_json(waveform), "info": info}
        else:
            if args.waveform is None:
                raise ValueError("demodulate mode requires waveform")
            grid, info = scfdma_demodulate(parse_complex(args.waveform), args.nrb, args.cyclic_prefix, args.nfft, args.cp_fraction)
            result = {"grid": complex_json(grid), "info": info}
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
