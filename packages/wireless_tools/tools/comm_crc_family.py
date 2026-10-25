"""Standalone configurable polynomial CRC generation and detection."""
from __future__ import annotations

import re
import numpy as np

from _nr_remaining_common import bits, run_cli


def _polynomial(value):
    if isinstance(value, str):
        terms = re.findall(r"(?:[xz]\s*\^\s*(\d+)|\b([xz])\b|\b(1)\b)", value.lower())
        if not terms:
            raise ValueError("polynomial string must contain x/z powers and 1")
        powers = [int(degree) if degree else 1 if variable else 0 for degree, variable, _ in terms]
        degree = max(powers)
        coefficients = [int(k in powers) for k in range(degree, -1, -1)]
    else:
        coefficients = list(map(int, value))
    if len(coefficients) < 2 or coefficients[0] != 1 or coefficients[-1] != 1 or any(x not in (0, 1) for x in coefficients):
        raise ValueError("polynomial must be monic binary with nonzero constant")
    return coefficients


def crcConfig(polynomial="z^16 + z^12 + z^5 + 1", initial_conditions=0,
              final_xor=0, reflect_input_bytes=False, reflect_checksums=False,
              checksums_per_frame: int = 1, direct_method=False):
    coefficients = _polynomial(polynomial)
    width = len(coefficients) - 1
    if width > 64 or type(checksums_per_frame) is not int or checksums_per_frame < 1:
        raise ValueError("CRC width must be <=64 and checksums_per_frame positive")
    if direct_method:
        raise ValueError("direct_method is outside this polynomial-division slice")
    for value, name in ((initial_conditions, "initial_conditions"), (final_xor, "final_xor")):
        if isinstance(value, int):
            value = [value] * width
        if len(value) != width or any(int(v) not in (0, 1) for v in value):
            raise ValueError(f"{name} must be binary scalar or width-length vector")
    return {"polynomial": coefficients, "width": width,
            "initial_conditions": [initial_conditions] * width if isinstance(initial_conditions, int) else list(initial_conditions),
            "final_xor": [final_xor] * width if isinstance(final_xor, int) else list(final_xor),
            "reflect_input_bytes": bool(reflect_input_bytes),
            "reflect_checksums": bool(reflect_checksums),
            "checksums_per_frame": checksums_per_frame, "direct_method": False}


def _checksum(data, config):
    poly = config["polynomial"]
    width = config["width"]
    data = list(map(int, data))
    if config["reflect_input_bytes"]:
        if len(data) % 8:
            raise ValueError("reflected input must have a whole number of bytes")
        data = [bit for start in range(0, len(data), 8) for bit in data[start:start + 8][::-1]]
    work = config["initial_conditions"] + data + [0] * width
    for position in range(len(config["initial_conditions"]) + len(data)):
        if work[position]:
            for offset, bit in enumerate(poly):
                work[position + offset] ^= bit
    output = work[-width:]
    if config["reflect_checksums"]:
        output = output[::-1]
    return [a ^ b for a, b in zip(output, config["final_xor"])]


def _cfg(config):
    if config is None:
        return crcConfig()
    if not isinstance(config, dict):
        raise ValueError("config must be a crcConfig object")
    return crcConfig(**{key: value for key, value in config.items() if key != "width"})


def crcGenerate(message, config=None):
    cfg = _cfg(config)
    data = bits(message, "message")
    count = cfg["checksums_per_frame"]
    if len(data) % count:
        raise ValueError("message length must divide by checksums_per_frame")
    block = len(data) // count
    output = []
    for offset in range(0, len(data), block):
        segment = data[offset:offset + block].tolist()
        output.extend(segment + _checksum(segment, cfg))
    return {"codeword": output, "checksum_width": cfg["width"]}


def crcDetect(codeword, config=None):
    cfg = _cfg(config)
    data = bits(codeword, "codeword")
    count, width = cfg["checksums_per_frame"], cfg["width"]
    if len(data) % count or len(data) // count <= width:
        raise ValueError("codeword does not fit checksums_per_frame")
    block = len(data) // count
    message, errors = [], []
    for offset in range(0, len(data), block):
        part = data[offset:offset + block].tolist()
        payload, received = part[:-width], part[-width:]
        message.extend(payload)
        errors.append(received != _checksum(payload, cfg))
    return {"message": message, "errors": errors, "valid": not any(errors)}


if __name__ == "__main__":
    run_cli("Standalone configurable CRC polynomial slices", {
        "crcConfig": crcConfig, "crcGenerate": crcGenerate, "crcDetect": crcDetect,
    })
