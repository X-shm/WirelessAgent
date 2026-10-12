"""Build and decode Bluetooth LE L2CAP signaling and data frames."""
from __future__ import annotations

from _bluetooth_common import InputError, run_cli


COMMANDS = {
    "Command reject": 0x01,
    "Disconnection request": 0x06,
    "Disconnection response": 0x07,
    "Connection parameter update request": 0x12,
    "Connection parameter update response": 0x13,
    "Credit based connection request": 0x14,
    "Credit based connection response": 0x15,
    "Flow control credit": 0x16,
}
REASONS = {"Command not understood": 0, "Signaling MTU exceeded": 1, "Invalid CID in request": 2}
UPDATES = {"Accepted": 0, "Rejected": 1}
RESULTS = {
    "Successful": 0, "LEPSM not supported": 2, "No resources available": 4,
    "Insufficient authentication": 5, "Insufficient authorization": 6,
    "Insufficient encryption key size": 7, "Insufficient encryption": 8,
    "Invalid source CID": 9, "Source CID already allocated": 10,
    "Unacceptable parameters": 11,
}
DEFAULTS = {
    "channel_identifier": "0005", "command_type": "Credit based connection request",
    "signal_identifier": "01", "command_reject_reason": "Command not understood",
    "source_channel_identifier": "0040", "destination_channel_identifier": "0040",
    "connection_interval_range": [6, 3200], "connection_timeout": 10,
    "peripheral_latency": 0, "parameter_update_result": "Accepted",
    "le_psm": "001F", "max_transmission_unit": 23,
    "max_pdu_payload_size": 23, "credits": 1, "connection_result": "Successful",
}
STATUS = {"Success": 0, "MismatchL2CAPHeaderLength": -305,
          "IncompleteL2CAPDataFrame": -306, "InvalidL2CAPChannelIdentifier": -307,
          "InvalidL2CAPCommand": -308, "InvalidL2CAPCommandRejectReason": -309,
          "InvalidL2CAPParameterUpdateResult": -310, "InvalidL2CAPConnectionResult": -311,
          "IllegalL2CAPSignalIdentifier": -312, "InvalidL2CAPSDULength": -319,
          "MismatchL2CAPSignalFrameLength": -320, "IncompleteL2CAPSignalFrame": -321,
          "L2CAPSegmentationUnsupported": -304}


def _hex_bytes(value, field: str, *, length: int | None = None) -> bytes:
    if isinstance(value, str):
        compact = "".join(value.split())
        if len(compact) % 2:
            raise InputError(f"{field} must contain complete hex octets")
        try:
            data = bytes.fromhex(compact)
        except ValueError as exc:
            raise InputError(f"{field} must be hexadecimal") from exc
    elif isinstance(value, list):
        if any(not isinstance(item, int) or isinstance(item, bool) or not 0 <= item <= 255 for item in value):
            raise InputError(f"{field} must contain byte values in 0..255")
        data = bytes(value)
    else:
        raise InputError(f"{field} must be a hex string or byte array")
    if length is not None and len(data) != length:
        raise InputError(f"{field} must contain {length} octets")
    return data


def _hex_number(value, field: str, *, size: int = 2) -> int:
    data = _hex_bytes(value, field, length=size)
    return int.from_bytes(data, "big")


