"""Build and decode Bluetooth LE Attribute Protocol PDUs."""
from __future__ import annotations

from _bluetooth_common import InputError, run_cli
from ble_l2cap import _hex_bytes, _hex_number, _int

OPCODES = {
    "Error response": 0x01, "MTU request": 0x02, "MTU response": 0x03,
    "Information request": 0x04, "Information response": 0x05,
    "Find by type value request": 0x06, "Find by type value response": 0x07,
    "Read by type request": 0x08, "Read by type response": 0x09,
    "Read request": 0x0A, "Read response": 0x0B,
    "Read blob request": 0x0C, "Read blob response": 0x0D,
    "Read by group type request": 0x10, "Read by group type response": 0x11,
    "Write request": 0x12, "Write response": 0x13,
    "Prepare write request": 0x16, "Prepare write response": 0x17,
    "Execute write request": 0x18, "Execute write response": 0x19,
    "Handle value notification": 0x1B, "Handle value indication": 0x1D,
    "Handle value confirmation": 0x1E, "Write command": 0x52,
}
ERRORS = {
    "Invalid handle": 1, "Read not permitted": 2, "Write not permitted": 3,
    "Invalid PDU": 4, "Insufficient authentication": 5, "Request not supported": 6,
    "Invalid offset": 7, "Insufficient authorization": 8, "Prepare queue full": 9,
    "Attribute not found": 10, "Attribute not long": 11,
    "Insufficient encryption key size": 12, "Invalid attribute value length": 13,
    "Unlikely error": 14, "Insufficient encryption": 15,
    "Unsupported group type": 16, "Insufficient resources": 17,
}
EXECUTE = {"Cancel all prepared writes": 0, "Write all pending requests": 1}
FORMATS = {"16 bit": 1, "128 bit": 2}
DEFAULTS = {
    "opcode": "Read request", "requested_opcode": "Read request",
    "format": "16 bit", "attribute_handle": "0001",
    "error_message": "Invalid handle", "max_transmission_unit": 23,
    "start_handle": "0001", "end_handle": "FFFF",
    "attribute_type": "2800", "attribute_value": "", "offset": 0,
    "execute_write": "Cancel all prepared writes",
}
STATUS = {"Success": 0, "UnsupportedATTOpcode": -401, "IncompleteATTPDU": -402,
          "InvalidATTReqOpcodeInErrorResp": -403, "InvalidATTErrorCode": -404,
          "InvalidATTRxMTU": -405, "InvalidAttributeHandleRange": -406,
          "InvalidAttributeType": -407, "InvalidATTExecuteWriteFlag": -408,
          "MismatchAttributeDataLength": -409, "InvalidATTDataFormat": -410}
REQUESTS = {"MTU request", "Information request", "Find by type value request",
            "Read by type request", "Read request", "Read blob request",
            "Read by group type request", "Write request", "Prepare write request",
            "Execute write request"}
BASE_UUID = "0000000000001000800000805F9B34FB"


def _hex_field(value, field, length):
    raw = _hex_bytes(value, field, length=length)
    return raw.hex().upper()


def _value_bytes(value):
    return _hex_bytes(value, "attribute_value")


def _u16(value):
    return value.to_bytes(2, "little")


def _handle(value, field):
    return _int(_hex_number(value, field), field, 1, 65535)


def _range(cfg):
    first = _handle(cfg["start_handle"], "start_handle")
    last = _handle(cfg["end_handle"], "end_handle")
    if first > last:
        raise InputError("start_handle must not exceed end_handle")
    return _u16(first) + _u16(last)


def configuration(properties: dict | None = None) -> dict:
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("configuration must be a JSON object")
    unknown = set(properties) - set(DEFAULTS)
    if unknown:
        raise InputError("unsupported configuration fields: " + ", ".join(sorted(unknown)))
    cfg = {**DEFAULTS, **properties}
    if cfg["opcode"] not in OPCODES:
        raise InputError("unsupported ATT opcode")
    if cfg["requested_opcode"] not in REQUESTS:
        raise InputError("requested_opcode must name an ATT request")
    if cfg["error_message"] not in ERRORS:
        raise InputError("unsupported ATT error message")
    if cfg["execute_write"] not in EXECUTE or cfg["format"] not in FORMATS:
        raise InputError("unsupported execute_write or format")
    for field in ("attribute_handle", "start_handle", "end_handle"):
        _handle(cfg[field], field)
    if len(_hex_bytes(cfg["attribute_type"], "attribute_type")) not in (2, 16):
        raise InputError("attribute_type must contain 2 or 16 octets")
    if len(_value_bytes(cfg["attribute_value"])) > 65534:
        raise InputError("attribute_value exceeds 65534 octets")
    _int(cfg["max_transmission_unit"], "max_transmission_unit", 23, 65535)
    _int(cfg["offset"], "offset", 0, 65535)
    return cfg


