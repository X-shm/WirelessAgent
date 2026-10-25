"""Independent WLAN numeric helpers for channel, timing and payload sizing."""
from __future__ import annotations

import math

import numpy as np

from _nr_remaining_common import run_cli
from wlan_constellation import constellation_map
from wlan_scramble import scramble


_SCHEMES = {"BPSK": 1, "QPSK": 2, "16QAM": 4, "64QAM": 6,
            "256QAM": 8, "1024QAM": 10, "4096QAM": 12}
_NONHT_MCS = ((1, .5), (1, .75), (2, .5), (2, .75),
              (4, .5), (4, .75), (6, 2/3), (6, .75))
_HT_MCS = ((1, .5), (2, .5), (2, .75), (4, .5), (4, .75),
           (6, 2/3), (6, .75), (6, 5/6))


def _complex_samples(value):
    if isinstance(value, dict):
        real = np.asarray(value.get("real"), float)
        imag = np.asarray(value.get("imag", np.zeros_like(real)), float)
        if real.shape != imag.shape:
            raise ValueError("real and imag shapes differ")
        result = real + 1j * imag
    else:
        raw = np.asarray(value, float)
        if raw.ndim < 2 or raw.shape[-1] != 2:
            raise ValueError("complex samples require {real,imag} or [...,2] pairs")
        result = raw[..., 0] + 1j * raw[..., 1]
    if not np.all(np.isfinite(result)):
        raise ValueError("samples must be finite")
    return result


def _scheme(name):
    phase = 0.0
    if name.startswith("pi/2-"):
        name, phase = name[5:], math.pi / 2
    elif name == "QBPSK":
        name, phase = "BPSK", math.pi / 2
    if name not in _SCHEMES:
        raise ValueError("unsupported WLAN modulation scheme")
    return _SCHEMES[name], phase


def wlan_reference_symbols(modulation="BPSK", phase=0.0):
    nbits, rotation = _scheme(modulation)
    values = np.arange(2 ** nbits, dtype=np.uint32)
    bit_matrix = ((values[:, None] >> np.arange(nbits - 1, -1, -1)) & 1).reshape(-1)
    points = constellation_map(bit_matrix, nbits, float(phase) + rotation)
    return {"modulation": modulation, "symbols": {"real": points.real.tolist(),
                                                      "imag": points.imag.tolist()}}


def wlan_closest_reference_symbol(symbols, modulation="BPSK", phase=0.0):
    data = _complex_samples(symbols)
    reference = wlan_reference_symbols(modulation, phase)["symbols"]
    points = np.asarray(reference["real"]) + 1j * np.asarray(reference["imag"])
    nearest = np.argmin(abs(data.reshape(-1, 1) - points.reshape(1, -1)), axis=1)
    selected = points[nearest].reshape(data.shape)
    return {"symbols": {"real": selected.real.tolist(), "imag": selected.imag.tolist()},
            "indices": nearest.reshape(data.shape).tolist()}


def wlan_channel_frequency(channel, band):
    channels = np.atleast_1d(channel)
    bands = np.atleast_1d(band)
    if bands.size == 1:
        bands = np.repeat(bands, channels.size)
    if bands.size != channels.size:
        raise ValueError("channel and band lengths differ")
    result = []
    for ch, bd in zip(channels, bands):
        if int(ch) != ch or ch < 1:
            raise ValueError("channel must be a positive integer")
        if float(bd) == 2.4 and ch <= 14:
            mhz = 2484 if ch == 14 else 2407 + 5 * int(ch)
        elif float(bd) == 5 and ch <= 200:
            mhz = 5000 + 5 * int(ch)
        elif float(bd) == 6 and ch <= 233:
            mhz = 5935 if ch == 2 else 5950 + 5 * int(ch)
        else:
            raise ValueError("invalid channel for 2.4, 5 or 6 GHz band")
        result.append(mhz * 1e6)
    return {"frequency_hz": result[0] if np.isscalar(channel) else result}