def _int(value, field: str, low: int, high: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise InputError(f"{field} must be an integer in {low}..{high}")
    return value


def _u16(value: int) -> bytes:
    return value.to_bytes(2, "little")


def _cid(value, field: str, *, allow_null: bool = False) -> int:
    number = _hex_number(value, field)
    if number == 0 and allow_null:
        return number
    if number not in (4, 5, 6) and not 32 <= number <= 127:
        raise InputError(f"{field} is not an LE L2CAP channel identifier")
    return number


def _named(mapping, value, field):
    if value not in mapping:
        raise InputError(f"{field} is unsupported")
    return mapping[value]


def configuration(properties: dict | None = None) -> dict:
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("configuration must be a JSON object")
    unknown = set(properties) - set(DEFAULTS)
    if unknown:
        raise InputError("unsupported configuration fields: " + ", ".join(sorted(unknown)))
    cfg = {**DEFAULTS, **properties}
    _cid(cfg["channel_identifier"], "channel_identifier")
    _named(COMMANDS, cfg["command_type"], "command_type")
    _named(REASONS, cfg["command_reject_reason"], "command_reject_reason")
    _named(UPDATES, cfg["parameter_update_result"], "parameter_update_result")
    _named(RESULTS, cfg["connection_result"], "connection_result")
    _int(_hex_number(cfg["signal_identifier"], "signal_identifier", size=1), "signal_identifier", 1, 255)
    allow_null = cfg["command_type"] == "Command reject" and cfg["command_reject_reason"] == "Invalid CID in request"
    _cid(cfg["source_channel_identifier"], "source_channel_identifier", allow_null=allow_null)
    _cid(cfg["destination_channel_identifier"], "destination_channel_identifier", allow_null=allow_null)
    _int(_hex_number(cfg["le_psm"], "le_psm"), "le_psm", 1, 65535)
    for field, low, high in (("connection_timeout", 10, 3200), ("peripheral_latency", 0, 499),
                             ("max_transmission_unit", 23, 65535), ("max_pdu_payload_size", 23, 65533),
                             ("credits", 0, 65535)):
        _int(cfg[field], field, low, high)
    interval = cfg["connection_interval_range"]
    if not isinstance(interval, list) or len(interval) != 2:
        raise InputError("connection_interval_range must contain [min,max]")
    _int(interval[0], "connection_interval_range minimum", 6, 3200)
    _int(interval[1], "connection_interval_range maximum", interval[0], 3200)
    return cfg


def encode(cfg: dict, sdu: bytes | None = None) -> bytes:
    cfg = configuration(cfg)
    channel = _cid(cfg["channel_identifier"], "channel_identifier")
    if channel == 5:
        if sdu is not None:
            raise InputError("signaling commands do not take an sdu")
        command = cfg["command_type"]
        if command == "Command reject":
            reason = _named(REASONS, cfg["command_reject_reason"], "command_reject_reason")
            data = _u16(reason)
            if reason == 1:
                data += _u16(cfg["max_transmission_unit"])
            elif reason == 2:
                data += _u16(_cid(cfg["destination_channel_identifier"], "destination_channel_identifier", allow_null=True))
                data += _u16(_cid(cfg["source_channel_identifier"], "source_channel_identifier", allow_null=True))
        elif command in {"Disconnection request", "Disconnection response"}:
            data = _u16(_cid(cfg["destination_channel_identifier"], "destination_channel_identifier"))
            data += _u16(_cid(cfg["source_channel_identifier"], "source_channel_identifier"))
        elif command == "Connection parameter update request":
            lo, hi = cfg["connection_interval_range"]
            if cfg["peripheral_latency"] > (cfg["connection_timeout"] * 10 / (hi * 1.25) * 2) - 1:
                raise InputError("peripheral_latency exceeds the connection timeout")
            data = b"".join(_u16(value) for value in (lo, hi, cfg["peripheral_latency"], cfg["connection_timeout"]))
        elif command == "Connection parameter update response":
            data = _u16(_named(UPDATES, cfg["parameter_update_result"], "parameter_update_result"))
        elif command == "Credit based connection request":
            data = b"".join(_u16(value) for value in (
                _hex_number(cfg["le_psm"], "le_psm"),
                _cid(cfg["source_channel_identifier"], "source_channel_identifier"),
                cfg["max_transmission_unit"], cfg["max_pdu_payload_size"], cfg["credits"]))
        elif command == "Credit based connection response":
            data = b"".join(_u16(value) for value in (
                _cid(cfg["destination_channel_identifier"], "destination_channel_identifier"),
                cfg["max_transmission_unit"], cfg["max_pdu_payload_size"], cfg["credits"],
                _named(RESULTS, cfg["connection_result"], "connection_result")))
        else:  # Flow control credit
            if cfg["credits"] == 0:
                raise InputError("flow control credits must be nonzero")
            data = _u16(_cid(cfg["source_channel_identifier"], "source_channel_identifier")) + _u16(cfg["credits"])
        payload = bytes((_named(COMMANDS, command, "command_type"),
                         _hex_number(cfg["signal_identifier"], "signal_identifier", size=1))) + _u16(len(data)) + data
    else:
        if sdu is None:
            raise InputError("data frames require sdu")
        if channel in (4, 6):
            if len(sdu) > 65535:
                raise InputError("B-frame SDU exceeds 65535 octets")
            payload = sdu
        else:
            if len(sdu) > 65533:
                raise InputError("LE-frame SDU exceeds 65533 octets")
            payload = _u16(len(sdu)) + sdu
    return _u16(len(payload)) + _u16(channel) + payload


def _read_u16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 2], "little")


def _decode_status(name: str, *, config=None, sdu=None):
    return {"status": name, "status_code": STATUS[name], "configuration": config, "sdu_hex": sdu}


