"""Non-GUI communication metadata, legacy helpers, and VITA 49 headers."""
from __future__ import annotations

import base64
import json
from pathlib import Path

import numpy as np

from _nr_remaining_common import complex_array, run_cli


def checkinp(values, defaults):
    if not isinstance(values, list) or not isinstance(defaults, list) or len(values) != len(defaults) or len(values) > 10:
        raise ValueError("values and defaults must be matching lists of at most ten elements")
    return {"values": [fallback if value is None or value == [] else value
                       for value, fallback in zip(values, defaults)]}


def intdump(x, nsamp: int):
    samples = complex_array(x)
    if samples.ndim not in (1, 2) or int(nsamp) != nsamp or nsamp < 1:
        raise ValueError("1-D or 2-D samples and positive integer nsamp required")
    if len(samples) % nsamp:
        raise ValueError("sample count must be divisible by nsamp")
    if samples.ndim == 1:
        return {"samples": samples.reshape(-1, nsamp).mean(axis=1)}
    return {"samples": samples.reshape(len(samples)//nsamp, nsamp, samples.shape[1]).mean(axis=1)}


def commlib():
    return {"library": "commlibv2", "kind": "Simulink Communications Toolbox library",
            "agent_interface": "See comms for Python tool entries"}


def comms():
    registry = Path(__file__).resolve().parents[1] / "tool_registry.json"
    entries = json.loads(registry.read_text(encoding="utf-8"))["tools"]
    return {"toolbox": "Communications Toolbox",
            "tools": [{"name": item["name"], "functions": item["source_functions"],
                       "status": item["status"]} for item in entries
                      if item["product"] == "Communications Toolbox"]}


def comm_links(blocks):
    if not isinstance(blocks, list):
        raise ValueError("blocks must be a list of system block descriptors")
    current, obsolete, unrelated = [], [], []
    for block in blocks:
        if not isinstance(block, dict) or "path" not in block or "library" not in block:
            raise ValueError("each block needs path and library")
        name = str(block["library"]).lower()
        if name == "commlibv2":
            current.append(block["path"])
        elif name.startswith("commlib"):
            obsolete.append(block["path"])
        else:
            unrelated.append(block["path"])
    return {"current": current, "obsolete": obsolete, "unrelated": unrelated}


def commprivate(function: str, params):
    if not isinstance(params, dict):
        raise ValueError("params must be a JSON object")
    allowed = {"checkinp": checkinp, "intdump": intdump}
    if function not in allowed:
        raise ValueError(f"supported private dispatcher functions: {sorted(allowed)}")
    return allowed[function](**params)


def vita49Reader(data_hex=None, data_base64=None, max_packets: int = 256):
    if (data_hex is None) == (data_base64 is None):
        raise ValueError("supply exactly one of data_hex or data_base64")
    raw = bytes.fromhex(data_hex) if data_hex is not None else base64.b64decode(data_base64, validate=True)
    if max_packets < 1:
        raise ValueError("max_packets must be positive")
    packets, offset = [], 0
    while offset < len(raw) and len(packets) < max_packets:
        if len(raw) - offset < 4:
            raise ValueError("truncated VITA 49 header")
        first, second, high, low = raw[offset:offset+4]
        kind = first >> 4
        if kind > 7:
            raise ValueError("invalid VITA 49 packet type")
        size_words = (high << 8) | low
        size = size_words * 4
        if size < 4 or offset + size > len(raw):
            raise ValueError("invalid or truncated VITA 49 packet size")
        has_stream = kind not in (0, 2)
        has_class = bool(first & 8)
        tsi, tsf = (second >> 6) & 3, (second >> 4) & 3
        prefix = 4 + 4*has_stream + 8*has_class + 4*bool(tsi) + 8*bool(tsf)
        trailer = 4 if kind <= 3 and first & 4 else 0
        if prefix + trailer > size:
            raise ValueError("packet shorter than declared optional fields")
        cursor = offset + 4
        stream = int.from_bytes(raw[cursor:cursor+4], "big") if has_stream else None
        cursor += 4*has_stream
        class_id = raw[cursor:cursor+8].hex() if has_class else None
        cursor += 8*has_class
        integer_timestamp = int.from_bytes(raw[cursor:cursor+4], "big") if tsi else None
        cursor += 4*bool(tsi)
        fractional_timestamp = int.from_bytes(raw[cursor:cursor+8], "big") if tsf else None
        packets.append({"type": kind, "class_id": class_id, "stream_id": stream,
                        "tsi": tsi, "tsf": tsf, "integer_timestamp": integer_timestamp,
                        "fractional_timestamp": fractional_timestamp,
                        "packet_count": second & 15, "size_words": size_words,
                        "payload_hex": raw[offset+prefix:offset+size-trailer].hex(),
                        "trailer_hex": raw[offset+size-trailer:offset+size].hex() if trailer else None})
        offset += size
    return {"packets": packets, "bytes_processed": offset, "remaining_bytes": len(raw)-offset}


if __name__ == "__main__":
    run_cli("Communications legacy and metadata slices", {
        "checkinp": checkinp, "intdump": intdump, "commlib": commlib,
        "comms": comms, "comm_links": comm_links, "commprivate": commprivate,
        "vita49Reader": vita49Reader,
    })
