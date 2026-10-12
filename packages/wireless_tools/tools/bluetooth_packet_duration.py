"""Compute Bluetooth BR/EDR and LE packet duration (MATLAB compatible)."""
from __future__ import annotations

from _bluetooth_common import InputError, run_cli


_PACKETS = {
    "BR": {"ID", "NULL", "POLL", "FHS", "DM1", "DH1", "DM3", "DH3", "DM5", "DH5", "HV1", "HV2", "HV3", "EV3", "DV", "EV4", "EV5", "AUX1"},
    "EDR2M": {"ID", "NULL", "POLL", "FHS", "DM1", "2-DH1", "2-DH3", "2-DH5", "2-EV3", "2-EV5", "AUX1"},
    "EDR3M": {"ID", "NULL", "POLL", "FHS", "DM1", "3-DH1", "3-DH3", "3-DH5", "3-EV3", "3-EV5", "AUX1"},
}
_FIXED = {"ID": 0, "NULL": 0, "POLL": 0, "FHS": 18, "HV1": 10, "HV2": 20, "HV3": 30}
_LIMITS = {
    "DM1": (0, 17), "DH1": (0, 27), "DM3": (0, 121), "DH3": (0, 183), "DM5": (0, 224), "DH5": (0, 339),
    "EV3": (1, 30), "EV4": (1, 120), "EV5": (1, 180), "DV": (10, 19), "AUX1": (0, 29),
    "2-DH1": (0, 54), "2-DH3": (0, 367), "2-DH5": (0, 679), "2-EV3": (1, 60), "2-EV5": (1, 360),
    "3-DH1": (0, 83), "3-DH3": (0, 552), "3-DH5": (0, 1021), "3-EV3": (1, 90), "3-EV5": (1, 540),
}


def packet_duration(mode: str, packet_type: str, payload_length: int, cte_length: int | None = None) -> tuple[float, int]:
    if mode not in {"BR", "EDR2M", "EDR3M", "LE1M", "LE2M", "LE500K", "LE125K"}:
        raise InputError("mode must be BR, EDR2M, EDR3M, LE1M, LE2M, LE500K, or LE125K")
    if not isinstance(payload_length, int) or isinstance(payload_length, bool) or payload_length < 0:
        raise InputError("payload_length must be a nonnegative integer")
    if mode in _PACKETS:
        if packet_type not in _PACKETS[mode]:
            raise InputError(f"packet_type {packet_type!r} is invalid for {mode}")
        if packet_type in _FIXED and payload_length != _FIXED[packet_type]:
            raise InputError(f"{mode} {packet_type} requires payload_length={_FIXED[packet_type]}")
        if packet_type in _LIMITS:
            low, high = _LIMITS[packet_type]
            if not low <= payload_length <= high:
                raise InputError(f"{mode} {packet_type} payload_length must be in {low}..{high}")
        header = 8 * int(packet_type in {"DM1", "DH1", "AUX1", "DV"}) + 16 * int(packet_type in {"DM3", "DH3", "DM5", "DH5", "2-DH1", "2-DH3", "2-DH5", "3-DH1", "3-DH3", "3-DH5"})
        crc = 16 * int(packet_type in {"FHS", "DM1", "DH1", "DM3", "DH3", "DM5", "DH5", "2-DH1", "2-DH3", "2-DH5", "3-DH1", "3-DH3", "3-DH5", "DV", "EV3", "EV4", "EV5", "2-EV3", "2-EV5", "3-EV3", "3-EV5"})
        data = header + 8 * payload_length + crc
        if packet_type in {"DM1", "HV2", "DM3", "DM5", "EV4", "FHS", "DV"}:
            padded = data + (-data % 10)
            fec = (80 + (padded - 80) * 3 // 2) if packet_type == "DV" else padded * 3 // 2
        elif packet_type == "HV1":
            fec = data * 3
        else:
            fec = data
        access = 68 + 4 * int(packet_type != "ID")
        header_bits = 54 * int(packet_type != "ID")
        ah = access + header_bits
        if mode == "BR":
            duration = access if packet_type == "ID" else ah if packet_type in {"NULL", "POLL"} else ah + fec
            return float(duration), duration
        if packet_type in {"ID", "NULL", "POLL"}:
            return float(ah), ah
        k = 3 if mode == "EDR3M" else 2
        edr = 11 * k + fec + 2 * k
        edr += -edr % k
        return float(ah + 5 + edr // k), ah + 5 + edr
    valid_le = {"Disabled"} if mode in {"LE125K", "LE500K"} else {"Disabled", "ConnectionCTE", "ConnectionlessCTE"}
    if packet_type not in valid_le or payload_length > 255:
        raise InputError(f"packet_type or payload_length is invalid for {mode}")
    if cte_length is not None and (mode not in {"LE1M", "LE2M"} or packet_type == "Disabled" or not isinstance(cte_length, int) or not 2 <= cte_length <= 20):
        raise InputError("cte_length is only valid for LE1M/LE2M ConnectionCTE or ConnectionlessCTE and must be 2..20")
    if mode in {"LE1M", "LE2M"}:
        factor, preamble = (1, 8) if mode == "LE1M" else (2, 16)
        cte = 0 if packet_type == "Disabled" else (cte_length or 2) * 8 * factor
        header = 16 + 8 * int(packet_type == "ConnectionCTE")
        total = preamble + 32 + header + 8 * payload_length + cte + 24
        return total / factor, total
    first = (32 + 2 + 3) * 2 * 4
    second = (16 + 8 * payload_length + 24 + 3) * 2 * (4 if mode == "LE125K" else 1)
    total = 80 + first + second
    return float(total), total


def _handler(_args, request):
    duration, num_bits = packet_duration(request.get("mode"), request.get("packet_type"), request.get("payload_length"), request.get("cte_length"))
    return {"result": {"duration_us": duration, "num_bits": num_bits}}


if __name__ == "__main__":
    run_cli("bluetooth_packet_duration", _handler, description=__doc__)