def encode(properties: dict) -> bytes:
    cfg = configuration(properties)
    name = cfg["opcode"]
    value = _value_bytes(cfg["attribute_value"])
    handle = _u16(_handle(cfg["attribute_handle"], "attribute_handle"))
    body = b""
    if name == "Error response":
        body = bytes((OPCODES[cfg["requested_opcode"]],)) + handle + bytes((ERRORS[cfg["error_message"]],))
    elif name in {"MTU request", "MTU response"}:
        body = _u16(cfg["max_transmission_unit"])
    elif name in {"Information request", "Find by type value response"}:
        body = _range(cfg)
    elif name == "Find by type value request":
        attribute_type = _hex_bytes(cfg["attribute_type"], "attribute_type", length=2)
        body = _range(cfg) + attribute_type[::-1] + value
    elif name == "Read request":
        body = handle
    elif name in {"Read response", "Read blob response"}:
        body = value
    elif name == "Read blob request":
        body = handle + _u16(cfg["offset"])
    elif name in {"Read by type request", "Read by group type request"}:
        body = _range(cfg) + _hex_bytes(cfg["attribute_type"], "attribute_type")[::-1]
    elif name in {"Write request", "Write command", "Handle value notification", "Handle value indication"}:
        body = handle + value
    elif name in {"Prepare write request", "Prepare write response"}:
        body = handle + _u16(cfg["offset"]) + value
    elif name == "Execute write request":
        body = bytes((EXECUTE[cfg["execute_write"]],))
    elif name == "Read by type response":
        record = handle + value
        _int(len(record), "attribute data length", 2, 255)
        body = bytes((len(record),)) + record
    elif name == "Read by group type response":
        record = _range(cfg) + value
        _int(len(record), "attribute data length", 4, 255)
        body = bytes((len(record),)) + record
    elif name == "Information response":
        attribute_type = cfg["attribute_type"]
        if len(attribute_type) == 4 and cfg["format"] == "128 bit":
            attribute_type = BASE_UUID[:4] + attribute_type + BASE_UUID[8:]
        elif len(attribute_type) == 32 and cfg["format"] == "16 bit":
            attribute_type = attribute_type[4:8]
        body = bytes((FORMATS[cfg["format"]],)) + handle + bytes.fromhex(attribute_type)[::-1]
    return bytes((OPCODES[name],)) + body


def _result(status, cfg=None):
    return {"status": status, "status_code": STATUS[status], "configuration": cfg}


