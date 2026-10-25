"""Standalone APSK, arbitrary QAM, MIL-188 QAM and MSK slices."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from _nr_remaining_common import complex_array, run_cli


def _indices(values, size):
    x = np.asarray(values)
    if not x.size or np.any(x != np.floor(x)) or np.any(x < 0) or np.any(x >= size):
        raise ValueError(f"symbols must be integers 0..{size-1}")
    return x.astype(int)


def _nearest(samples, constellation):
    y = complex_array(samples).reshape(-1)
    if not len(y):
        raise ValueError("samples must be nonempty")
    return np.argmin(abs(y[:, None] - constellation[None, :])**2, axis=1)


def genqammod(symbols, constellation):
    c = complex_array(constellation).reshape(-1)
    if not len(c) or len(set(c.tolist())) != len(c):
        raise ValueError("constellation must contain distinct points")
    return {"samples": c[_indices(symbols, len(c))]}


def genqamdemod(samples, constellation):
    c = complex_array(constellation).reshape(-1)
    if not len(c) or len(set(c.tolist())) != len(c):
        raise ValueError("constellation must contain distinct points")
    return {"symbols": _nearest(samples, c)}


def _apsk_constellation(ring_sizes, radii, phase_offsets=None):
    sizes = list(map(int, ring_sizes))
    r = np.asarray(radii, float).reshape(-1)
    if not sizes or len(sizes) != len(r) or any(n < 1 for n in sizes) or np.any(r <= 0) or np.any(np.diff(r) <= 0):
        raise ValueError("positive ring sizes and strictly increasing positive radii required")
    phases = np.zeros(len(sizes)) if phase_offsets is None else np.asarray(phase_offsets, float)
    if len(phases) != len(sizes):
        raise ValueError("one phase offset required per ring")
    return np.concatenate([radius * np.exp(1j * (phase + 2 * np.pi * np.arange(n) / n))
                           for n, radius, phase in zip(sizes, r, phases)])


def apskmod(symbols, ring_sizes, radii, phase_offsets=None):
    c = _apsk_constellation(ring_sizes, radii, phase_offsets)
    return {"samples": c[_indices(symbols, len(c))], "constellation": c}


def apskdemod(samples, ring_sizes, radii, phase_offsets=None):
    c = _apsk_constellation(ring_sizes, radii, phase_offsets)
    return {"symbols": _nearest(samples, c)}


def _mil188_constellation(order: int):
    if order not in (16, 32, 64, 256):
        raise ValueError("MIL-188 order must be 16, 32, 64 or 256")
    path = Path(__file__).resolve().parents[1] / "matlab_oracle" / "samples" / "comm_mil188_constellations.json"
    data = json.loads(path.read_text(encoding="utf-8"))[f"M{order}"]
    return np.asarray(data["real"]) + 1j * np.asarray(data["imag"])


def mil188qammod(symbols, order: int):
    c = _mil188_constellation(order)
    return {"samples": c[_indices(symbols, order)]}


def mil188qamdemod(samples, order: int):
    return {"symbols": _nearest(samples, _mil188_constellation(order))}


def mskmod(bits, samples_per_symbol: int, initial_phase: float = 0.0):
    b = np.asarray(bits)
    if not b.size or np.any((b != 0) & (b != 1)) or samples_per_symbol < 1:
        raise ValueError("binary bits and positive samples_per_symbol required")
    increments = np.repeat((2 * b.astype(int).reshape(-1) - 1) * np.pi / (2 * samples_per_symbol),
                           samples_per_symbol)
    phase = initial_phase + np.cumsum(increments)
    return {"samples": np.exp(1j * phase), "final_phase": float(phase[-1])}


def mskdemod(samples, samples_per_symbol: int, initial_phase: float = 0.0):
    y = complex_array(samples).reshape(-1)
    if samples_per_symbol < 1 or not len(y) or len(y) % samples_per_symbol:
        raise ValueError("sample count must be a multiple of samples_per_symbol")
    previous = np.r_[np.exp(1j * initial_phase), y[:-1]]
    phase_steps = np.angle(y * np.conj(previous)).reshape(-1, samples_per_symbol)
    return {"bits": (np.sum(phase_steps, axis=1) > 0).astype(int)}


if __name__ == "__main__":
    run_cli("Standalone APSK, arbitrary QAM, MIL-188 QAM and MSK", {
        "apskmod": apskmod, "apskdemod": apskdemod,
        "genqammod": genqammod, "genqamdemod": genqamdemod,
        "mil188qammod": mil188qammod, "mil188qamdemod": mil188qamdemod,
        "mskmod": mskmod, "mskdemod": mskdemod,
    })
