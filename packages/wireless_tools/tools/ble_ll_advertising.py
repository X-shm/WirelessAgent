"""BLE Link Layer advertising-channel PDU configuration, encoder and decoder."""
from __future__ import annotations

import numpy as np

from _bluetooth_algorithms import crc24_ble
from _bluetooth_common import InputError, run_cli
from ble_l2cap import _hex_bytes, _int


PDU_TYPES = [
    "Advertising indication", "Advertising direct indication",
    "Advertising non connectable indication", "Scan request", "Scan response",
    "Connection indication", "Advertising scannable indication",
]
SCA = ["251 to 500 ppm", "151 to 250 ppm", "101 to 150 ppm", "76 to 100 ppm",
       "51 to 75 ppm", "31 to 50 ppm", "21 to 30 ppm", "0 to 20 ppm"]
DEFAULTS = {
    "pdu_type": PDU_TYPES[0], "channel_selection": "Algorithm1",
    "advertiser_address_type": "Random", "advertiser_address": "0123456789AB",
    "target_address_type": "Random", "target_address": "0123456789CD",
    "scanner_address_type": "Random", "scanner_address": "0123456789CD",
    "initiator_address_type": "Random", "initiator_address": "0123456789CD",
    "advertising_data": "020106", "scan_response_data": "020106",
    "access_address": "01234567", "crc_initialization": "012345",
    "window_size": 1, "window_offset": 0, "connection_interval": 6,
    "peripheral_latency": 0, "connection_timeout": 10,
    "used_channels": list(range(37)), "hop_increment": 5,
    "sleep_clock_accuracy": SCA[0],
}
STATUS = {"Success": 0, "CRCFailed": -1, "LLPDULengthMismatch": -2,
          "InvalidLLPeripheralLatency": -3, "InvalidLLConnectionTimeout": -4,
          "InvalidLLWindowSize": -5, "InvalidLLWindowOffset": -6,
          "InvalidLLConnectionInterval": -7, "InvalidLLChannelMap": -8,
          "IncompleteLLAdvertisingChannelPDU": -51,
          "InvalidLLHopIncrement": -52, "InvalidLLAdvertisingDataLength": -53,
          "InvalidLLScanResponseDataLength": -54,
          "UnsupportedLLAdvertisingPDUType": -55}


def configuration(properties: dict | None = None) -> dict:
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("configuration must be a JSON object")
    unknown = set(properties) - set(DEFAULTS)
    if unknown:
        raise InputError("unsupported configuration fields: " + ", ".join(sorted(unknown)))
    cfg = {**DEFAULTS, **properties}
    if cfg["pdu_type"] not in PDU_TYPES:
        raise InputError("unsupported pdu_type")
    if cfg["channel_selection"] not in ("Algorithm1", "Algorithm2"):
        raise InputError("channel_selection must be Algorithm1 or Algorithm2")
    for name in ("advertiser", "target", "scanner", "initiator"):
        if cfg[f"{name}_address_type"] not in ("Public", "Random"):
            raise InputError(f"{name}_address_type must be Public or Random")
        cfg[f"{name}_address"] = _hex_bytes(cfg[f"{name}_address"], f"{name}_address", length=6).hex().upper()
    for name, length in (("access_address", 4), ("crc_initialization", 3)):
        cfg[name] = _hex_bytes(cfg[name], name, length=length).hex().upper()
    for name in ("advertising_data", "scan_response_data"):
        data = _hex_bytes(cfg[name], name)
        if len(data) > 31:
            raise InputError(f"{name} must contain at most 31 octets")
        cfg[name] = data.hex().upper()
    for name, low, high in (("window_size", 1, 8), ("window_offset", 0, 3200),
                            ("connection_interval", 6, 3200), ("peripheral_latency", 0, 499),
                            ("connection_timeout", 10, 3200), ("hop_increment", 5, 16)):
        _int(cfg[name], name, low, high)
    channels = cfg["used_channels"]
    if not isinstance(channels, list):
        raise InputError("used_channels must be a list")
    for channel in channels:
        _int(channel, "used_channels element", 0, 36)
    channels = sorted(set(channels))
    if len(channels) < 2:
        raise InputError("used_channels requires at least two distinct channels")
    cfg["used_channels"] = channels
    if cfg["sleep_clock_accuracy"] not in SCA:
        raise InputError("unsupported sleep_clock_accuracy")
    return cfg


