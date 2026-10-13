"""BLE Link Layer data/control-channel PDU configuration, encoding and decoding."""
from __future__ import annotations

import numpy as np

from _bluetooth_algorithms import crc24_ble
from _bluetooth_common import InputError, run_cli
from ble_l2cap import _hex_bytes, _int
from ble_ll_advertising import _bits, _pack, _connection_error


OPCODES = {"Connection update indication": 0, "Channel map indication": 1,
           "Terminate indication": 2, "Unknown response": 7,
           "Version indication": 12, "Reject indication": 13}
ERROR_CODES = dict(zip(
    ["Success", "Unknown connection identifier", "Hardware failure", "Memory capacity exceeded",
     "Connection timeout", "Connection limit exceeded", "Connection already exists",
     "Command disallowed", "Connection rejected due to limited resources",
     "Connection rejected due to unacceptable BD_ADDR", "Connection accept timeout exceeded",
     "Unspecified error", "Invalid LL parameters", "Unsupported LL parameter value",
     "Role change not allowed", "LL response timeout", "LL procedure collision", "Instant passed",
     "Channel classification not supported", "Extended inquiry response too large", "Advertising timeout",
     "Connection rejected due to no suitable channel found", "Controller busy",
     "Unacceptable connection parameters", "Connection failed to be established",
     "Unknown advertising identifier", "Limit reached", "Operation cancelled by host"],
    [0, 2, 3, 7, 8, 9, 11, 12, 13, 15, 16, 30, 31, 32, 33, 34, 35, 40, 46, 54, 57, 58, 59, 60, 62, 66, 67, 68]))
VERSIONS = {"4.0": 6, "4.1": 7, "4.2": 8, "5.0": 9}
CONTROL_DEFAULTS = {"opcode": "Connection update indication", "window_size": 1,
                    "window_offset": 0, "connection_interval": 6, "peripheral_latency": 0,
                    "connection_timeout": 10, "instant": 0, "used_channels": list(range(37)),
                    "error_code": "Success", "unknown_opcode": "00", "version_number": "5.0",
                    "company_identifier": "FFFF", "sub_version_number": "0000"}
DATA_DEFAULTS = {"llid": "Data (continuation fragment/empty)", "nesn": 0,
                 "sequence_number": 0, "more_data": False, "crc_initialization": "012345",
                 "control_config": CONTROL_DEFAULTS}
LLIDS = {"Data (continuation fragment/empty)": 1,
         "Data (start fragment/complete)": 2, "Control": 3}
STATUS = {"Success": 0, "CRCFailed": -1, "LLPDULengthMismatch": -2,
          "InvalidLLPeripheralLatency": -3, "InvalidLLConnectionTimeout": -4,
          "InvalidLLWindowSize": -5, "InvalidLLWindowOffset": -6,
          "InvalidLLConnectionInterval": -7, "InvalidLLChannelMap": -8,
          "IncompleteLLDataChannelPDU": -101, "InvalidLLID": -102,
          "UnsupportedLLOpCode": -103, "InvalidLLErrorCode": -104,
          "InvalidBluetoothVersion": -105, "ExpectedNonZeroPayload": -106,
          "MICNotSupported": -107}


def control_configuration(properties: dict | None = None) -> dict:
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("control_config must be a JSON object")
    unknown = set(properties) - set(CONTROL_DEFAULTS)
    if unknown:
        raise InputError("unsupported control fields: " + ", ".join(sorted(unknown)))
    cfg = {**CONTROL_DEFAULTS, **properties}
    if cfg["opcode"] not in OPCODES:
        raise InputError("unsupported control opcode")
    if cfg["error_code"] not in ERROR_CODES:
        raise InputError("unsupported error_code")
    if cfg["version_number"] not in VERSIONS:
        raise InputError("unsupported version_number")
    for name, length in (("unknown_opcode", 1), ("company_identifier", 2), ("sub_version_number", 2)):
        cfg[name] = _hex_bytes(cfg[name], name, length=length).hex().upper()
    for name, low, high in (("window_size", 1, 8), ("window_offset", 0, 3200),
                            ("connection_interval", 6, 3200), ("peripheral_latency", 0, 499),
                            ("connection_timeout", 10, 3200), ("instant", 0, 65535)):
        _int(cfg[name], name, low, high)
    channels = cfg["used_channels"]
    if not isinstance(channels, list):
        raise InputError("used_channels must be a list")
    for channel in channels:
        _int(channel, "used_channels element", 0, 36)
    cfg["used_channels"] = sorted(set(channels))
    if len(cfg["used_channels"]) < 2:
        raise InputError("used_channels requires at least two distinct channels")
    return cfg


