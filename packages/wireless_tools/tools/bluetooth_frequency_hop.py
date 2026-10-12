"""Bluetooth BR/EDR 79-channel frequency-hop kernel for all 11 sequences."""
from __future__ import annotations

from _bluetooth_common import InputError, run_cli


SEQUENCES = (
    "Page scan", "Inquiry scan", "Page", "Inquiry", "Central page response",
    "Peripheral page response", "Inquiry response", "Connection basic",
    "Connection adaptive", "Interlaced page scan", "Interlaced inquiry scan",
)
REGISTER_BANK = list(range(0, 79, 2)) + list(range(1, 79, 2))
STAGES = [(3, 4), (5, 2), (4, 2), (3, 1), (5, 2), (4, 1), (2, 1),
          (5, 3), (4, 2), (5, 1), (2, 1), (4, 3), (3, 2), (5, 4)]
DEFAULTS = {"device_address": "9E8B33", "sequence_type": "Inquiry",
            "interlace_offset": 16, "k_nudge": 0, "k_offset": 24,
            "counter": 0, "used_channels": list(range(79))}


def _integer(value, key: str, low: int, high: int):
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise InputError(f"{key} must be an integer in {low}..{high}")


def configuration(properties: dict | None = None) -> dict:
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("configuration must be an object")
    unknown = set(properties) - set(DEFAULTS)
    if unknown:
        raise InputError("unsupported fields: " + ", ".join(sorted(unknown)))
    cfg = {**DEFAULTS, **properties}
    addr = cfg["device_address"]
    if not isinstance(addr, str) or not 1 <= len(addr) <= 12 or any(c not in "0123456789abcdefABCDEF" for c in addr):
        raise InputError("device_address must contain 1..12 hexadecimal digits")
    cfg["device_address"] = addr.upper()
    if cfg["sequence_type"] not in SEQUENCES:
        raise InputError("unsupported sequence_type")
    _integer(cfg["interlace_offset"], "interlace_offset", 0, 31)
    _integer(cfg["k_nudge"], "k_nudge", 0, 1 << 28)
    if cfg["k_nudge"] % 2:
        raise InputError("k_nudge must be even")
    if cfg["k_offset"] not in (8, 24):
        raise InputError("k_offset must be 8 or 24")
    _integer(cfg["counter"], "counter", 0, 1 << 28)
    channels = cfg["used_channels"]
    if not isinstance(channels, list):
        raise InputError("used_channels must be a list")
    for channel in channels:
        _integer(channel, "used_channels element", 0, 78)
    cfg["used_channels"] = sorted(set(channels))
    if len(cfg["used_channels"]) < 20:
        raise InputError("used_channels requires at least 20 distinct channels")
    return cfg


def _bits(number: int, width: int) -> list[int]:
    return [(number >> shift) & 1 for shift in range(width - 1, -1, -1)]


def _value(bits: list[int]) -> int:
    result = 0
    for bit in bits:
        result = (result << 1) | bit
    return result


def _parse_clock(value) -> int:
    if isinstance(value, str):
        if not 1 <= len(value) <= 7 or any(c not in "0123456789abcdefABCDEF" for c in value):
            raise InputError("clock must contain 1..7 hexadecimal digits")
        return int(value, 16)
    _integer(value, "clock", 0, (1 << 28) - 1)
    return value


def next_hop(properties: dict, clock) -> dict:
    cfg = configuration(properties)
    a = _bits(int(cfg["device_address"], 16), 48)
    c = _bits(_parse_clock(clock), 28)
    # MATLAB source indices below are one-based; these slices are zero-based.
    b = a[25:29]
    e = _value([a[i - 1] for i in (35, 37, 39, 41, 43, 45, 47)])
    addr_a = a[20:25]
    addr_c = [a[i - 1] for i in (40, 42, 44, 46, 48)]
    addr_d = a[29:38]
    kind = cfg["sequence_type"]
    scan_x = _value(c[11:16])
    y1, y2, f, f_prime = 0, 0, 0, 0
    mapping = [channel for channel in REGISTER_BANK if channel in cfg["used_channels"]]
    if kind in {"Page scan", "Inquiry scan", "Interlaced page scan", "Interlaced inquiry scan"}:
        x = scan_x
        if kind == "Interlaced page scan":
            x = (x + cfg["interlace_offset"]) % 32
        elif kind == "Interlaced inquiry scan":
            x = (x + cfg["counter"] + cfg["interlace_offset"]) % 32
    elif kind in {"Page", "Inquiry", "Central page response",
                  "Peripheral page response", "Inquiry response"}:
        if kind == "Peripheral page response" or kind == "Inquiry response":
            x = (scan_x + cfg["counter"]) % 32
        else:
            high = _value(c[23:26] + [c[27]])
            x = (scan_x + cfg["k_nudge"] + cfg["k_offset"]
                 + (high - scan_x) % 16
                 + (cfg["counter"] if kind == "Central page response" else 0)) % 32
        y1 = 1 if kind == "Inquiry response" else c[26]
        y2 = 32 * y1
    else:
        x = _value(c[21:26])
        y1, y2 = c[26], 32 * c[26]
        addr_a = [u ^ v for u, v in zip(addr_a, c[2:7])]
        addr_c = [u ^ v for u, v in zip(addr_c, c[7:12])]
        addr_d = [u ^ v for u, v in zip(addr_d, c[12:21])]
        clock_upper = _value(c[:21])
        f = (16 * clock_upper) % 79
        if kind == "Connection adaptive":
            f_prime = 16 * (clock_upper % len(mapping))
    z_prime = _bits((x + _value(addr_a)) % 32, 5)
    z = [z_prime[0]] + [u ^ v for u, v in zip(b, z_prime[1:])]
    p = [u ^ y1 for u in addr_c] + addr_d
    perm = z.copy()
    for index, (left, right) in enumerate(STAGES):
        if p[index]:
            left -= 1
            right -= 1
            perm[left], perm[right] = perm[right], perm[left]
    perm_value = _value(perm)
    register_index = (perm_value + e + f + y2) % 79
    channel = REGISTER_BANK[register_index]
    if kind == "Connection adaptive" and channel not in mapping:
        channel = mapping[(perm_value + e + f_prime + y2) % len(mapping)]
    return {"channel_index": channel, "x": x}


def _handler(_args, request):
    operation = request.get("operation", "hop")
    if operation == "config":
        return {"result": {"configuration": configuration(request.get("configuration"))}}
    if operation == "hop":
        return {"result": next_hop(request.get("configuration", {}), request.get("clock"))}
    raise InputError("operation must be config or hop")


if __name__ == "__main__":
    run_cli("bluetooth_frequency_hop", _handler, description=__doc__)