def _connection_error(cfg: dict) -> str | None:
    interval, latency, timeout = (cfg[key] for key in
                                  ("connection_interval", "peripheral_latency", "connection_timeout"))
    if latency > timeout * 10 / (interval * 1.25 * 2) - 1:
        return "InvalidLLPeripheralLatency"
    if timeout <= (1 + latency) * interval * 1.25 * 2 / 10:
        return "InvalidLLConnectionTimeout"
    if cfg["window_size"] > min(8, interval - 1):
        return "InvalidLLWindowSize"
    if cfg["window_offset"] > interval:
        return "InvalidLLWindowOffset"
    return None


def _address(hex_string: str) -> bytes:
    return bytes.fromhex(hex_string)[::-1]


def _bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder="little")


def _pack(bits: np.ndarray) -> bytes:
    return np.packbits(bits, bitorder="little").tobytes()


def encode(properties: dict) -> bytes:
    cfg = configuration(properties)
    kind = cfg["pdu_type"]
    code = PDU_TYPES.index(kind)
    if kind == "Connection indication":
        error = _connection_error(cfg)
        if error:
            raise InputError(error)
        bitmap = sum(1 << channel for channel in cfg["used_channels"])
        payload = (_address(cfg["initiator_address"]) + _address(cfg["advertiser_address"])
                   + _address(cfg["access_address"]) + _address(cfg["crc_initialization"])
                   + cfg["window_size"].to_bytes(1, "little")
                   + cfg["window_offset"].to_bytes(2, "little")
                   + cfg["connection_interval"].to_bytes(2, "little")
                   + cfg["peripheral_latency"].to_bytes(2, "little")
                   + cfg["connection_timeout"].to_bytes(2, "little")
                   + bitmap.to_bytes(5, "little")
                   + bytes((cfg["hop_increment"] | (SCA.index(cfg["sleep_clock_accuracy"]) << 5),)))
    elif kind == "Advertising direct indication":
        payload = _address(cfg["advertiser_address"]) + _address(cfg["target_address"])
    elif kind == "Scan request":
        payload = _address(cfg["scanner_address"]) + _address(cfg["advertiser_address"])
    elif kind == "Scan response":
        payload = _address(cfg["advertiser_address"]) + bytes.fromhex(cfg["scan_response_data"])
    else:
        payload = _address(cfg["advertiser_address"]) + bytes.fromhex(cfg["advertising_data"])
    tx_name = "scanner" if kind == "Scan request" else "initiator" if kind == "Connection indication" else "advertiser"
    rx_name = "target" if kind == "Advertising direct indication" else "advertiser" if kind in ("Scan request", "Connection indication") else None
    tx = int(cfg[f"{tx_name}_address_type"] == "Random")
    rx = int(cfg[f"{rx_name}_address_type"] == "Random") if rx_name else 0
    header = bytes((code | (int(cfg["channel_selection"] == "Algorithm2") << 5) | (tx << 6) | (rx << 7), len(payload)))
    content = header + payload
    return content + _pack(crc24_ble(_bits(content), 0x555555))


def _result(name: str, cfg: dict | None = None) -> dict:
    return {"status": name, "status_code": STATUS[name], "configuration": cfg}