def configuration(properties: dict | None = None) -> dict:
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("configuration must be a JSON object")
    unknown = set(properties) - set(DATA_DEFAULTS)
    if unknown:
        raise InputError("unsupported configuration fields: " + ", ".join(sorted(unknown)))
    cfg = {**DATA_DEFAULTS, **properties}
    if cfg["llid"] not in LLIDS:
        raise InputError("unsupported llid")
    for name in ("nesn", "sequence_number"):
        _int(cfg[name], name, 0, 1)
    if not isinstance(cfg["more_data"], bool):
        raise InputError("more_data must be boolean")
    cfg["crc_initialization"] = _hex_bytes(cfg["crc_initialization"], "crc_initialization", length=3).hex().upper()
    cfg["control_config"] = control_configuration(cfg["control_config"])
    return cfg


def _u16(value: int) -> bytes:
    return value.to_bytes(2, "little")


def _control_payload(cfg: dict) -> bytes:
    opcode = cfg["opcode"]
    if opcode == "Connection update indication":
        error = _connection_error(cfg)
        if error:
            raise InputError(error)
        body = (bytes((cfg["window_size"],)) + _u16(cfg["window_offset"])
                + _u16(cfg["connection_interval"]) + _u16(cfg["peripheral_latency"])
                + _u16(cfg["connection_timeout"]) + _u16(cfg["instant"]))
    elif opcode == "Channel map indication":
        bitmap = sum(1 << channel for channel in cfg["used_channels"])
        body = bitmap.to_bytes(5, "little") + _u16(cfg["instant"])
    elif opcode in ("Terminate indication", "Reject indication"):
        body = bytes((ERROR_CODES[cfg["error_code"]],))
    elif opcode == "Unknown response":
        body = bytes.fromhex(cfg["unknown_opcode"])
    else:
        body = (bytes((VERSIONS[cfg["version_number"]],))
                + bytes.fromhex(cfg["company_identifier"])[::-1]
                + bytes.fromhex(cfg["sub_version_number"])[::-1])
    return bytes((OPCODES[opcode],)) + body


def encode(properties: dict, payload: bytes | None = None) -> bytes:
    cfg = configuration(properties)
    if cfg["llid"] == "Control":
        if payload:
            raise InputError("payload is not accepted for a Control PDU")
        data = _control_payload(cfg["control_config"])
    else:
        data = payload if payload is not None else b""
        if len(data) > 251:
            raise InputError("payload must contain at most 251 octets")
        if not data and cfg["llid"] == "Data (start fragment/complete)":
            raise InputError("ExpectedNonZeroPayload")
    header = bytes((LLIDS[cfg["llid"]] | (cfg["nesn"] << 2)
                    | (cfg["sequence_number"] << 3) | (int(cfg["more_data"]) << 4), len(data)))
    content = header + data
    crc_init = int(cfg["crc_initialization"], 16)
    return content + _pack(crc24_ble(_bits(content), crc_init))


def _result(name: str, cfg: dict | None = None, payload: bytes | None = None) -> dict:
    value = {"status": name, "status_code": STATUS[name], "configuration": cfg}
    if payload is not None:
        value["payload_hex"] = payload.hex().upper()
    return value


