"""MATLAB-free, explicitly parameterized NR channel model subsets."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import complex_array, run_cli


def _validate_rate(sample_rate: float):
    if not np.isfinite(sample_rate) or sample_rate <= 0:
        raise ValueError("sample_rate must be positive")


def _delay_samples(delays, sample_rate):
    values = np.asarray(delays, dtype=float).reshape(-1)
    if values.size == 0 or np.any(~np.isfinite(values)) or np.any(values < 0):
        raise ValueError("delays must be finite nonnegative seconds")
    samples = values * sample_rate
    if not np.allclose(samples, np.rint(samples), atol=1e-8, rtol=0):
        raise ValueError("this subset requires integer-sample delays")
    return np.rint(samples).astype(int)


def _path_waveform(samples, delays, gains, sample_rate, dopplers=None):
    _validate_rate(sample_rate)
    x = complex_array(samples)
    if x.ndim == 1:
        x = x[:, None]
    if x.ndim != 2 or x.shape[0] == 0:
        raise ValueError("samples must have shape [time, transmit_port]")
    shift = _delay_samples(delays, sample_rate)
    g = complex_array(gains)
    if g.ndim == 1:
        g = g[:, None, None]
    if g.ndim != 3 or g.shape[0] != len(shift) or g.shape[2] != x.shape[1]:
        raise ValueError("gains must have shape [path, receive_port, transmit_port]")
    d = np.zeros(len(shift)) if dopplers is None else np.asarray(dopplers, dtype=float).reshape(-1)
    if len(d) != len(shift) or np.any(~np.isfinite(d)):
        raise ValueError("dopplers must contain one finite Hz value per path")
    y = np.zeros((len(x) + int(max(shift)), g.shape[1]), dtype=complex)
    for path, delay in enumerate(shift):
        phase = np.exp(2j * np.pi * d[path] * np.arange(len(x)) / sample_rate)
        y[delay:delay + len(x)] += (x @ g[path].T) * phase[:, None]
    return {"samples": y, "delay_samples": shift}


def tdl_channel(samples, sample_rate: float, delays, gains, dopplers=None):
    """Static or single-Doppler explicit tapped-delay line, no built-in profile."""
    return _path_waveform(samples, delays, gains, sample_rate, dopplers)


def cdl_channel(samples, sample_rate: float, delays, gains, dopplers=None):
    """Explicit MIMO cluster rays with one constant matrix per ray."""
    return _path_waveform(samples, delays, gains, sample_rate, dopplers)


def hst_channel(samples, sample_rate: float, speed_mps: float,
                carrier_hz: float, path_gain=1.0, delay_seconds: float = 0.0):
    if speed_mps < 0 or carrier_hz <= 0:
        raise ValueError("speed_mps must be nonnegative and carrier_hz positive")
    doppler = speed_mps * carrier_hz / 299792458.0
    return _path_waveform(samples, [delay_seconds], [path_gain], sample_rate, [doppler])


def path_loss(freq_hz: float, bs, ue, los=True, scenario="FSPL"):
    """FSPL and 3GPP urban-macro path loss without stochastic shadow fading."""
    if not np.isfinite(freq_hz) or freq_hz <= 0:
        raise ValueError("freq_hz must be positive")
    bs = np.asarray(bs, dtype=float).reshape(3)
    ue = np.asarray(ue, dtype=float).reshape(3)
    d3 = float(np.linalg.norm(bs - ue))
    d2 = float(np.linalg.norm((bs - ue)[:2]))
    if d3 <= 0:
        raise ValueError("BS and UE must be at different positions")
    if scenario == "FSPL":
        loss = 20 * np.log10(4 * np.pi * d3 * freq_hz / 299792458.0)
        sigma = 0.0
    elif scenario == "UMa":
        if not 1.5 <= ue[2] <= 22.5 or bs[2] <= 1 or d2 < 10:
            raise ValueError("UMa subset requires 10 m <= d2D, 1.5..22.5 m UE and BS > 1 m")
        fc = freq_hz / 1e9
        bp = 4 * (bs[2] - 1) * (ue[2] - 1) * freq_hz / 299792458.0
        pl1 = 28 + 22 * np.log10(d3) + 20 * np.log10(fc)
        pl_los = (pl1 if d2 <= bp else 28 + 40 * np.log10(d3) +
                  20 * np.log10(fc) - 9 * np.log10(bp * bp + (bs[2] - ue[2]) ** 2))
        pl_nlos = 13.54 + 39.08 * np.log10(d3) + 20 * np.log10(fc) - 0.6 * (ue[2] - 1.5)
        loss = pl_los if los else max(pl_los, pl_nlos)
        sigma = 4.0 if los else 6.0
    else:
        raise ValueError("scenario must be FSPL or UMa")
    return {"pathloss_db": float(loss), "shadow_fading_std_db": sigma,
            "distance_2d_m": d2, "distance_3d_m": d3}


def perfect_channel_estimate(path_gains, delays, sample_rate: float,
                             nfft: int, nsc: int):
    """Frequency response of constant explicit path gains at centered NR bins."""
    _validate_rate(sample_rate)
    if not isinstance(nfft, int) or not isinstance(nsc, int) or nfft < nsc or nsc < 1:
        raise ValueError("nfft >= nsc >= 1 required")
    g = complex_array(path_gains)
    if g.ndim == 1:
        g = g[:, None, None]
    d = np.asarray(delays, dtype=float).reshape(-1)
    if g.ndim != 3 or g.shape[0] != len(d) or np.any(d < 0):
        raise ValueError("path_gains must have shape [path, receive_port, transmit_port]")
    frequencies = np.arange(nsc) - nsc // 2
    phasors = np.exp(-2j * np.pi * frequencies[:, None] * sample_rate / nfft * d[None, :])
    h = np.einsum("kp,prt->krt", phasors, g)
    return {"channel": h}


def phase_noise(samples, sample_rate: float, linewidth_hz: float, seed: int = 0):
    """Common-port Wiener phase-noise slice with a specified 3-dB linewidth."""
    _validate_rate(sample_rate)
    if linewidth_hz < 0 or not np.isfinite(linewidth_hz):
        raise ValueError("linewidth_hz must be finite and nonnegative")
    x = complex_array(samples)
    if x.ndim not in (1, 2) or len(x) == 0:
        raise ValueError("samples must be a nonempty vector or [time,port] matrix")
    rng = np.random.default_rng(seed)
    phase = np.cumsum(rng.normal(0, np.sqrt(2 * np.pi * linewidth_hz / sample_rate), len(x)))
    return {"samples": x * np.exp(1j * phase).reshape((-1,) + (1,) * (x.ndim - 1)),
            "phase_radians": phase}


if __name__ == "__main__":
    run_cli("Standalone explicit-path NR channel subsets", {
        "nrTDLChannel": tdl_channel,
        "nrCDLChannel": cdl_channel,
        "nrHSTChannel": hst_channel,
        "nrPathLoss": path_loss,
        "nrPerfectChannelEstimate": perfect_channel_estimate,
        "nrPhaseNoise": phase_noise,
    })
