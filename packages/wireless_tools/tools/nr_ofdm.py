"""NR OFDM Tool — 5G NR OFDM modulate/demodulate (3GPP TS 38.211 §5.3).

Replicates MATLAB nrOFDMModulate / nrOFDMDemodulate from the 5G Toolbox.

Subcarrier k (1-based, k=1 is lowest frequency) maps to 0-based FFT bin
(k - nrb*12/2 - 1) mod nfft, i.e. the active subcarriers are centered on DC.
"""
from __future__ import annotations

import json
import sys
import numpy as np


def _fft_shift_indices(nfft: int, n_sc: int) -> np.ndarray:
    """0-based FFT bins for n_sc active subcarriers centered on DC.

    Probed from MATLAB: sc1 -> bin -n_sc/2, sc(n_sc/2+1) -> bin 0 (DC),
    sc(n_sc) -> bin +n_sc/2-1. For n_sc=12: bins -6,-5,...,-1,0,1,...,+5.
    """
    half = n_sc // 2
    bins = np.arange(-half, half) % nfft
    return bins.astype(int)


def _cp_lengths(nfft: int, n_symbols: int) -> np.ndarray:
    """Normal cyclic prefix lengths for a 14-symbol slot.

    First symbol of each half-slot (indices 0 and 7) uses the long CP.
    For nfft=128 the long CP is 10 and short CP is 9 (matching MATLAB).
    """
    # MATLAB's rule for normal CP at nfft=128: long=10, short=9.
    # General rule (TS 38.211 table 5.3.1-1): long CP = ceil(9*nfft/128) + ...
    # We derive from nfft: short = floor(9*nfft/128), long = short + floor(nfft/128).
    short = 9 * nfft // 128
    long = short + 1
    cp = np.full(n_symbols, short, dtype=int)
    for idx in (0, n_symbols // 2):
        if idx < n_symbols:
            cp[idx] = long
    return cp


def _windowing_samples(nfft: int, n_symbols: int, windowing: int | None) -> int:
    """Resolve the NR OFDM overlap window length.

    MATLAB selects a nonzero EVM-safe default when ``Windowing`` is omitted.
    For the integer-NFFT, normal-CP form supported here, that default scales
    with the FFT length (four samples for the 128-point, 15 kHz reference
    configuration).  Callers can pass zero to request rectangular OFDM.
    """
    if windowing is None:
        windowing = nfft // 32
    windowing = int(windowing)
    if windowing < 0:
        raise ValueError("windowing must be nonnegative")
    if windowing > int(np.min(_cp_lengths(nfft, n_symbols))):
        raise ValueError("windowing must not exceed the shortest cyclic prefix")
    return windowing


def _apply_windowing(symbol_waves: list[np.ndarray], nfft: int, windowing: int) -> np.ndarray:
    """Apply MATLAB-compatible raised-cosine overlap at OFDM boundaries.

    The extra CP samples used for an overlap are the final ``windowing`` IFFT
    samples before the ordinary CP.  In a nominal CP-plus-IFFT symbol they are
    located at indices ``nfft-windowing:nfft``.  The final symbol overlaps the
    first symbol, matching ``nrOFDMModulate`` waveform construction.
    """
    if windowing == 0:
        return np.concatenate(symbol_waves)

    positions = np.arange(windowing, dtype=float)
    falling = 0.5 * (1.0 + np.cos(np.pi * (2.0 * positions + 1.0) / (2.0 * windowing)))
    rising = 1.0 - falling
    windowed = [symbol.copy() for symbol in symbol_waves]
    for index, symbol in enumerate(windowed):
        next_symbol = symbol_waves[(index + 1) % len(symbol_waves)]
        symbol[-windowing:] = (
            falling * symbol[-windowing:]
            + rising * next_symbol[nfft - windowing:nfft]
        )
    return np.concatenate(windowed)


def ofdm_modulate(
    grid: np.ndarray,
    nfft: int,
    scs: float = 15.0,
    windowing: int | None = None,
) -> np.ndarray:
    """Modulate a resource grid (n_sc x n_symbols) to an OFDM waveform.

    grid: complex resource grid, columns are OFDM symbols, rows are subcarriers.
    """
    grid = np.asarray(grid)
    if grid.ndim != 2:
        raise ValueError(f"grid must be 2-D (n_sc x n_symbols), got {grid.shape}")
    n_sc, n_symbols = grid.shape
    bins = _fft_shift_indices(nfft, n_sc)
    cp = _cp_lengths(nfft, n_symbols)
    overlap = _windowing_samples(nfft, n_symbols, windowing)

    symbol_waves = []
    for sym in range(n_symbols):
        # Place subcarriers into FFT bins (centered on DC)
        fd = np.zeros(nfft, dtype=np.complex128)
        fd[bins] = grid[:, sym]
        # numpy ifft already applies 1/N normalization (matches MATLAB).
        td = np.fft.ifft(fd)
        # Cyclic prefix: copy last cp samples to front
        symbol_wave = np.concatenate([td[-cp[sym]:], td])
        symbol_waves.append(symbol_wave)
    return _apply_windowing(symbol_waves, nfft, overlap)


def ofdm_demodulate(
    wave: np.ndarray,
    n_sc: int,
    nfft: int,
    n_symbols: int = 14,
    windowing: int | None = None,
) -> np.ndarray:
    """Demodulate an OFDM waveform back to a resource grid (n_sc x n_symbols)."""
    wave = np.asarray(wave).reshape(-1)
    bins = _fft_shift_indices(nfft, n_sc)
    cp = _cp_lengths(nfft, n_symbols)
    overlap = _windowing_samples(nfft, n_symbols, windowing)

    grid = np.zeros((n_sc, n_symbols), dtype=np.complex128)
    pos = 0
    for sym in range(n_symbols):
        c = cp[sym]
        # Start E samples earlier in the CP to exclude the E overlapped tail
        # samples.  This circularly shifts the useful IFFT output by E.
        symbol_wave = wave[pos + c - overlap: pos + c - overlap + nfft]
        pos += c + nfft
        fd = np.fft.fft(symbol_wave)
        phase_correction = np.exp(1j * 2.0 * np.pi * bins * overlap / nfft)
        grid[:, sym] = fd[bins] * phase_correction
    return grid


def _parse_complex_list(text: str) -> np.ndarray:
    import re
    text = text.strip()
    try:
        return np.array(json.loads(text), dtype=np.complex128)
    except Exception:
        pass
    items = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?\s*[+-]\s*\d*\.?\d+(?:[eE][-+]?\d+)?j', text)
    syms = []
    for it in items:
        it = it.replace(' ', '')
        m = re.match(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)([+-])(\d*\.?\d+(?:[eE][-+]?\d+)?)j', it)
        if m:
            re_v = float(m.group(1)) if m.group(1) not in ('+', '') else 0.0
            im_s = 1 if m.group(2) == '+' else -1
            im_v = float(m.group(3)) * im_s
            syms.append(complex(re_v, im_v))
    return np.array(syms, dtype=np.complex128)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NR OFDM tool")
    parser.add_argument('--nfft', type=int, required=True)
    parser.add_argument('--nsc', type=int, help="number of active subcarriers")
    parser.add_argument('--nrb', type=int, help="number of RBs (1 RB = 12 subcarriers)")
    parser.add_argument('--grid', help="JSON array of complex grid symbols (row-major)")
    parser.add_argument('--inverse', action='store_true', help="demodulate")
    parser.add_argument('--wave', help="JSON array of complex waveform samples")
    parser.add_argument('--nsym', type=int, default=14)
    parser.add_argument('--windowing', type=int, default=None,
                        help="raised-cosine overlap samples; default follows the MATLAB-compatible auto value, 0 disables it")
    args = parser.parse_args()

    nsc = args.nsc or (args.nrb * 12 if args.nrb else None)
    if not nsc:
        parser.error("need --nsc or --nrb")

    if args.inverse:
        wave = _parse_complex_list(args.wave)
        grid = ofdm_demodulate(wave, nsc, args.nfft, args.nsym, args.windowing)
        print(json.dumps({"grid_real": grid.real.tolist(), "grid_imag": grid.imag.tolist()}))
    else:
        grid = _parse_complex_list(args.grid)
        grid = grid.reshape(nsc, -1)
        wave = ofdm_modulate(grid, args.nfft, windowing=args.windowing)
        print(json.dumps({"wave_real": wave.real.tolist(), "wave_imag": wave.imag.tolist(),
                          "wave_len": len(wave)}))


if __name__ == '__main__':
    main()
