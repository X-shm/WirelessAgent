"""Headless IQ and event logging operations for Wireless Network Toolbox."""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np
from scipy.signal import resample_poly

from _nr_remaining_common import run_cli


EVENT_NAMES = {"TransmissionStarted", "ReceptionEnded", "AppPacketGenerated", "AppPacketReceived"}


def wireless_network_event_tracer(events, event_name=None, node_id=None,
                                  start_time_s=None, end_time_s=None, max_events=1000000):
    if not isinstance(events, list) or not isinstance(max_events, int) or max_events < 1:
        raise ValueError("events must be an array and max_events a positive integer")
    if event_name is not None:
        selected = {event_name} if isinstance(event_name, str) else set(event_name)
        if not selected <= EVENT_NAMES:
            raise ValueError("unknown event name")
    else:
        selected = EVENT_NAMES
    node_ids = None if node_id is None else ({node_id} if isinstance(node_id, int) else set(node_id))
    if start_time_s is not None and (not math.isfinite(start_time_s) or start_time_s < 0):
        raise ValueError("start_time_s must be nonnegative")
    if end_time_s is not None and (not math.isfinite(end_time_s) or end_time_s < 0):
        raise ValueError("end_time_s must be nonnegative")
    if start_time_s is not None and end_time_s is not None and start_time_s > end_time_s:
        raise ValueError("start_time_s exceeds end_time_s")
    filtered = []
    for event in events[:max_events]:
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        timestamp = float(event.get("Timestamp", -1))
        if not math.isfinite(timestamp) or timestamp < 0:
            raise ValueError("event Timestamp must be nonnegative and finite")
        if event.get("EventName") not in selected:
            continue
        if node_ids is not None and event.get("NodeID") not in node_ids:
            continue
        if start_time_s is not None and timestamp < start_time_s:
            continue
        if end_time_s is not None and timestamp > end_time_s:
            continue
        # MATLAB's tracer excludes packet/PDU bytes from the event log.
        cleaned = {k: v for k, v in event.items() if k not in ("Payload", "PacketOctets", "PDUOctets")}
        if isinstance(cleaned.get("EventData"), dict):
            cleaned["EventData"] = {k: v for k, v in cleaned["EventData"].items()
                                    if k not in ("Payload", "PacketOctets", "PDUOctets")}
        filtered.append(cleaned)
    filtered.sort(key=lambda event: event["Timestamp"])
    return {"events": filtered, "count": len(filtered), "truncated": len(events) > max_events}


def wireless_iq_logger(node_id, samples, input_sample_rate_hz,
                       sample_rate_hz=None, start_time_s=0,
                       center_frequency_hz=None, bandwidth_hz=None):
    if not isinstance(node_id, int) or isinstance(node_id, bool) or node_id < 1:
        raise ValueError("node_id must be a positive integer")
    if not math.isfinite(input_sample_rate_hz) or input_sample_rate_hz < 1e6:
        raise ValueError("input_sample_rate_hz must be at least 1 MHz")
    rate = input_sample_rate_hz if sample_rate_hz is None else sample_rate_hz
    if not math.isfinite(rate) or rate < 1e6:
        raise ValueError("sample_rate_hz must be at least 1 MHz")
    if not math.isfinite(start_time_s) or start_time_s < 0:
        raise ValueError("start_time_s must be nonnegative")
    for value, name in ((center_frequency_hz, "center_frequency_hz"), (bandwidth_hz, "bandwidth_hz")):
        if value is not None and (not math.isfinite(value) or value <= 0):
            raise ValueError(f"{name} must be positive and finite")
    if isinstance(samples, dict) and "real" in samples:
        real = np.asarray(samples["real"], dtype=float)
        imag = np.asarray(samples.get("imag", np.zeros_like(real)), dtype=float)
        if real.shape != imag.shape:
            raise ValueError("sample real/imag lengths differ")
        iq = real + 1j * imag
    else:
        raw = np.asarray(samples, dtype=float)
        if raw.ndim != 2 or raw.shape[1] != 2:
            raise ValueError("samples must be {real,imag} arrays or [real,imag] pairs")
        iq = raw[:, 0] + 1j * raw[:, 1]
    if iq.ndim != 1 or not 1 <= iq.size <= 1000000 or not np.all(np.isfinite(iq)):
        raise ValueError("samples must be a finite vector of 1..1000000 samples")
    if rate != input_sample_rate_hz:
        ratio = Fraction(rate / input_sample_rate_hz).limit_denominator(10000)
        if abs(float(ratio) - rate / input_sample_rate_hz) > 1e-9:
            raise ValueError("sample rate ratio needs a rational approximation with denominator <= 10000")
        iq = resample_poly(iq, ratio.numerator, ratio.denominator)
    return {"node_id": node_id, "sample_rate_hz": rate,
            "input_sample_rate_hz": input_sample_rate_hz,
            "start_time_s": start_time_s, "center_frequency_hz": center_frequency_hz,
            "bandwidth_hz": bandwidth_hz, "sample_count": iq.size,
            "duration_s": iq.size / rate,
            "samples": {"real": iq.real.tolist(), "imag": iq.imag.tolist()}}


if __name__ == "__main__":
    run_cli("Wireless Network Toolbox headless event and IQ logging", {
        "wirelessNetworkEventTracer": wireless_network_event_tracer,
        "wirelessIQLogger": wireless_iq_logger,
    })