def wlan_sample_rate(channel_bandwidth=None, config=None, oversampling_factor=1.0):
    if config is not None:
        if not isinstance(config, dict):
            raise ValueError("config must be an object")
        channel_bandwidth = config.get("properties", config).get("ChannelBandwidth", channel_bandwidth)
    if not isinstance(channel_bandwidth, str) or not channel_bandwidth.startswith("CBW"):
        raise ValueError("ChannelBandwidth must be a CBW string")
    try:
        mhz = int(channel_bandwidth[3:])
    except ValueError as exc:
        raise ValueError("invalid ChannelBandwidth") from exc
    if mhz not in (1, 2, 4, 5, 8, 10, 16, 20, 40, 80, 160, 320, 2160):
        raise ValueError("unsupported ChannelBandwidth")
    if not math.isfinite(oversampling_factor) or oversampling_factor < 1:
        raise ValueError("oversampling_factor must be at least 1")
    return {"sample_rate_hz": mhz * 1e6 * oversampling_factor,
            "channel_bandwidth": channel_bandwidth}


def wlan_spectral_flatness(channel_est, format="Non-HT", channel_bandwidth="CBW20",
                           max_deviation_db=4.0):
    h = _complex_samples(channel_est)
    if h.size < 2:
        raise ValueError("at least two channel estimates required")
    if max_deviation_db <= 0 or not math.isfinite(max_deviation_db):
        raise ValueError("max_deviation_db must be positive")
    power = abs(h.reshape(h.shape[0], -1)) ** 2
    power = np.mean(power, axis=1)
    if np.any(power <= 0):
        return {"pass": False, "deviation_db": None, "test_subcarriers": list(range(len(power)))}
    db = 10 * np.log10(power)
    db -= np.mean(db)
    return {"pass": bool(np.max(abs(db)) <= max_deviation_db),
            "deviation_db": db.tolist(), "test_subcarriers": list(range(len(power))),
            "format": format, "channel_bandwidth": channel_bandwidth}


def wlan_interpret_scrambler_state(scram_init, center_freq_index1=0, service_field_bits=None):
    if isinstance(scram_init, list):
        if len(scram_init) != 7 or any(bit not in (0, 1) for bit in scram_init):
            raise ValueError("scram_init bit vector must contain seven bits")
        seed = sum(int(b) << i for i, b in enumerate(scram_init))
    else:
        seed = int(scram_init)
    if not 0 <= seed <= 127 or not 0 <= center_freq_index1 <= 200:
        raise ValueError("invalid scrambler state or center frequency index")
    service = [0] * 16 if service_field_bits is None else service_field_bits
    if len(service) != 16 or any(x not in (0, 1) for x in service):
        raise ValueError("service_field_bits must contain 16 bits")
    if seed == 0:
        return {"channel_bandwidth": "Unknown", "dynamic_bandwidth": False}
    initial = scramble(np.zeros(7, dtype=np.uint8), seed)
    cbw_code = int(initial[5]) + 2 * int(initial[6])
    if (cbw_code != 0 and service[7]) or (cbw_code != 3 and center_freq_index1 > 0):
        band = "Unknown"
    elif cbw_code == 0:
        band = "CBW320" if service[7] else "CBW20"
    elif cbw_code == 1:
        band = "CBW40"
    elif cbw_code == 2:
        band = "CBW80"
    else:
        band = "CBW80+80" if center_freq_index1 else "CBW160"
    return {"channel_bandwidth": band, "dynamic_bandwidth": bool(initial[4])}


