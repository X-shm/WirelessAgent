"""Standalone normalized Doppler impulse responses and spectrum metadata."""
from __future__ import annotations

import numpy as np
from scipy.special import gamma, jv

from _nr_remaining_common import run_cli


def _time(fd, time):
    t = np.asarray(time, float).reshape(-1)
    if fd <= 0 or not np.isfinite(fd) or not len(t) or np.any(~np.isfinite(t)):
        raise ValueError("positive finite Doppler frequency and nonempty finite time required")
    return t


def _normalize(response):
    h = np.real(response) * np.hamming(len(response))
    energy = np.sum(abs(h)**2)
    if energy <= 0:
        raise ValueError("Doppler impulse response has zero energy")
    return {"impulse_response": h / np.sqrt(energy)}


def flatir(fd: float, time):
    t = _time(fd, time)
    return _normalize(np.sqrt(2 * fd) * np.sinc(2 * fd * t))


def gaussianir(fc: float, time):
    t = _time(fc, time)
    response = (np.pi**.25 * np.sqrt(2 * fc) / np.log(2)**.25 *
                np.exp(-2 * np.pi**2 * fc**2 * t**2 / np.log(2)))
    return _normalize(response)


def jakesir(fd: float, time):
    t = _time(fd, time)
    x = abs(2 * np.pi * fd * t)
    nu = .25
    response = np.empty_like(x)
    nz = x > 0
    response[nz] = x[nz]**-nu * jv(nu, x[nz])
    response[~nz] = .5**nu / gamma(nu + 1)
    return _normalize(response)


def _spectrum_filter(fd, time, oversampling, density):
    t = _time(fd, time)
    if oversampling < 2:
        raise ValueError("oversampling must be at least 2")
    n = int(np.ceil(oversampling * len(t)))
    if n % 2:
        n += 1
    frequency = np.fft.fftfreq(n, 1 / (2 * fd * oversampling))
    spectral_density = np.maximum(np.asarray(density(frequency), float), 0)
    response = np.fft.fftshift(np.fft.ifft(np.sqrt(spectral_density))).real
    start = (n - len(t)) // 2
    return _normalize(response[start:start + len(t)])


def bellir(fd: float, coefficient: float, time, oversampling: int = 8):
    if coefficient <= 0:
        raise ValueError("coefficient must be positive")
    return _spectrum_filter(fd, time, oversampling,
                            lambda f: np.where(abs(f) <= fd, 1 / (1 + coefficient * (f / fd)**2), 0))


def roundedir(fd: float, coefficients, time, oversampling: int = 8):
    c = np.asarray(coefficients, float).reshape(-1)
    if not len(c) or np.any(~np.isfinite(c)):
        raise ValueError("coefficients must be finite and nonempty")
    return _spectrum_filter(fd, time, oversampling,
                            lambda f: np.where(abs(f) <= fd,
                                               np.polyval(c[::-1], abs(f) / fd), 0))


def bigaussianir(fd: float, sigmas, centers, gains, time, oversampling: int = 8):
    sigma, center, gain = (np.asarray(x, float).reshape(-1) for x in (sigmas, centers, gains))
    if len(sigma) != 2 or len(center) != 2 or len(gain) != 2 or np.any(sigma <= 0) or np.any(gain < 0):
        raise ValueError("two positive sigmas, centers and nonnegative gains required")
    return _spectrum_filter(fd, time, oversampling,
                            lambda f: sum(g * np.exp(-.5 * ((f / fd - mu) / s)**2)
                                          for s, mu, g in zip(sigma, center, gain)))


def rjakesir(fd: float, frequency_range, time, oversampling: int = 8):
    bounds = np.asarray(frequency_range, float).reshape(-1)
    if len(bounds) != 2 or bounds[0] >= bounds[1] or bounds[0] < -1 or bounds[1] > 1:
        raise ValueError("frequency_range must be increasing within [-1,1]")
    return _spectrum_filter(fd, time, oversampling,
                            lambda f: np.where((f / fd >= bounds[0]) & (f / fd <= bounds[1]),
                                               1 / np.sqrt(np.maximum(1 - (f / fd)**2, 1e-9)), 0))


def ajakesir(fd: float, frequency_range, time, oversampling: int = 8):
    bounds = np.asarray(frequency_range, float).reshape(-1)
    if len(bounds) != 2 or bounds[0] >= bounds[1] or bounds[0] < -1 or bounds[1] > 1:
        raise ValueError("frequency_range must be increasing within [-1,1]")
    midpoint = np.mean(bounds)
    return _spectrum_filter(fd, time, oversampling,
                            lambda f: np.where((f / fd >= bounds[0]) & (f / fd <= bounds[1]),
                                               (1 + .5 * (f / fd - midpoint)) /
                                               np.sqrt(np.maximum(1 - (f / fd)**2, 1e-9)), 0))


def doppler(spec_type: str, **parameters):
    kinds = {"Flat", "Gaussian", "Jakes", "Bell", "Rounded", "BiGaussian", "RJakes", "AJakes"}
    if spec_type not in kinds:
        raise ValueError(f"spec_type must be one of {sorted(kinds)}")
    return {"type": spec_type, "parameters": parameters}


if __name__ == "__main__":
    run_cli("Standalone normalized Doppler spectrum and impulse-response slices", {
        "flatir": flatir, "gaussianir": gaussianir, "jakesir": jakesir,
        "bellir": bellir, "roundedir": roundedir, "bigaussianir": bigaussianir,
        "rjakesir": rjakesir, "ajakesir": ajakesir, "doppler": doppler,
    })
