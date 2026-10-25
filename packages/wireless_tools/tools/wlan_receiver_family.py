"""WLAN channel estimation, equalization and pilot tracking primitives."""
from __future__ import annotations

from functools import partial

import numpy as np

from _nr_remaining_common import run_cli
from wlan_numeric_family import _complex_samples


CHANNEL_ESTIMATES = (
    "wlanEHTLTFChannelEstimate", "wlanHELTFChannelEstimate",
    "wlanHTLTFChannelEstimate", "wlanLLTFChannelEstimate",
    "wlanPreEHTChannelEstimate", "wlanPreHEChannelEstimate",
    "wlanVHTLTFChannelEstimate",
)
NOISE_ESTIMATES = ("wlanEHTDataNoiseEstimate", "wlanHEDataNoiseEstimate",
                   "wlanLLTFNoiseEstimate")
EQUALIZERS = ("wlanEHTEqualize", "wlanHEEqualize", "wlanVHTEqualize")
TRACKERS = ("wlanEHTTrackPilotError", "wlanHETrackPilotError",
            "wlanVHTTrackPilotError")


def channel_estimate(rx_symbols, reference_symbols, min_reference_magnitude=1e-12):
    rx = _complex_samples(rx_symbols)
    reference = _complex_samples(reference_symbols)
    if rx.ndim == 1:
        rx = rx[:, None]
    if reference.ndim == 1:
        reference = reference[:, None]
    if rx.shape != reference.shape or rx.shape[0] < 1:
        raise ValueError("SISO received and reference symbol grids must have the same shape")
    weights = abs(reference) ** 2
    summed = np.sum(weights, axis=1)
    if np.any(summed <= min_reference_magnitude):
        raise ValueError("reference energy must be positive on each subcarrier")
    h = np.sum(rx * np.conj(reference), axis=1) / summed
    residual = rx - h[:, None] * reference
    return {"channel_estimate": {"real": h.real.tolist(), "imag": h.imag.tolist()},
            "noise_variance": float(np.mean(abs(residual) ** 2)),
            "num_subcarriers": rx.shape[0], "num_training_symbols": rx.shape[1]}


def noise_estimate(rx_symbols, reference_symbols=None, channel_estimate_symbols=None):
    rx = _complex_samples(rx_symbols)
    if reference_symbols is None:
        if rx.ndim < 2 or rx.shape[1] < 2:
            raise ValueError("two repeated training symbols or reference_symbols required")
        variance = float(np.mean(abs(rx[:, 0] - rx[:, 1]) ** 2) / 2)
    else:
        ref = _complex_samples(reference_symbols)
        if channel_estimate_symbols is None:
            return {"noise_variance": channel_estimate(rx_symbols, reference_symbols)["noise_variance"]}
        h = _complex_samples(channel_estimate_symbols)
        if h.ndim == 1 and rx.ndim == 2:
            h = h[:, None]
        if np.shape(rx) != np.shape(h * ref):
            raise ValueError("received, reference and channel shapes differ")
        variance = float(np.mean(abs(rx - h * ref) ** 2))
    return {"noise_variance": variance}


def equalize(rx_symbols, channel_estimate_symbols, noise_variance=0.0, method="MMSE"):
    y = _complex_samples(rx_symbols)
    h = _complex_samples(channel_estimate_symbols)
    if y.shape != h.shape and not (y.ndim == 2 and h.ndim == 1 and y.shape[0] == h.size):
        raise ValueError("received and channel grids must have matching subcarriers")
    if y.ndim == 2 and h.ndim == 1:
        h = h[:, None]
    if noise_variance < 0 or method not in ("MMSE", "ZF"):
        raise ValueError("noise variance must be nonnegative and method MMSE/ZF")
    power = abs(h) ** 2
    denominator = power + (noise_variance if method == "MMSE" else 0)
    z = np.divide(np.conj(h) * y, denominator, out=np.zeros_like(y), where=denominator > 1e-15)
    csi = np.divide(power, power + noise_variance, out=np.zeros_like(power, dtype=float),
                    where=(power + noise_variance) > 1e-15)
    return {"equalized_symbols": {"real": z.real.tolist(), "imag": z.imag.tolist()},
            "csi": csi.tolist(), "method": method}


def track_pilot_error(received_pilots, reference_pilots):
    received = _complex_samples(received_pilots)
    reference = _complex_samples(reference_pilots)
    if received.shape != reference.shape or received.size == 0:
        raise ValueError("pilot grids must have matching nonempty shapes")
    if received.ndim == 1:
        received = received[:, None]
        reference = reference[:, None]
    common_phase = np.angle(np.sum(received * np.conj(reference), axis=0))
    corrected = received * np.exp(-1j * common_phase)
    return {"common_phase_error_rad": common_phase.tolist(),
            "corrected_pilots": {"real": corrected.real.tolist(),
                                 "imag": corrected.imag.tolist()}}


DISPATCH = {name: channel_estimate for name in CHANNEL_ESTIMATES}
DISPATCH.update({name: noise_estimate for name in NOISE_ESTIMATES})
DISPATCH.update({name: equalize for name in EQUALIZERS})
DISPATCH.update({name: track_pilot_error for name in TRACKERS})


if __name__ == "__main__":
    run_cli("WLAN receiver channel/noise/equalization/pilot primitives", DISPATCH)
