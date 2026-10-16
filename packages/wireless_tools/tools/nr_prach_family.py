"""Standalone single-occasion PRACH Zadoff-Chu processing subsets."""
from __future__ import annotations

import math
import numpy as np

from _nr_remaining_common import complex_array, run_cli


def _length(sequence_length: int):
    if sequence_length not in (139, 839):
        raise ValueError("sequence_length must be 139 (short) or 839 (long)")


def prach(root: int, sequence_length: int = 839, cyclic_shift: int = 0):
    _length(sequence_length)
    if not 1 <= root < sequence_length or math.gcd(root, sequence_length) != 1:
        raise ValueError("root must be coprime with sequence_length")
    if not 0 <= cyclic_shift < sequence_length:
        raise ValueError("cyclic_shift is out of range")
    n = np.arange(sequence_length)
    sequence = np.exp(-1j * np.pi * root * n * (n + 1) / sequence_length)
    return {"symbols": np.roll(sequence, cyclic_shift),
            "sequence_length": sequence_length, "root": root}


def prach_indices(sequence_length: int = 839, subcarrier_offset: int = 0,
                  nsc: int | None = None, index_base: int = 1):
    _length(sequence_length)
    if nsc is None:
        nsc = sequence_length
    if not 0 <= subcarrier_offset or subcarrier_offset + sequence_length > nsc:
        raise ValueError("PRACH allocation exceeds grid")
    if index_base not in (0, 1):
        raise ValueError("index_base must be 0 or 1")
    return {"indices": np.arange(subcarrier_offset + index_base,
                                  subcarrier_offset + sequence_length + index_base),
            "n_re": sequence_length}


def prach_grid(sequence_length: int = 839, nsc: int | None = None,
               symbols=None, subcarrier_offset: int = 0):
    _length(sequence_length)
    if nsc is None:
        nsc = sequence_length
    if nsc < sequence_length or not 0 <= subcarrier_offset <= nsc - sequence_length:
        raise ValueError("invalid nsc or subcarrier_offset")
    grid = np.zeros(nsc, dtype=complex)
    if symbols is not None:
        values = complex_array(symbols).reshape(-1)
        if len(values) != sequence_length:
            raise ValueError("symbols must contain sequence_length elements")
        grid[subcarrier_offset:subcarrier_offset + sequence_length] = values
    return {"grid": grid}


def prach_ofdm_info(sequence_length: int = 839, nfft: int | None = None,
                    subcarrier_spacing_hz: float | None = None, cp_samples: int = 0):
    _length(sequence_length)
    if nfft is None:
        nfft = 1024 if sequence_length == 839 else 256
    if subcarrier_spacing_hz is None:
        subcarrier_spacing_hz = 1250.0 if sequence_length == 839 else 15000.0
    if nfft < sequence_length or subcarrier_spacing_hz <= 0 or not 0 <= cp_samples <= nfft:
        raise ValueError("invalid OFDM size, spacing, or cyclic prefix")
    return {"nfft": nfft, "sample_rate": nfft * subcarrier_spacing_hz,
            "subcarrier_spacing_hz": subcarrier_spacing_hz,
            "cp_samples": cp_samples, "symbol_samples": nfft + cp_samples}


def prach_ofdm_modulate(symbols, nfft: int = 1024, cp_samples: int = 0):
    values = complex_array(symbols).reshape(-1)
    if len(values) not in (139, 839) or nfft < len(values) or not 0 <= cp_samples <= nfft:
        raise ValueError("symbols must have length 139/839 and fit nfft")
    spectrum = np.zeros(nfft, dtype=complex)
    bins = (np.arange(len(values)) - len(values) // 2) % nfft
    spectrum[bins] = values
    time = np.fft.ifft(spectrum) * np.sqrt(nfft)
    if cp_samples:
        time = np.r_[time[-cp_samples:], time]
    return {"waveform": time}


def prach_detect(received, root: int, sequence_length: int = 839,
                 threshold: float = 0.5):
    """Circular matched-filter detection on a synchronized frequency grid."""
    rx = complex_array(received).reshape(-1)
    if len(rx) != sequence_length or not 0 <= threshold <= 1:
        raise ValueError("received must contain one sequence and threshold must be 0..1")
    reference = prach(root, sequence_length)["symbols"]
    correlations = np.fft.ifft(np.fft.fft(rx) * np.conj(np.fft.fft(reference)))
    peak = int(np.argmax(abs(correlations)))
    normalized = min(1.0, float(abs(correlations[peak]) /
                                (np.linalg.norm(rx) * np.linalg.norm(reference) + 1e-15)))
    return {"detected": normalized >= threshold, "cyclic_shift": peak,
            "normalized_peak": normalized}


if __name__ == "__main__":
    run_cli("Standalone single-occasion NR PRACH processing", {
        "nrPRACH": prach,
        "nrPRACHIndices": prach_indices,
        "nrPRACHGrid": prach_grid,
        "nrPRACHOFDMInfo": prach_ofdm_info,
        "nrPRACHOFDMModulate": prach_ofdm_modulate,
        "nrPRACHDetect": prach_detect,
    })