def decode(frame: bytes) -> dict:
    if len(frame) < 4:
        return _decode_status("IncompleteL2CAPDataFrame")
    length, channel = _read_u16(frame, 0), _read_u16(frame, 2)
    if len(frame) - 4 != length:
        return _decode_status("MismatchL2CAPHeaderLength")
    if channel not in (4, 5, 6) and not 32 <= channel <= 127:
        return _decode_status("InvalidL2CAPChannelIdentifier")
    payload = frame[4:]
    cfg = {"channel_identifier": f"{channel:04X}"}
    if channel in (4, 6):
        return _decode_status("Success", config=cfg, sdu=payload.hex().upper())
    if channel != 5:
        if len(payload) < 2:
            return _decode_status("IncompleteL2CAPDataFrame")
        if _read_u16(payload, 0) != len(payload) - 2:
            return _decode_status("L2CAPSegmentationUnsupported")
        return _decode_status("Success", config=cfg, sdu=payload[2:].hex().upper())
    if len(payload) < 4:
        return _decode_status("IncompleteL2CAPSignalFrame")
    command = next((name for name, code in COMMANDS.items() if code == payload[0]), None)
    if command is None:
        return _decode_status("InvalidL2CAPCommand")
    if payload[1] == 0:
        return _decode_status("IllegalL2CAPSignalIdentifier")
    data_len = _read_u16(payload, 2)
    if len(payload) - 4 != data_len:
        return _decode_status("MismatchL2CAPSignalFrameLength")
    data = payload[4:]
    expected_len = {"Command reject": 2, "Disconnection request": 4,
                    "Disconnection response": 4, "Connection parameter update request": 8,
                    "Connection parameter update response": 2, "Credit based connection request": 10,
                    "Credit based connection response": 10, "Flow control credit": 4}[command]
    if len(data) < expected_len:
        return _decode_status("IncompleteL2CAPSignalFrame")
    cfg.update(command_type=command, signal_identifier=f"{payload[1]:02X}")
    if command == "Command reject":
        reason = _read_u16(data, 0)
        cfg["command_reject_reason"] = next((name for name, code in REASONS.items() if code == reason), None)
        if cfg["command_reject_reason"] is None:
            return _decode_status("InvalidL2CAPCommandRejectReason")
        expected_len = 2 if reason == 0 else 4 if reason == 1 else 6
        if len(data) != expected_len:
            return _decode_status("IncompleteL2CAPSignalFrame")
        if reason == 1:
            cfg["max_transmission_unit"] = _read_u16(data, 2)
        elif reason == 2:
            cfg["source_channel_identifier"] = f"{_read_u16(data, 2):04X}"
            cfg["destination_channel_identifier"] = f"{_read_u16(data, 4):04X}"
    elif command.startswith("Disconnection"):
        cfg["destination_channel_identifier"] = f"{_read_u16(data, 0):04X}"
        cfg["source_channel_identifier"] = f"{_read_u16(data, 2):04X}"
    elif command == "Connection parameter update request":
        cfg["connection_interval_range"] = [_read_u16(data, 0), _read_u16(data, 2)]
        cfg["peripheral_latency"] = _read_u16(data, 4)
        cfg["connection_timeout"] = _read_u16(data, 6)
    elif command == "Connection parameter update response":
        cfg["parameter_update_result"] = next((name for name, code in UPDATES.items() if code == _read_u16(data, 0)), None)
        if cfg["parameter_update_result"] is None:
            return _decode_status("InvalidL2CAPParameterUpdateResult")
    elif command == "Credit based connection request":
        cfg.update(le_psm=f"{_read_u16(data, 0):04X}",
                   source_channel_identifier=f"{_read_u16(data, 2):04X}",
                   max_transmission_unit=_read_u16(data, 4),
                   max_pdu_payload_size=_read_u16(data, 6), credits=_read_u16(data, 8))
    elif command == "Credit based connection response":
        cfg.update(destination_channel_identifier=f"{_read_u16(data, 0):04X}",
                   max_transmission_unit=_read_u16(data, 2),
                   max_pdu_payload_size=_read_u16(data, 4), credits=_read_u16(data, 6))
        cfg["connection_result"] = next((name for name, code in RESULTS.items() if code == _read_u16(data, 8)), None)
        if cfg["connection_result"] is None:
            return _decode_status("InvalidL2CAPConnectionResult")
    else:  # Flow control credit
        cfg["source_channel_identifier"] = f"{_read_u16(data, 0):04X}"
        cfg["credits"] = _read_u16(data, 2)
        if cfg["credits"] == 0:
            return _decode_status("IncompleteL2CAPSignalFrame")
    return _decode_status("Success", config=cfg)


def _handler(_args, request):
    operation = request.get("operation")
    if operation == "config":
        return {"result": {"configuration": configuration(request.get("configuration"))}}
    if operation == "encode":
        cfg = request.get("configuration")
        if not isinstance(cfg, dict):
            raise InputError("configuration must be a JSON object")
        sdu = _hex_bytes(request["sdu"], "sdu") if "sdu" in request else None
        frame = encode(cfg, sdu)
        return {"result": {"frame_hex": frame.hex().upper(), "octets": len(frame)}}
    if operation == "decode":
        return {"result": decode(_hex_bytes(request.get("frame"), "frame"))}
    raise InputError("operation must be config, encode, or decode")


if __name__ == "__main__":
    run_cli("ble_l2cap", _handler, description=__doc__)
