"""OFDM frequency response from sampled path gains and path filters."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def channel_response(path_gains, path_filters, nfft, cp_length, active_subcarriers=None, timing_offset=0):
    gains = np.asarray(path_gains, dtype=complex)
    filters = np.asarray(path_filters, dtype=float)
    if gains.ndim == 2:
        gains = gains[:, :, None, None]
    elif gains.ndim == 3:
        gains = gains[:, :, :, None]
    nfft, cp_length, timing_offset = int(nfft), int(cp_length), int(timing_offset)
    if gains.ndim != 4 or filters.ndim != 2 or gains.shape[1] != filters.shape[0]:
        raise ValueError("path_gains must be [Ns,Np,Nt,Nr] and path_filters [Np,Nh]")
    if nfft < 1 or not 0 <= cp_length <= nfft or timing_offset < 0:
        raise ValueError("invalid FFT, cyclic prefix or timing offset")
    symbol_length = nfft+cp_length
    nsymbols = (len(gains)-timing_offset)//symbol_length
    if nsymbols < 1:
        raise ValueError("path_gains contains fewer than one complete OFDM symbol")
    active = np.arange(nfft, dtype=int) if active_subcarriers is None else np.asarray(active_subcarriers, dtype=int)
    if np.any(active < 0) or np.any(active >= nfft):
        raise ValueError("active_subcarriers uses zero-based indices within the FFT")
    output = np.zeros((len(active), nsymbols, gains.shape[2], gains.shape[3]), complex)
    for symbol in range(nsymbols):
        start = timing_offset+symbol*symbol_length+cp_length
        averaged = np.mean(gains[start:start+nfft], axis=0)
        taps = np.einsum("ptr,ph->htr", averaged, filters)
        response = np.fft.fft(taps, nfft, axis=0)
        phase = np.exp(1j*2*np.pi*np.arange(nfft)*timing_offset/nfft)[:, None, None]
        output[:, symbol] = (response*phase)[active]
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_gains", required=True)
    parser.add_argument("--path_filters", required=True)
    parser.add_argument("--nfft", type=int, required=True)
    parser.add_argument("--cp_length", type=int, required=True)
    parser.add_argument("--active_subcarriers")
    parser.add_argument("--timing_offset", type=int, default=0)
    args = parser.parse_args()
    try:
        active = None if args.active_subcarriers is None else json.loads(args.active_subcarriers)
        response = channel_response(parse_complex(args.path_gains), json.loads(args.path_filters), args.nfft, args.cp_length, active, args.timing_offset)
        print(json.dumps({"channel_response": complex_json(response), "shape": list(response.shape), "index_base": 0}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
