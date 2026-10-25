"""Headless WLAN OFDM geometry and FFT demodulation slices."""
from __future__ import annotations

import math
from functools import partial

import numpy as np

from _nr_remaining_common import run_cli
from wlan_numeric_family import _complex_samples


INFO = {
    "wlanDMGOFDMInfo": "DMG", "wlanEHTOFDMInfo": "EHT",
    "wlanHEOFDMInfo": "HE", "wlanHTOFDMInfo": "HT",
    "wlanS1GOFDMInfo": "S1G", "wlanVHTOFDMInfo": "VHT",
}
DEMOD = {
    "wlanDMGOFDMDemodulate": "DMG", "wlanEHTDemodulate": "EHT",
    "wlanHEDemodulate": "HE", "wlanHTLTFDemodulate": "HT",
    "wlanLLTFDemodulate": "Non-HT", "wlanNonHTOFDMDemodulate": "Non-HT",
    "wlanS1GDemodulate": "S1G", "wlanVHTDemodulate": "VHT",
    "wlanVHTLTFDemodulate": "VHT",
}


def geometry(format, channel_bandwidth="CBW20", guard_interval_us=None,
             oversampling_factor=1.0):
    if format not in ("Non-HT", "HT", "VHT", "HE", "EHT", "DMG", "S1G"):
        raise ValueError("unsupported WLAN format")
    if not isinstance(channel_bandwidth, str) or not channel_bandwidth.startswith("CBW"):
        raise ValueError("invalid channel bandwidth")
    try:
        mhz = int(channel_bandwidth[3:])
    except ValueError as exc:
        raise ValueError("invalid channel bandwidth") from exc
    allowed = ((1, 2, 4, 8, 16) if format == "S1G" else
               (2160,) if format == "DMG" else
               (20, 40, 80, 160, 320) if format == "EHT" else
               (20, 40, 80, 160) if format in ("HE", "VHT") else
               (5, 10, 20, 40))
    if mhz not in allowed:
        raise ValueError(f"{format} does not support {channel_bandwidth} in this Python slice")
    if not math.isfinite(oversampling_factor) or oversampling_factor < 1 or int(oversampling_factor) != oversampling_factor:
        raise ValueError("oversampling_factor must be a positive integer")
    if format == "DMG":
        base_fft, rate = 512, 2.64e9
    elif format == "S1G":
        base_fft, rate = 64 * max(1, mhz // 2), mhz * 1e6
    else:
        base_fft = (256 if format in ("HE", "EHT") else 64) * max(1, mhz // 20)
        rate = mhz * 1e6
    nfft = int(base_fft * oversampling_factor)
    if guard_interval_us is None:
        guard_interval_us = 0.8
    if guard_interval_us not in (0.4, 0.8, 1.6, 3.2):
        raise ValueError("guard_interval_us must be 0.4, 0.8, 1.6 or 3.2")
    cp = int(round(guard_interval_us * 1e-6 * rate * oversampling_factor))
    return {"format": format, "channel_bandwidth": channel_bandwidth,
            "fft_length": nfft, "sample_rate_hz": rate * oversampling_factor,
            "cp_length": cp, "symbol_length": nfft + cp,
            "subcarrier_spacing_hz": rate * oversampling_factor / nfft}


def ofdm_info(format, field="Data", channel_bandwidth="CBW20",
              guard_interval_us=None, oversampling_factor=1.0):
    result = geometry(format, channel_bandwidth, guard_interval_us, oversampling_factor)
    result["field"] = field
    return result


def ofdm_demodulate(format, waveform, field="Data", channel_bandwidth="CBW20",
                    guard_interval_us=None, oversampling_factor=1.0,
                    fft_length=None, cp_length=None, active_indices=None):
    geom = geometry(format, channel_bandwidth, guard_interval_us, oversampling_factor)
    nfft = geom["fft_length"] if fft_length is None else fft_length
    cp = geom["cp_length"] if cp_length is None else cp_length
    if not isinstance(nfft, int) or nfft < 8 or nfft > 8192 or not isinstance(cp, int) or not 0 <= cp < nfft:
        raise ValueError("invalid FFT/CP lengths")
    waveform = _complex_samples(waveform)
    if waveform.ndim not in (1, 2):
        raise ValueError("waveform must be a 1-D or [sample,antenna] array")
    if waveform.ndim == 1:
        waveform = waveform[:, None]
    if field == "L-LTF" and format == "Non-HT" and cp_length is None:
        cp = nfft // 2
        if waveform.shape[0] < cp + 2*nfft:
            raise ValueError("L-LTF requires two repeated FFT symbols")
        useful = np.stack((waveform[cp:cp+nfft], waveform[cp+nfft:cp+2*nfft]))
        nsym = 2
    else:
        step = nfft + cp
        nsym = waveform.shape[0] // step
        if nsym < 1:
            raise ValueError("waveform shorter than one OFDM symbol")
        useful = waveform[:nsym*step].reshape(nsym, step, waveform.shape[1])[:, cp:cp+nfft]
    grid = np.fft.fftshift(np.fft.fft(useful, axis=1) / math.sqrt(nfft), axes=1)
    grid = np.moveaxis(grid, 0, 1)
    if active_indices is not None:
        indices = np.asarray(active_indices, dtype=int)
        if indices.ndim != 1 or np.any(indices < 0) or np.any(indices >= nfft):
            raise ValueError("active_indices must be zero-based FFT-bin indices")
        grid = grid[indices]
    return {"symbols": {"real": grid.real.tolist(), "imag": grid.imag.tolist()},
            "num_symbols": nsym, "fft_length": nfft, "cp_length": cp,
            "sample_rate_hz": geom["sample_rate_hz"], "format": format, "field": field}


DISPATCH = {name: partial(ofdm_info, fmt) for name, fmt in INFO.items()}
DISPATCH.update({name: partial(ofdm_demodulate, fmt) for name, fmt in DEMOD.items()})
DISPATCH["wlanLLTFDemodulate"] = partial(ofdm_demodulate, "Non-HT", field="L-LTF")


if __name__ == "__main__":
    run_cli("WLAN OFDM geometry and FFT demodulation", DISPATCH)
