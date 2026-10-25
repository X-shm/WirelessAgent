"""Python WLAN legacy preamble, SIGNAL and SISO data waveform slices."""
from __future__ import annotations

import math
import json
from functools import partial
from pathlib import Path

import numpy as np

from _nr_remaining_common import run_cli
from wlan_bcc import bcc_encode
from wlan_bit_routing import wlan_bcc_interleave
from wlan_constellation import constellation_map
from wlan_scramble import scramble


TRAINING = ("wlanLSTF", "wlanHTSTF", "wlanHTLTF", "wlanVHTSTF", "wlanVHTLTF")
SIGNAL = ("wlanLSIG", "wlanHTSIG", "wlanVHTSIGA", "wlanVHTSIGB")
DATA = ("wlanNonHTData", "wlanHTData", "wlanVHTData")

_STF_SIGNS = (1, -1, 1, -1, -1, 1, -1, -1, 1, 1, 1, 1)
_NONHT = ((1, "1/2"), (1, "3/4"), (2, "1/2"), (2, "3/4"),
          (4, "1/2"), (4, "3/4"), (6, "2/3"), (6, "3/4"))
_HTVHT = ((1, "1/2"), (2, "1/2"), (2, "3/4"), (4, "1/2"),
          (4, "3/4"), (6, "2/3"), (6, "3/4"), (6, "5/6"),
          (8, "3/4"), (8, "5/6"))
_RATE_BITS = ((1,1,0,1),(1,1,1,1),(0,1,0,1),(0,1,1,1),
              (1,0,0,1),(1,0,1,1),(0,0,0,1),(0,0,1,1))
_PILOT_POLARITY = json.loads(Path(__file__).with_name("_wlan_training_defaults.json").read_text(
    encoding="utf-8"))["pilot_polarity"]


def _iq(array):
    return {"real": array.real.tolist(), "imag": array.imag.tolist()}


def _bits(value):
    bits = np.asarray(value, dtype=np.uint8).reshape(-1)
    if bits.size == 0 or not np.all((bits == 0) | (bits == 1)):
        raise ValueError("input must contain binary bits")
    return bits


def _stf():
    spectrum = np.zeros(64, dtype=complex)
    positions = (-24, -20, -16, -12, -8, -4, 4, 8, 12, 16, 20, 24)
    for tone, sign in zip(positions, _STF_SIGNS):
        spectrum[tone + 32] = sign * (1 + 1j) / math.sqrt(2)
    one = np.fft.ifft(np.fft.ifftshift(spectrum)) * 64 / math.sqrt(12)
    return np.concatenate((one, one, one[:32]))


def training_field(name, channel_bandwidth="CBW20", num_transmit_antennas=1):
    if name == "wlanLSTF" and channel_bandwidth not in ("CBW5", "CBW10", "CBW20"):
        raise ValueError("L-STF waveform slice supports CBW5/10/20")
    if name != "wlanLSTF" and channel_bandwidth != "CBW20":
        raise ValueError("HT/VHT training waveform slice supports CBW20")
    if num_transmit_antennas != 1:
        raise ValueError("training waveform slice supports one transmit antenna")
    if name == "wlanLSTF":
        wave = _stf()
    else:
        source = Path(__file__).with_name("_wlan_training_defaults.json")
        samples = json.loads(source.read_text(encoding="utf-8"))[name]
        wave = np.asarray(samples["real"]) + 1j * np.asarray(samples["imag"])
    return {"field": name, "waveform": _iq(wave), "sample_count": len(wave),
            "sample_rate_hz": int(channel_bandwidth[3:]) * 1e6}


def _ofdm_symbol(data, data_tones, pilot_tones=(-21, -7, 7, 21), pilot_values=(1, 1, 1, -1)):
    if len(data) != len(data_tones):
        raise ValueError("data symbol count differs from active data tones")
    grid = np.zeros(64, dtype=complex)
    for tone, value in zip(data_tones, data):
        grid[tone + 32] = value
    for tone, value in zip(pilot_tones, pilot_values):
        grid[tone + 32] = value
    ntones = len(data_tones) + len(pilot_tones)
    useful = np.fft.ifft(np.fft.ifftshift(grid)) * 64 / math.sqrt(ntones)
    return np.concatenate((useful[-16:], useful))