def _payload_length(format="Non-HT", mcs=0, num_data_symbols=None, tx_time_us=None,
                    channel_bandwidth="CBW20", num_space_time_streams=1):
    if format not in ("Non-HT", "HT", "VHT", "HE", "EHT"):
        raise ValueError("unsupported format")
    if not isinstance(mcs, int) or not 0 <= mcs < 8:
        raise ValueError("supported MCS range is 0..7")
    bw = int(channel_bandwidth.removeprefix("CBW"))
    if bw not in (20, 40, 80, 160, 320):
        raise ValueError("supported bandwidths are CBW20..CBW320")
    if not isinstance(num_space_time_streams, int) or not 1 <= num_space_time_streams <= 8:
        raise ValueError("num_space_time_streams must be 1..8")
    symbol_us = 12.8 if format in ("HE", "EHT") else 3.2
    if num_data_symbols is None:
        if tx_time_us is None or tx_time_us <= 0:
            raise ValueError("num_data_symbols or positive tx_time_us required")
        num_data_symbols = math.floor(tx_time_us / symbol_us)
    if not isinstance(num_data_symbols, int) or num_data_symbols < 0:
        raise ValueError("num_data_symbols must be a nonnegative integer")
    if format == "Non-HT":
        n_data = 48 * max(1, bw // 20)
    elif format in ("HT", "VHT"):
        n_data = {20: 52, 40: 108, 80: 234, 160: 468, 320: 936}[bw]
    else:
        n_data = {20: 234, 40: 468, 80: 980, 160: 1960, 320: 3920}[bw]
    bits, rate = (_NONHT_MCS if format == "Non-HT" else _HT_MCS)[mcs]
    ndbps = math.floor(n_data * bits * rate * num_space_time_streams)
    payload = max(0, math.floor((num_data_symbols * ndbps - 16 - 6 * num_space_time_streams) / 8))
    return {"length_octets": payload, "num_data_symbols": num_data_symbols,
            "bits_per_data_symbol": ndbps, "format": format,
            "channel_bandwidth": channel_bandwidth}


def wlan_psdu_length(**params):
    return _payload_length(**params)


def wlan_apep_length(**params):
    if params.get("format", "VHT") not in ("VHT", "HE", "EHT"):
        raise ValueError("APEP length applies to VHT/HE/EHT")
    result = _payload_length(format="VHT", **params) if "format" not in params else _payload_length(**params)
    result["length_octets"] = max(0, result["length_octets"] - 4)
    return result


def wlan_msdu_lengths(frame_length, mac_header_bytes=24, fcs_bytes=4,
                      max_msdu_bytes=2304):
    if not all(isinstance(x, int) for x in (frame_length, mac_header_bytes, fcs_bytes, max_msdu_bytes)):
        raise ValueError("lengths must be integers")
    if frame_length < 28 or mac_header_bytes < 0 or fcs_bytes < 0 or max_msdu_bytes < 1:
        raise ValueError("invalid MAC frame sizing parameters")
    payload = frame_length - mac_header_bytes - fcs_bytes
    if payload < 0:
        raise ValueError("frame shorter than MAC overhead")
    lengths = []
    while payload:
        size = min(max_msdu_bytes, payload)
        lengths.append(size)
        payload -= size
    return {"msdu_lengths": lengths, "frame_length": frame_length,
            "overhead_bytes": mac_header_bytes + fcs_bytes}


def wlan_hetb_ndp_feedback_status(first_tone_set, second_tone_set, threshold=2.0):
    first = _complex_samples(first_tone_set)
    second = _complex_samples(second_tone_set)
    if first.size == 0 or second.size == 0 or threshold <= 1:
        raise ValueError("nonempty tone sets and threshold > 1 required")
    a, b = float(np.mean(abs(first) ** 2)), float(np.mean(abs(second) ** 2))
    state = 1 if a > threshold * b else 0 if b > threshold * a else -1
    return {"feedback_status": state, "first_energy": a, "second_energy": b}


DISPATCH = {
    "wlanAPEPLength": wlan_apep_length,
    "wlanChannelFrequency": wlan_channel_frequency,
    "wlanClosestReferenceSymbol": wlan_closest_reference_symbol,
    "wlanHETBNDPFeedbackStatus": wlan_hetb_ndp_feedback_status,
    "wlanInterpretScramblerState": wlan_interpret_scrambler_state,
    "wlanMSDULengths": wlan_msdu_lengths,
    "wlanPSDULength": wlan_psdu_length,
    "wlanReferenceSymbols": wlan_reference_symbols,
    "wlanSampleRate": wlan_sample_rate,
    "wlanSpectralFlatness": wlan_spectral_flatness,
}


if __name__ == "__main__":
    run_cli("WLAN independent numerical helper slices", DISPATCH)
