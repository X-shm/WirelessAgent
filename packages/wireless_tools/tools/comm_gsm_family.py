"""Stateless GSM TDMA configuration, waveform and envelope checks."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter1d

from _nr_remaining_common import run_cli


DOWNLINK = {"NB": 0, "FB": 1, "SB": 2, "Dummy": 3, "Off": 5}
UPLINK = {"NB": 0, "AB": 4, "Off": 5}
SYMBOL_RATE = 1625e3 / 6
BURST_SYMBOLS = 156.25


def gsmDownlinkBurstType(value=None):
    if value is not None and value not in DOWNLINK:
        raise ValueError("invalid downlink burst type")
    return {"choices": DOWNLINK, "value": value, "code": DOWNLINK.get(value)}


def gsmUplinkBurstType(value=None):
    if value is not None and value not in UPLINK:
        raise ValueError("invalid uplink burst type")
    return {"choices": UPLINK, "value": value, "code": UPLINK.get(value)}


def _config(direction, samples_per_symbol=16, burst_type="NB", attenuation=0,
            rise_time=2, fall_time=2, rise_delay=0, fall_delay=0, tsc=0):
    if int(samples_per_symbol) != samples_per_symbol or samples_per_symbol < 4 or samples_per_symbol % 4:
        raise ValueError("samples_per_symbol must be a positive multiple of four")
    allowed = DOWNLINK if direction == "downlink" else UPLINK
    def expand(value, name):
        result = [value] * 8 if np.isscalar(value) else list(value)
        if len(result) != 8:
            raise ValueError(f"{name} must have eight slots")
        return result
    types = expand(burst_type, "burst_type")
    if any(t not in allowed for t in types):
        raise ValueError("invalid burst_type for direction")
    attenuation, tsc = expand(attenuation, "attenuation"), expand(tsc, "tsc")
    if any(not np.isfinite(x) or x < 0 for x in attenuation):
        raise ValueError("attenuation must be finite and nonnegative")
    if any(int(x) != x or not 0 <= x <= 7 for x in tsc):
        raise ValueError("tsc must contain integers 0..7")
    if rise_time < 1/samples_per_symbol or fall_time < 1/samples_per_symbol or rise_time-rise_delay+fall_time+fall_delay >= 9.25:
        raise ValueError("invalid ramp duration")
    return {"direction": direction, "samples_per_symbol": int(samples_per_symbol),
            "burst_type": types, "attenuation": attenuation, "tsc": tsc,
            "rise_time": float(rise_time), "fall_time": float(fall_time),
            "rise_delay": float(rise_delay), "fall_delay": float(fall_delay)}


def gsmDownlinkConfig(**kwargs):
    return _config("downlink", **kwargs)


def gsmUplinkConfig(**kwargs):
    return _config("uplink", **kwargs)


def gsmInfo(cfg):
    sps = int(cfg["samples_per_symbol"])
    if cfg.get("direction") not in ("downlink", "uplink") or sps < 4 or sps % 4:
        raise ValueError("valid GSM configuration required")
    return {"symbol_rate": SYMBOL_RATE, "sample_rate": SYMBOL_RATE*sps,
            "bandwidth_time_product": .3, "burst_length_symbols": BURST_SYMBOLS,
            "num_bursts_per_frame": 8, "burst_length_samples": int(BURST_SYMBOLS*sps),
            "frame_length_samples": int(8*BURST_SYMBOLS*sps)}


def gsmFrame(cfg, num_frames: int = 1, burst_bits=None, seed: int = 0):
    if int(num_frames) != num_frames or num_frames < 1:
        raise ValueError("num_frames must be positive")
    info = gsmInfo(cfg)
    sps, length = cfg["samples_per_symbol"], info["burst_length_samples"]
    rng = np.random.default_rng(seed)
    provided = None if burst_bits is None else np.asarray(burst_bits, int)
    if provided is not None and (provided.shape != (8, 148) or np.any((provided != 0) & (provided != 1))):
        raise ValueError("burst_bits must be a binary [8,148] array")
    bursts = []
    for _ in range(num_frames):
        for slot, kind in enumerate(cfg["burst_type"]):
            if kind == "Off":
                bursts.append(np.zeros(length, complex))
                continue
            if kind == "FB":
                bits = np.zeros(148, int)
            elif kind == "Dummy":
                bits = np.tile([0, 1], 74)
            else:
                bits = rng.integers(0, 2, 148) if provided is None else provided[slot]
            nrz = 2*np.repeat(bits, sps) - 1
            shaped = gaussian_filter1d(nrz.astype(float), max(1, .3*sps), mode="nearest")
            phase = np.cumsum(shaped) * np.pi / (2*sps)
            waveform = np.zeros(length, complex)
            waveform[:len(phase)] = np.exp(1j*phase)
            ramp = max(1, round(cfg["rise_time"]*sps))
            fall = max(1, round(cfg["fall_time"]*sps))
            waveform[:ramp] *= np.sin(np.linspace(0, np.pi/2, ramp))
            waveform[len(phase)-fall:len(phase)] *= np.cos(np.linspace(0, np.pi/2, fall))
            waveform *= 10 ** (-cfg["attenuation"][slot] / 20)
            bursts.append(waveform)
    return {"waveform": np.concatenate(bursts), "info": info}


def gsmCheckTimeMask(cfg, waveform=None):
    data = gsmFrame(cfg)["waveform"] if waveform is None else np.asarray(waveform, complex).reshape(-1)
    info = gsmInfo(cfg)
    if len(data) % info["burst_length_samples"]:
        raise ValueError("waveform length must contain complete bursts")
    sps, n = cfg["samples_per_symbol"], info["burst_length_samples"]
    checks = []
    for slot, block in enumerate(data.reshape(-1, n)):
        kind = cfg["burst_type"][slot % 8]
        if kind == "Off":
            checks.append(bool(np.max(abs(block)) <= 1e-8))
        else:
            level = 10 ** (-cfg["attenuation"][slot % 8]/20)
            center = abs(block[10*sps:100*sps])
            checks.append(bool(np.max(center) <= level*1.01 and np.mean(center) >= level*.8))
    return {"pass": all(checks), "burst_pass": checks}


if __name__ == "__main__":
    run_cli("Stateless GSM TDMA slices", {
        "gsmDownlinkBurstType": gsmDownlinkBurstType,
        "gsmUplinkBurstType": gsmUplinkBurstType,
        "gsmDownlinkConfig": gsmDownlinkConfig,
        "gsmUplinkConfig": gsmUplinkConfig,
        "gsmInfo": gsmInfo, "gsmFrame": gsmFrame,
        "gsmCheckTimeMask": gsmCheckTimeMask,
    })
