"""Standalone sampled analog carrier modulation and coherent demodulation."""
from __future__ import annotations

import numpy as np
from scipy.signal import hilbert

from _nr_remaining_common import run_cli


def _signal(samples, carrier_hz: float, sample_rate: float):
    x = np.asarray(samples, float).reshape(-1)
    if not len(x) or np.any(~np.isfinite(x)) or not 0 < carrier_hz < sample_rate / 2:
        raise ValueError("finite samples and 0 < carrier_hz < Nyquist required")
    return x, np.arange(len(x)) / sample_rate


def _baseband(samples, carrier_hz, sample_rate, initial_phase):
    y, t = _signal(samples, carrier_hz, sample_rate)
    z = hilbert(y) * np.exp(-1j * (2 * np.pi * carrier_hz * t + initial_phase))
    return z


def _lowpass(values, cutoff_hz, sample_rate):
    if not 0 < cutoff_hz < sample_rate / 2:
        raise ValueError("cutoff_hz must lie below Nyquist")
    spectrum = np.fft.fft(values)
    spectrum[abs(np.fft.fftfreq(len(values), 1 / sample_rate)) > cutoff_hz] = 0
    return np.fft.ifft(spectrum)


def ammod(samples, carrier_hz: float, sample_rate: float,
          carrier_amplitude: float = 0.0, initial_phase: float = 0.0):
    x, t = _signal(samples, carrier_hz, sample_rate)
    return {"samples": (x + carrier_amplitude) *
            np.cos(2 * np.pi * carrier_hz * t + initial_phase)}


def amdemod(samples, carrier_hz: float, sample_rate: float,
            carrier_amplitude: float = 0.0, initial_phase: float = 0.0,
            cutoff_hz: float | None = None):
    if cutoff_hz is None:
        cutoff_hz = carrier_hz * .8
    base = _lowpass(_baseband(samples, carrier_hz, sample_rate, initial_phase),
                    cutoff_hz, sample_rate)
    return {"samples": base.real - carrier_amplitude}


def fmmod(samples, carrier_hz: float, sample_rate: float,
          freqdev_hz: float, initial_phase: float = 0.0):
    x, t = _signal(samples, carrier_hz, sample_rate)
    if freqdev_hz <= 0:
        raise ValueError("freqdev_hz must be positive")
    phase = 2 * np.pi * carrier_hz * t + 2 * np.pi * freqdev_hz * np.cumsum(x) / sample_rate + initial_phase
    return {"samples": np.cos(phase)}


def fmdemod(samples, carrier_hz: float, sample_rate: float,
            freqdev_hz: float, initial_phase: float = 0.0):
    if freqdev_hz <= 0:
        raise ValueError("freqdev_hz must be positive")
    base = _baseband(samples, carrier_hz, sample_rate, initial_phase)
    phase = np.unwrap(np.angle(base))
    delta = np.diff(np.r_[0, phase])
    return {"samples": delta * sample_rate / (2 * np.pi * freqdev_hz)}


def pmmod(samples, carrier_hz: float, sample_rate: float,
          phasedev: float, initial_phase: float = 0.0):
    x, t = _signal(samples, carrier_hz, sample_rate)
    if phasedev <= 0:
        raise ValueError("phasedev must be positive")
    return {"samples": np.cos(2 * np.pi * carrier_hz * t + phasedev * x + initial_phase)}


def pmdemod(samples, carrier_hz: float, sample_rate: float,
            phasedev: float, initial_phase: float = 0.0,
            cutoff_hz: float | None = None):
    if phasedev <= 0:
        raise ValueError("phasedev must be positive")
    base = _baseband(samples, carrier_hz, sample_rate, initial_phase)
    if cutoff_hz is not None:
        base = _lowpass(base, cutoff_hz, sample_rate)
    return {"samples": np.unwrap(np.angle(base)) / phasedev}


def ssbmod(samples, carrier_hz: float, sample_rate: float,
           sideband: str = "lower", initial_phase: float = 0.0):
    x, t = _signal(samples, carrier_hz, sample_rate)
    if sideband not in ("lower", "upper"):
        raise ValueError("sideband must be lower or upper")
    theta = 2 * np.pi * carrier_hz * t + initial_phase
    sign = 1 if sideband == "lower" else -1
    return {"samples": x * np.cos(theta) + sign * np.imag(hilbert(x)) * np.sin(theta)}


def ssbdemod(samples, carrier_hz: float, sample_rate: float,
             sideband: str = "lower", initial_phase: float = 0.0,
             cutoff_hz: float | None = None):
    if sideband not in ("lower", "upper"):
        raise ValueError("sideband must be lower or upper")
    if cutoff_hz is None:
        cutoff_hz = carrier_hz * .8
    return {"samples": _lowpass(_baseband(samples, carrier_hz, sample_rate,
                                          initial_phase), cutoff_hz, sample_rate).real}


if __name__ == "__main__":
    run_cli("Standalone sampled analog carrier modulation slices", {
        "ammod": ammod, "amdemod": amdemod, "fmmod": fmmod, "fmdemod": fmdemod,
        "pmmod": pmmod, "pmdemod": pmdemod, "ssbmod": ssbmod, "ssbdemod": ssbdemod,
    })
