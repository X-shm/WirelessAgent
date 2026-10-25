"""Headless WLAN tapped-delay channel and Non-HT packet workflow slices."""
from __future__ import annotations

import math
from functools import partial

import numpy as np
from scipy.special import j0

from _nr_remaining_common import run_cli
from wlan_mac_family import field_indices, format_detect
from wlan_numeric_family import _complex_samples
from wlan_signal_fields import data_field, signal_field, training_field
from wlan_symbol_timing import lltf_waveform


CHANNELS = ("wlanTGacChannel", "wlanTGahChannel", "wlanTGaxChannel",
            "wlanTGayChannel", "wlanTGnChannel")


def tapped_channel(name, waveform, sample_rate_hz, path_delays_ns=None,
                   average_path_gains_db=None, max_doppler_hz=0.0,
                   k_factor=0.0, seed=0, normalize=True):
    x = _complex_samples(waveform).reshape(-1)
    if x.size == 0 or x.size > 1000000 or not 0 < sample_rate_hz <= 3e9:
        raise ValueError("finite nonempty waveform and sample_rate_hz in (0,3e9] required")
    delays = [0.0] if path_delays_ns is None else path_delays_ns
    gains = [0.0] if average_path_gains_db is None else average_path_gains_db
    if len(delays) != len(gains) or not 1 <= len(delays) <= 64:
        raise ValueError("path delays and gains must have equal lengths in 1..64")
    if any(not math.isfinite(d) or d < 0 for d in delays) or any(not math.isfinite(g) for g in gains):
        raise ValueError("path delays must be nonnegative and gains finite")
    if not math.isfinite(max_doppler_hz) or max_doppler_hz < 0 or not math.isfinite(k_factor) or k_factor < 0:
        raise ValueError("max_doppler_hz and k_factor must be nonnegative")
    taps = np.rint(np.asarray(delays) * 1e-9 * sample_rate_hz).astype(int)
    if taps.max() > 1000000:
        raise ValueError("path delay exceeds output limit")
    power = 10 ** (np.asarray(gains, float) / 10)
    if normalize:
        power /= power.sum()
    rng = np.random.default_rng(seed)
    length = x.size + int(taps.max())
    y = np.zeros(length, dtype=complex)
    rho = float(j0(2 * math.pi * max_doppler_hz / sample_rate_hz)) if max_doppler_hz else 1.0
    rho = max(-.999999, min(.999999, rho)) if max_doppler_hz else 1.0
    first_gains = []
    for index, (offset, path_power) in enumerate(zip(taps, power)):
        real = rng.standard_normal(x.size)
        imag = rng.standard_normal(x.size)
        innovations = (real + 1j*imag) / math.sqrt(2)
        if max_doppler_hz:
            fading = np.empty(x.size, dtype=complex)
            fading[0] = innovations[0]
            for i in range(1, x.size):
                fading[i] = rho*fading[i-1] + math.sqrt(1-rho*rho)*innovations[i]
        else:
            fading = np.full(x.size, innovations[0], dtype=complex)
        if index == 0 and k_factor > 0:
            fading = math.sqrt(k_factor/(k_factor+1)) + fading / math.sqrt(k_factor+1)
        fading *= math.sqrt(path_power)
        y[offset:offset+x.size] += x*fading
        first_gains.append([float(fading[0].real), float(fading[0].imag)])
    return {"model": name, "waveform": {"real": y.real.tolist(), "imag": y.imag.tolist()},
            "path_delay_samples": taps.tolist(), "first_tap_gains": first_gains,
            "sample_rate_hz": sample_rate_hz, "max_doppler_hz": max_doppler_hz}


def waveform_generator(psdu_bits, mcs=0, scrambler_seed=93,
                       format="Non-HT", channel_bandwidth="CBW20"):
    if format != "Non-HT" or channel_bandwidth != "CBW20":
        raise ValueError("waveform generator slice supports Non-HT CBW20")
    if not isinstance(psdu_bits, list) or not psdu_bits or len(psdu_bits) % 8:
        raise ValueError("psdu_bits must be a nonempty whole number of octets")
    data = data_field("wlanNonHTData", psdu_bits, mcs, scrambler_seed)
    sig = signal_field("wlanLSIG", mcs, len(psdu_bits)//8)
    stf = training_field("wlanLSTF")["waveform"]
    ltf = lltf_waveform("CBW20")
    components = [np.asarray(stf["real"]) + 1j*np.asarray(stf["imag"]),
                  ltf,
                  np.asarray(sig["waveform"]["real"]) + 1j*np.asarray(sig["waveform"]["imag"]),
                  np.asarray(data["waveform"]["real"]) + 1j*np.asarray(data["waveform"]["imag"])]
    wave = np.concatenate(components)
    indices = field_indices(format="Non-HT", num_data_symbols=data["num_data_symbols"])
    return {"format": format, "waveform": {"real": wave.real.tolist(), "imag": wave.imag.tolist()},
            "sample_rate_hz": 20e6, "sample_count": len(wave),
            "field_indices": indices["indices"], "num_data_symbols": data["num_data_symbols"]}


def waveform_analyzer(waveform, sample_rate_hz=20e6, threshold=0.5):
    x = _complex_samples(waveform).reshape(-1)
    if sample_rate_hz != 20e6 or x.size < 400:
        raise ValueError("analyzer slice requires CBW20 waveform of at least 400 samples")
    detected = format_detect({"real": x.real.tolist(), "imag": x.imag.tolist()}, threshold)
    legacy = x[:400]
    power = abs(x) ** 2
    papr = float(10*np.log10(power.max() / max(power.mean(), 1e-30)))
    return {"format": detected["format"],
            "legacy_preamble_correlation": detected["legacy_preamble_correlation"],
            "sample_count": x.size, "sample_rate_hz": sample_rate_hz,
            "papr_db": papr, "legacy_field_indices": field_indices(format="Non-HT")["indices"],
            "mean_legacy_power": float(np.mean(abs(legacy)**2))}


DISPATCH = {name: partial(tapped_channel, name) for name in CHANNELS}
DISPATCH.update({"wlanWaveformGenerator": waveform_generator,
                 "wlanWaveformAnalyzer": waveform_analyzer})


if __name__ == "__main__":
    run_cli("WLAN explicit tapped-delay channel and Non-HT waveform workflow", DISPATCH)
