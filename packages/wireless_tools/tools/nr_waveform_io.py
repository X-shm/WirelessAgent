"""Programmatic single-numerology NR OFDM waveform generation and analysis."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import complex_array, run_cli
from nr_ofdm import ofdm_modulate, ofdm_demodulate


def waveform_generator(grid, nfft: int, scs_khz: float = 15.0):
    resource_grid = complex_array(grid)
    if resource_grid.ndim != 2 or resource_grid.shape[0] % 12 or nfft < resource_grid.shape[0]:
        raise ValueError("grid must be [12*nrb, symbols], with nfft >= 12*nrb")
    if scs_khz <= 0:
        raise ValueError("scs_khz must be positive")
    waveform = ofdm_modulate(resource_grid, nfft, scs=scs_khz, windowing=0)
    return {"waveform": waveform, "sample_rate": nfft * scs_khz * 1000,
            "nrb": resource_grid.shape[0] // 12,
            "symbols": resource_grid.shape[1], "nfft": nfft}


def waveform_analyzer(waveform, nfft: int, nrb: int, symbols: int,
                      scs_khz: float = 15.0):
    samples = complex_array(waveform).reshape(-1)
    if nrb < 1 or symbols < 1 or nfft < 12 * nrb or scs_khz <= 0:
        raise ValueError("invalid nfft, nrb, symbols or scs_khz")
    grid = ofdm_demodulate(samples, 12 * nrb, nfft, symbols, windowing=0)
    power = abs(samples) ** 2
    mean_power = float(np.mean(power))
    papr = float(10 * np.log10(np.max(power) / mean_power)) if mean_power else None
    spectrum = np.fft.fftshift(np.fft.fft(samples, nfft))
    return {"grid": grid, "mean_power": mean_power, "papr_db": papr,
            "spectrum_power": abs(spectrum) ** 2,
            "frequency_hz": np.fft.fftshift(np.fft.fftfreq(nfft, 1 / (nfft * scs_khz * 1000)))}


if __name__ == "__main__":
    run_cli("Single-numerology NR OFDM waveform I/O", {
        "nrWaveformGenerator": waveform_generator,
        "nrWaveformAnalyzer": waveform_analyzer,
    })