def decode(pdu: bytes) -> dict:
    if len(pdu) < 5:
        return _result("IncompleteLLAdvertisingChannelPDU")
    if not np.array_equal(_bits(pdu[-3:]), crc24_ble(_bits(pdu[:-3]), 0x555555)):
        return _result("CRCFailed")
    header, length = pdu[0], pdu[1]
    code = header & 15
    if code >= len(PDU_TYPES):
        return _result("UnsupportedLLAdvertisingPDUType")
    if length != len(pdu) - 5:
        return _result("LLPDULengthMismatch")
    kind = PDU_TYPES[code]
    minimum = 34 if code == 5 else 12 if code in (1, 3) else 6
    if length < minimum:
        return _result("IncompleteLLAdvertisingChannelPDU")
    data = pdu[2:-3]
    cfg = configuration({"pdu_type": kind})
    cfg["channel_selection"] = "Algorithm2" if header & 32 else "Algorithm1"
    tx_type = "Random" if header & 64 else "Public"
    rx_type = "Random" if header & 128 else "Public"
    tx_name = "scanner" if code == 3 else "initiator" if code == 5 else "advertiser"
    cfg[f"{tx_name}_address_type"] = tx_type
    rx_name = "target" if code == 1 else "advertiser" if code in (3, 5) else None
    if rx_name:
        cfg[f"{rx_name}_address_type"] = rx_type
    address = lambda octets: octets[::-1].hex().upper()
    if code == 3:
        cfg["scanner_address"] = address(data[:6])
        cfg["advertiser_address"] = address(data[6:12])
    elif code == 5:
        cfg["initiator_address"] = address(data[:6])
        cfg["advertiser_address"] = address(data[6:12])
        cfg["access_address"] = address(data[12:16])
        cfg["crc_initialization"] = address(data[16:19])
        cfg["window_size"] = data[19]
        cfg["window_offset"] = int.from_bytes(data[20:22], "little")
        cfg["connection_interval"] = int.from_bytes(data[22:24], "little")
        cfg["peripheral_latency"] = int.from_bytes(data[24:26], "little")
        cfg["connection_timeout"] = int.from_bytes(data[26:28], "little")
        bitmap = int.from_bytes(data[28:33], "little")
        cfg["used_channels"] = [channel for channel in range(37) if bitmap & (1 << channel)]
        cfg["hop_increment"] = data[33] & 31
        cfg["sleep_clock_accuracy"] = SCA[data[33] >> 5]
        for key, low, high, status in (("window_size", 1, 8, "InvalidLLWindowSize"),
                                        ("window_offset", 0, 3200, "InvalidLLWindowOffset"),
                                        ("connection_interval", 6, 3200, "InvalidLLConnectionInterval"),
                                        ("peripheral_latency", 0, 499, "InvalidLLPeripheralLatency"),
                                        ("connection_timeout", 10, 3200, "InvalidLLConnectionTimeout"),
                                        ("hop_increment", 5, 16, "InvalidLLHopIncrement")):
            if not low <= cfg[key] <= high:
                return _result(status)
        if len(cfg["used_channels"]) < 2:
            return _result("InvalidLLChannelMap")
        error = _connection_error(cfg)
        if error:
            return _result(error)
    else:
        cfg["advertiser_address"] = address(data[:6])
        if code == 1:
            cfg["target_address"] = address(data[6:12])
        elif code == 4:
            if len(data) - 6 > 31:
                return _result("InvalidLLScanResponseDataLength")
            cfg["scan_response_data"] = data[6:].hex().upper()
        else:
            if len(data) - 6 > 31:
                return _result("InvalidLLAdvertisingDataLength")
            cfg["advertising_data"] = data[6:].hex().upper()
    return _result("Success", cfg)


def _handler(_args, request):
    operation = request.get("operation")
    if operation == "config":
        return {"result": {"configuration": configuration(request.get("configuration"))}}
    if operation == "encode":
        data = encode(request.get("configuration", {}))
        return {"result": {"pdu_hex": data.hex().upper(), "bits": len(data) * 8}}
    if operation == "decode":
        return {"result": decode(_hex_bytes(request.get("pdu"), "pdu"))}
    raise InputError("operation must be config, encode, or decode")


if __name__ == "__main__":
    run_cli("ble_ll_advertising", _handler, description=__doc__)
