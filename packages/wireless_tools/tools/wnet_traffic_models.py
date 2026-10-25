"""Stateless deterministic schedules from public Wireless Network traffic classes."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import run_cli


def _count(value):
    if int(value) != value or not 1 <= value <= 10000:
        raise ValueError("packet_count must be an integer in [1,10000]")
    return int(value)


def _payload(size, application_data):
    if application_data is None:
        return [1] * size
    data = np.asarray(application_data, int).reshape(-1)
    if np.any((data < 0) | (data > 255)):
        raise ValueError("application_data values must be bytes")
    return data[:size].tolist() + [0] * max(0, size-len(data))


def networkTrafficFTP(packet_count: int = 10, seed: int = 0,
                      fixed_file_size_mb=None, lognormal_mu: float = 14.45,
                      lognormal_sigma: float = .35, upper_limit_mb: float = 5,
                      reading_time_ms=None, exponential_mean_ms: float = 180000,
                      poisson_mean=None, packet_interval_ms: float = 0,
                      max_packet_size: int = 1460, application_data=None,
                      include_payload: bool = False):
    count = _count(packet_count)
    if fixed_file_size_mb is not None and fixed_file_size_mb <= 0:
        raise ValueError("fixed_file_size_mb must be positive")
    if max_packet_size not in (536, 1460) or upper_limit_mb <= 0 or packet_interval_ms < 0:
        raise ValueError("max_packet_size must be 536 or 1460; limits and intervals must be nonnegative")
    rng = np.random.default_rng(seed)
    packets, time_ms, file_id, remaining = [], 0.0, 0, 0
    for _ in range(count):
        if remaining == 0:
            file_id += 1
            if fixed_file_size_mb is not None:
                remaining = round(fixed_file_size_mb * 1e6)
            else:
                if lognormal_sigma <= 0 or lognormal_mu <= 0:
                    raise ValueError("positive lognormal parameters required")
                for _attempt in range(10000):
                    remaining = round(rng.lognormal(lognormal_mu, lognormal_sigma))
                    if 0 < remaining <= upper_limit_mb * 1e6:
                        break
                else:
                    raise ValueError("truncated lognormal file-size sampling failed")
        data_size = min(max_packet_size, remaining)
        record = {"time_ms": round(time_ms, 9), "size_bytes": data_size + 40,
                  "file_id": file_id, "payload_bytes": data_size}
        if include_payload:
            record["payload"] = _payload(data_size, application_data)
        packets.append(record)
        remaining -= data_size
        if remaining:
            time_ms += packet_interval_ms
        else:
            if reading_time_ms is not None:
                if reading_time_ms < 0:
                    raise ValueError("reading_time_ms must be nonnegative")
                time_ms += reading_time_ms
            elif poisson_mean is not None:
                time_ms += float(rng.poisson(poisson_mean))
            else:
                time_ms += float(rng.exponential(exponential_mean_ms))
    return {"packets": packets, "next_time_ms": time_ms,
            "remaining_file_bytes": remaining, "model": "FTP"}


def networkTrafficOnOff(packet_count: int = 10, seed: int = 0,
                        on_time_s=None, off_time_s=None,
                        on_exponential_mean_s: float = 1,
                        off_exponential_mean_s: float = 2,
                        data_rate_kbps: float = 5, packet_size: int = 1500,
                        application_data=None, include_payload: bool = False):
    count = _count(packet_count)
    if data_rate_kbps < 1 or int(packet_size) != packet_size or packet_size < 1:
        raise ValueError("positive packet size and data_rate_kbps >= 1 required")
    if on_time_s is not None and on_time_s <= 0 or off_time_s is not None and off_time_s < 0:
        raise ValueError("on_time_s must be positive and off_time_s nonnegative")
    rng = np.random.default_rng(seed)
    active_needed = packet_size * 8 / (data_rate_kbps*1000)
    time_s, on_remaining = 0.0, 0.0
    packets = []
    for _ in range(count):
        active_left = active_needed
        while active_left > 1e-12:
            if on_remaining <= 1e-12:
                on_remaining = (on_time_s if on_time_s is not None else
                                float(rng.exponential(on_exponential_mean_s)))
                if on_remaining <= 0:
                    raise ValueError("on-state duration must be positive")
            chunk = min(active_left, on_remaining)
            time_s += chunk
            active_left -= chunk
            on_remaining -= chunk
            if on_remaining <= 1e-12:
                off = off_time_s if off_time_s is not None else float(rng.exponential(off_exponential_mean_s))
                time_s += off
        record = {"time_ms": round(time_s*1000, 9), "size_bytes": int(packet_size), "state": "on"}
        if include_payload:
            record["payload"] = _payload(int(packet_size), application_data)
        packets.append(record)
    return {"packets": packets, "next_time_ms": time_s*1000, "model": "OnOff"}


def networkTrafficVideoConference(packet_count: int = 10, seed: int = 0,
                                  frame_interval_ms: float = 40,
                                  frame_size_method="WeibullDistribution",
                                  fixed_frame_size: int = 5000,
                                  weibull_scale: float = 6950, weibull_shape: float = .8099,
                                  has_jitter: bool = True, gamma_shape: float = .2463,
                                  gamma_scale: float = 60.227, protocol_overhead: int = 28,
                                  application_data=None, include_payload: bool = False):
    count = _count(packet_count)
    if frame_interval_ms <= 0 or not 0 <= protocol_overhead < 1500 or fixed_frame_size < 1:
        raise ValueError("positive frame interval/size and protocol overhead in [0,1500) required")
    if frame_size_method not in ("FixedSize", "WeibullDistribution"):
        raise ValueError("invalid frame_size_method")
    rng = np.random.default_rng(seed)
    payload_max = 1500-protocol_overhead
    frame_id, remaining, time_ms, segment = 0, 0, 0.0, 0
    packets = []
    while len(packets) < count:
        if remaining == 0:
            frame_id += 1
            segment = 0
            remaining = (int(fixed_frame_size) if frame_size_method == "FixedSize" else
                         min(15000, max(1, round(rng.weibull(weibull_shape)*weibull_scale))))
        segment += 1
        used = min(remaining, payload_max)
        record = {"time_ms": round(time_ms, 9), "size_bytes": used+protocol_overhead,
                  "payload_bytes": used, "frame_id": frame_id, "segment": segment}
        if include_payload:
            record["payload"] = _payload(used, application_data)
        packets.append(record)
        remaining -= used
        if remaining == 0:
            time_ms += frame_interval_ms
        elif has_jitter:
            time_ms += min(frame_interval_ms/max(1, np.ceil((remaining+used)/payload_max)),
                           float(rng.gamma(gamma_shape, gamma_scale)))
    return {"packets": packets, "next_time_ms": time_ms, "model": "VideoConference"}


def networkTrafficVoIP(packet_count: int = 10, seed: int = 0,
                       exponential_mean_ms: float = 1250,
                       has_jitter: bool = True,
                       laplace_scale: float = 5.11, laplace_mu: float = 0,
                       application_data=None, include_payload: bool = False):
    count = _count(packet_count)
    if exponential_mean_ms < 0 or laplace_scale <= 0:
        raise ValueError("nonnegative state mean and positive Laplace scale required")
    rng = np.random.default_rng(seed)
    packets, time_ms, state, state_end = [], 0.0, "active", float(rng.exponential(exponential_mean_ms))
    for _ in range(count):
        if time_ms >= state_end:
            state = "silent" if state == "active" else "active"
            state_end = time_ms + float(rng.exponential(exponential_mean_ms))
        interval, size = (20, 36) if state == "active" else (160, 10)
        record = {"time_ms": round(time_ms, 9), "size_bytes": size, "state": state}
        if include_payload:
            record["payload"] = _payload(size, application_data)
        packets.append(record)
        jitter = float(rng.laplace(laplace_mu, laplace_scale) - laplace_mu) if has_jitter else 0.0
        time_ms += max(1, round(interval+jitter))
    return {"packets": packets, "next_time_ms": time_ms, "model": "VoIP"}


if __name__ == "__main__":
    run_cli("Wireless Network Toolbox traffic model slices", {
        "networkTrafficFTP": networkTrafficFTP,
        "networkTrafficOnOff": networkTrafficOnOff,
        "networkTrafficVideoConference": networkTrafficVideoConference,
        "networkTrafficVoIP": networkTrafficVoIP,
    })