def decode(pdu: bytes) -> dict:
    if not pdu:
        return _result("IncompleteATTPDU")
    opcode = next((name for name, code in OPCODES.items() if code == pdu[0]), None)
    if opcode is None:
        return _result("UnsupportedATTOpcode")
    body = pdu[1:]
    cfg = {"opcode": opcode}
    value_ops = {"Read response", "Read blob response"}
    simple_ops = {"Write response", "Execute write response", "Handle value confirmation"}
    minimum = (4 if opcode == "Error response" else 2 if opcode in {"MTU request", "MTU response", "Read request"} else
               4 if opcode in {"Information request", "Find by type value response", "Read blob request"} else
               6 if opcode in {"Find by type value request", "Read by type request", "Read by group type request"} else
               2 if opcode in {"Write request", "Write command", "Handle value notification", "Handle value indication"} else
               4 if opcode in {"Prepare write request", "Prepare write response"} else
               1 if opcode in {"Execute write request", "Information response", "Read by type response", "Read by group type response"} else 0)
    if len(body) < minimum:
        return _result("IncompleteATTPDU")
    def hex16(index):
        return f"{int.from_bytes(body[index:index + 2], 'little'):04X}"
    if opcode == "Error response":
        cfg["requested_opcode"] = next((name for name in REQUESTS if OPCODES[name] == body[0]), None)
        if cfg["requested_opcode"] is None:
            return _result("InvalidATTReqOpcodeInErrorResp")
        cfg["attribute_handle"] = hex16(1)
        cfg["error_message"] = next((name for name, code in ERRORS.items() if code == body[3]), None)
        if cfg["error_message"] is None:
            return _result("InvalidATTErrorCode")
    elif opcode in {"MTU request", "MTU response"}:
        mtu = int.from_bytes(body[:2], "little")
        if mtu < 23:
            return _result("InvalidATTRxMTU")
        cfg["max_transmission_unit"] = mtu
    elif opcode in {"Information request", "Find by type value response"}:
        cfg.update(start_handle=hex16(0), end_handle=hex16(2))
        if int(cfg["start_handle"], 16) > int(cfg["end_handle"], 16):
            return _result("InvalidAttributeHandleRange")
    elif opcode == "Find by type value request":
        cfg.update(start_handle=hex16(0), end_handle=hex16(2),
                   attribute_type=body[4:6][::-1].hex().upper(), attribute_value=body[6:].hex().upper())
        if int(cfg["start_handle"], 16) > int(cfg["end_handle"], 16):
            return _result("InvalidAttributeHandleRange")
    elif opcode == "Read request":
        cfg["attribute_handle"] = hex16(0)
    elif opcode in value_ops:
        cfg["attribute_value"] = body.hex().upper()
    elif opcode == "Read blob request":
        cfg.update(attribute_handle=hex16(0), offset=int.from_bytes(body[2:4], "little"))
    elif opcode in {"Read by type request", "Read by group type request"}:
        if len(body) not in (6, 20):
            return _result("InvalidAttributeType")
        cfg.update(start_handle=hex16(0), end_handle=hex16(2), attribute_type=body[4:][::-1].hex().upper())
        if int(cfg["start_handle"], 16) > int(cfg["end_handle"], 16):
            return _result("InvalidAttributeHandleRange")
    elif opcode in {"Write request", "Write command", "Handle value notification", "Handle value indication"}:
        cfg.update(attribute_handle=hex16(0), attribute_value=body[2:].hex().upper())
    elif opcode in {"Prepare write request", "Prepare write response"}:
        cfg.update(attribute_handle=hex16(0), offset=int.from_bytes(body[2:4], "little"),
                   attribute_value=body[4:].hex().upper())
    elif opcode == "Execute write request":
        cfg["execute_write"] = next((name for name, code in EXECUTE.items() if code == body[0]), None)
        if cfg["execute_write"] is None:
            return _result("InvalidATTExecuteWriteFlag")
    elif opcode == "Read by type response":
        if body[0] != len(body) - 1 or body[0] < 2:
            return _result("MismatchAttributeDataLength")
        cfg.update(attribute_handle=hex16(1), attribute_value=body[3:].hex().upper())
    elif opcode == "Read by group type response":
        if body[0] != len(body) - 1 or body[0] < 4:
            return _result("MismatchAttributeDataLength")
        cfg.update(start_handle=hex16(1), end_handle=hex16(3), attribute_value=body[5:].hex().upper())
        if int(cfg["start_handle"], 16) > int(cfg["end_handle"], 16):
            return _result("InvalidAttributeHandleRange")
    elif opcode == "Information response":
        if body[0] not in (1, 2):
            return _result("InvalidATTDataFormat")
        size = 2 if body[0] == 1 else 16
        if len(body) != 1 + 2 + size:
            return _result("InvalidAttributeType")
        cfg.update(format="16 bit" if size == 2 else "128 bit", attribute_handle=hex16(1),
                   attribute_type=body[3:][::-1].hex().upper())
    elif opcode in simple_ops and body:
        return _result("IncompleteATTPDU")
    return _result("Success", cfg)


def _handler(_args, request):
    operation = request.get("operation")
    if operation == "config":
        return {"result": {"configuration": configuration(request.get("configuration"))}}
    if operation == "encode":
        if not isinstance(request.get("configuration"), dict):
            raise InputError("configuration must be a JSON object")
        pdu = encode(request["configuration"])
        return {"result": {"pdu_hex": pdu.hex().upper(), "octets": len(pdu)}}
    if operation == "decode":
        return {"result": decode(_hex_bytes(request.get("pdu"), "pdu"))}
    raise InputError("operation must be config, encode, or decode")


if __name__ == "__main__":
    run_cli("ble_att", _handler, description=__doc__)