def _decode_control(data: bytes) -> tuple[str, dict | None]:
    if not data:
        return "IncompleteLLDataChannelPDU", None
    opcode = next((name for name, value in OPCODES.items() if value == data[0]), None)
    if opcode is None:
        return "UnsupportedLLOpCode", None
    expected = {0: 12, 1: 8, 2: 2, 7: 2, 12: 6, 13: 2}[data[0]]
    if len(data) != expected:
        return "IncompleteLLDataChannelPDU", None
    cfg = control_configuration({"opcode": opcode})
    if opcode == "Connection update indication":
        cfg.update(window_size=data[1], window_offset=int.from_bytes(data[2:4], "little"),
                   connection_interval=int.from_bytes(data[4:6], "little"),
                   peripheral_latency=int.from_bytes(data[6:8], "little"),
                   connection_timeout=int.from_bytes(data[8:10], "little"),
                   instant=int.from_bytes(data[10:12], "little"))
        for key, low, high, status in (("window_size", 1, 8, "InvalidLLWindowSize"),
                                        ("window_offset", 0, 3200, "InvalidLLWindowOffset"),
                                        ("connection_interval", 6, 3200, "InvalidLLConnectionInterval"),
                                        ("peripheral_latency", 0, 499, "InvalidLLPeripheralLatency"),
                                        ("connection_timeout", 10, 3200, "InvalidLLConnectionTimeout")):
            if not low <= cfg[key] <= high:
                return status, None
        error = _connection_error(cfg)
        if error:
            return error, None
    elif opcode == "Channel map indication":
        bitmap = int.from_bytes(data[1:6], "little")
        cfg["used_channels"] = [i for i in range(37) if bitmap & (1 << i)]
        cfg["instant"] = int.from_bytes(data[6:8], "little")
        if len(cfg["used_channels"]) < 2:
            return "InvalidLLChannelMap", None
    elif opcode in ("Terminate indication", "Reject indication"):
        code = next((name for name, value in ERROR_CODES.items() if value == data[1]), None)
        if code is None:
            return "InvalidLLErrorCode", None
        cfg["error_code"] = code
    elif opcode == "Unknown response":
        cfg["unknown_opcode"] = f"{data[1]:02X}"
    else:
        version = next((name for name, value in VERSIONS.items() if value == data[1]), None)
        if version is None:
            return "InvalidBluetoothVersion", None
        cfg["version_number"] = version
        cfg["company_identifier"] = data[2:4][::-1].hex().upper()
        cfg["sub_version_number"] = data[4:6][::-1].hex().upper()
    return "Success", cfg


def decode(pdu: bytes, crc_initialization: str = "012345") -> dict:
    crc_init = int.from_bytes(_hex_bytes(crc_initialization, "crc_initialization", length=3), "big")
    if len(pdu) < 5:
        return _result("IncompleteLLDataChannelPDU")
    if not np.array_equal(_bits(pdu[-3:]), crc24_ble(_bits(pdu[:-3]), crc_init)):
        return _result("CRCFailed")
    kind = next((name for name, code in LLIDS.items() if code == (pdu[0] & 3)), None)
    if kind is None:
        return _result("InvalidLLID")
    if pdu[1] != len(pdu) - 5:
        return _result("LLPDULengthMismatch")
    if pdu[1] > 251:
        return _result("MICNotSupported")
    cfg = configuration({"llid": kind, "nesn": (pdu[0] >> 2) & 1,
                         "sequence_number": (pdu[0] >> 3) & 1,
                         "more_data": bool(pdu[0] & 16),
                         "crc_initialization": crc_initialization})
    data = pdu[2:-3]
    if kind == "Control":
        status, control = _decode_control(data)
        if status != "Success":
            return _result(status)
        cfg["control_config"] = control
        return _result("Success", cfg, b"")
    if not data and kind == "Data (start fragment/complete)":
        return _result("ExpectedNonZeroPayload")
    return _result("Success", cfg, data)


def _handler(_args, request):
    operation = request.get("operation")
    if operation == "control_config":
        return {"result": {"configuration": control_configuration(request.get("configuration"))}}
    if operation == "config":
        return {"result": {"configuration": configuration(request.get("configuration"))}}
    if operation == "encode":
        payload = _hex_bytes(request["payload"], "payload") if "payload" in request else None
        data = encode(request.get("configuration", {}), payload)
        return {"result": {"pdu_hex": data.hex().upper(), "bits": len(data) * 8}}
    if operation == "decode":
        return {"result": decode(_hex_bytes(request.get("pdu"), "pdu"),
                                 request.get("crc_initialization", "012345"))}
    raise InputError("operation must be control_config, config, encode, or decode")


if __name__ == "__main__":
    run_cli("ble_ll_data", _handler, description=__doc__)