def _data_tones(format):
    edge = 26 if format == "Non-HT" else 28
    return [i for i in range(-edge, edge+1) if i not in (0,-21,-7,7,21)]


def signal_field(name, mcs=0, psdu_length=0, field_bits=None):
    if name == "wlanLSIG":
        if not isinstance(mcs, int) or not 0 <= mcs < 8 or not 0 <= psdu_length <= 4095:
            raise ValueError("L-SIG MCS 0..7 and PSDU length 0..4095 required")
        length = [(psdu_length >> i) & 1 for i in range(12)]
        first = list(_RATE_BITS[mcs]) + [0] + length
        bits = np.asarray(first + [sum(first) % 2] + [0]*6, dtype=np.uint8)
    else:
        if field_bits is None:
            raise ValueError("field_bits required for HT/VHT SIGNAL subset")
        bits = _bits(field_bits)
        if bits.size % 24:
            raise ValueError("field_bits length must be a multiple of 24")
    encoded = bcc_encode(bits, "1/2")
    if encoded.size % 48:
        raise ValueError("SIGNAL encoded length must be divisible by 48")
    interleaved = np.asarray(wlan_bcc_interleave(encoded.tolist(), 48)["bits"], dtype=np.uint8)
    mapped = constellation_map(interleaved, 1)
    tones = _data_tones("Non-HT")
    symbols = [_ofdm_symbol(mapped[i:i+48], tones) for i in range(0, mapped.size, 48)]
    wave = np.concatenate(symbols)
    return {"field": name, "field_bits": bits.tolist(), "encoded_bits": encoded.tolist(),
            "waveform": _iq(wave), "sample_count": len(wave), "sample_rate_hz": 20e6}


def data_field(name, psdu_bits, mcs=0, scrambler_seed=93):
    payload = _bits(psdu_bits)
    format = "Non-HT" if name == "wlanNonHTData" else "HT" if name == "wlanHTData" else "VHT"
    table = _NONHT if format == "Non-HT" else _HTVHT
    if not isinstance(mcs, int) or not 0 <= mcs < len(table):
        raise ValueError("MCS out of supported range")
    nbpscs, code_rate = table[mcs]
    tones = _data_tones(format)
    ncbps = len(tones)*nbpscs
    rate_num, rate_den = (int(x) for x in code_rate.split("/"))
    ndbps = ncbps*rate_num//rate_den
    useful = 16 + payload.size + 6
    nsym = math.ceil(useful / ndbps)
    raw = np.concatenate((np.zeros(16,dtype=np.uint8), payload,
                          np.zeros(nsym*ndbps-16-payload.size,dtype=np.uint8)))
    scrambled = scramble(raw, scrambler_seed)
    scrambled[16+payload.size:16+payload.size+6] = 0
    encoded = bcc_encode(scrambled, code_rate)
    if encoded.size != nsym*ncbps:
        raise ValueError("BCC puncturing length inconsistent with selected MCS")
    interleaved = np.asarray(wlan_bcc_interleave(encoded.tolist(), ncbps, nbpscs,
                                                "Non-HT" if format == "Non-HT" else "VHT")["bits"])
    mapped = constellation_map(interleaved, nbpscs)
    symbols = [_ofdm_symbol(mapped[i:i+len(tones)], tones,
                            pilot_values=tuple(_PILOT_POLARITY[(symbol+1) % 127]*p
                                               for p in (1, 1, 1, -1)))
               for symbol, i in enumerate(range(0, mapped.size, len(tones)))]
    wave = np.concatenate(symbols)
    return {"field": name, "format": format, "mcs": mcs, "num_data_symbols": nsym,
            "waveform": _iq(wave), "sample_count": len(wave), "sample_rate_hz": 20e6,
            "psdu_bit_count": int(payload.size)}


DISPATCH = {name: partial(training_field, name) for name in TRAINING}
DISPATCH.update({name: partial(signal_field, name) for name in SIGNAL})
DISPATCH.update({name: partial(data_field, name) for name in DATA})


if __name__ == "__main__":
    run_cli("WLAN legacy training, SIGNAL and SISO data waveform slices", DISPATCH)
