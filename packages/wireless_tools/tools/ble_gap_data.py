"""Build and decode Bluetooth LE GAP advertising data blocks."""
from __future__ import annotations

from _bluetooth_common import InputError, run_cli
from ble_l2cap import _hex_bytes, _int

DEFAULTS = {
    "advertising_data_types": ["Flags"], "le_discoverability": "General",
    "bredr": False, "le": "None", "local_name_shortening": False,
    "local_name": "Bluetooth", "identifier_type": "Complete", "identifiers": [],
    "advertising_interval": 32, "tx_power_level": 0,
    "connection_interval_range": [6, 3200],
}
TYPE_CODES = {"Flags": 0x01, "UUIDs": 0x03, "Local name": 0x09,
              "Tx power level": 0x0A, "Connection interval range": 0x12,
              "Advertising interval": 0x1A}
DECODE_TYPES = {1: "Flags", 2: "UUIDs", 3: "UUIDs", 8: "Local name",
                9: "Local name", 10: "Tx power level", 18: "Connection interval range",
                26: "Advertising interval"}
STATUS = {"Success": 0, "InvalidGAPADLength": -201,
          "MismatchGAPADLength": -202, "UnsupportedGAPADType": -203,
          "InvalidGAPAdvertisingInterval": -204,
          "InvalidGAPConnectionIntervalRange": -205,
          "InvalidGAPConnectionIntervalMinimum": -206,
          "InvalidGAPConnectionIntervalMaximum": -207}


def configuration(properties: dict | None = None) -> dict:
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("configuration must be a JSON object")
    unknown = set(properties) - set(DEFAULTS)
    if unknown:
        raise InputError("unsupported configuration fields: " + ", ".join(sorted(unknown)))
    cfg = {**DEFAULTS, **properties}
    names = cfg["advertising_data_types"]
    if isinstance(names, str):
        names = [names]
    if not isinstance(names, list) or any(name not in TYPE_CODES for name in names):
        raise InputError("advertising_data_types must list supported AD types")
    cfg["advertising_data_types"] = list(dict.fromkeys(names))
    if cfg["le_discoverability"] not in {"None", "General", "Limited", "Limited and general"}:
        raise InputError("unsupported le_discoverability")
    if cfg["le"] not in {"None", "Host", "Controller", "Host and controller"}:
        raise InputError("unsupported le capability")
    if cfg["identifier_type"] not in {"Complete", "Incomplete"}:
        raise InputError("identifier_type must be Complete or Incomplete")
    for name in ("bredr", "local_name_shortening"):
        if not isinstance(cfg[name], bool):
            raise InputError(f"{name} must be boolean")
    if not isinstance(cfg["local_name"], str):
        raise InputError("local_name must be a string")
    try:
        encoded_name = cfg["local_name"].encode("latin-1")
    except UnicodeEncodeError as exc:
        raise InputError("local_name contains a character outside MATLAB uint8 char range") from exc
    if len(encoded_name) > 254:
        raise InputError("local_name is too long")
    identifiers = cfg["identifiers"]
    if isinstance(identifiers, str):
        identifiers = [identifiers] if identifiers else []
    if not isinstance(identifiers, list) or len(identifiers) > 127:
        raise InputError("identifiers must be a list of at most 127 UUID16 values")
    for uuid in identifiers:
        _hex_bytes(uuid, "identifier", length=2)
    cfg["identifiers"] = [uuid.upper() for uuid in identifiers]
    _int(cfg["advertising_interval"], "advertising_interval", 32, 65535)
    _int(cfg["tx_power_level"], "tx_power_level", -127, 127)
    interval = cfg["connection_interval_range"]
    if not isinstance(interval, list) or len(interval) != 2:
        raise InputError("connection_interval_range must contain [min,max]")
    _int(interval[0], "connection_interval_range minimum", 6, 3200)
    _int(interval[1], "connection_interval_range maximum", interval[0], 3200)
    return cfg


def encode(properties: dict) -> bytes:
    cfg = configuration(properties)
    out = bytearray()
    for name in cfg["advertising_data_types"]:
        code = TYPE_CODES[name]
        if name == "Flags":
            discovery = {"None": 0, "Limited": 1, "General": 2, "Limited and general": 3}[cfg["le_discoverability"]]
            flags = discovery | (0 if cfg["bredr"] else 4)
            if cfg["bredr"]:
                flags |= {"None": 0, "Controller": 8, "Host": 16, "Host and controller": 24}[cfg["le"]]
            data = bytes((flags,))
        elif name == "UUIDs":
            code = 3 if cfg["identifier_type"] == "Complete" else 2
            data = b"".join(_hex_bytes(uuid, "identifier", length=2)[::-1] for uuid in cfg["identifiers"])
        elif name == "Local name":
            code = 8 if cfg["local_name_shortening"] else 9
            data = cfg["local_name"].encode("latin-1")
        elif name == "Tx power level":
            data = bytes((cfg["tx_power_level"] & 255,))
        elif name == "Connection interval range":
            data = b"".join(value.to_bytes(2, "little") for value in cfg["connection_interval_range"])
        else:
            data = cfg["advertising_interval"].to_bytes(2, "little")
        if not data:
            continue
        if len(data) + 1 > 255:
            raise InputError(f"{name} exceeds the one-octet AD length field")
        out.extend((len(data) + 1, code))
        out.extend(data)
    return bytes(out)


def _result(status, cfg=None):
    return {"status": status, "status_code": STATUS[status], "configuration": cfg}


def decode(block: bytes) -> dict:
    position = 0
    cfg = {"advertising_data_types": []}
    while position < len(block):
        length = block[position]
        position += 1
        if len(block) - position < length:
            return _result("MismatchGAPADLength")
        if length == 0:
            continue
        code = block[position]
        data = block[position + 1:position + length]
        position += length
        name = DECODE_TYPES.get(code)
        if name is None:
            return _result("UnsupportedGAPADType")
        expected = 1 if name in {"Flags", "Tx power level"} else 2 if name == "Advertising interval" else 4 if name == "Connection interval range" else None
        if expected is not None and len(data) != expected:
            return _result("InvalidGAPADLength")
        if name == "UUIDs" and len(data) % 2:
            return _result("InvalidGAPADLength")
        if name not in cfg["advertising_data_types"]:
            cfg["advertising_data_types"].append(name)
        if not data:
            continue
        if name == "Flags":
            flag = data[0]
            cfg["le_discoverability"] = {0: "None", 1: "Limited", 2: "General", 3: "Limited and general"}[flag & 3]
            cfg["bredr"] = not bool(flag & 4)
            cfg["le"] = ({0: "None", 8: "Controller", 16: "Host", 24: "Host and controller"}[flag & 24]
                         if cfg["bredr"] else "None")
        elif name == "UUIDs":
            cfg["identifier_type"] = "Complete" if code == 3 else "Incomplete"
            cfg["identifiers"] = [data[index:index + 2][::-1].hex().upper() for index in range(0, len(data), 2)]
        elif name == "Local name":
            cfg["local_name_shortening"] = code == 8
            cfg["local_name"] = data.decode("latin-1")
        elif name == "Tx power level":
            cfg["tx_power_level"] = int.from_bytes(data, "little", signed=True)
        elif name == "Connection interval range":
            low, high = int.from_bytes(data[:2], "little"), int.from_bytes(data[2:], "little")
            if not 6 <= low <= 3200:
                return _result("InvalidGAPConnectionIntervalMinimum")
            if not 6 <= high <= 3200:
                return _result("InvalidGAPConnectionIntervalMaximum")
            if low > high:
                return _result("InvalidGAPConnectionIntervalRange")
            cfg["connection_interval_range"] = [low, high]
        else:
            interval = int.from_bytes(data, "little")
            if interval < 32:
                return _result("InvalidGAPAdvertisingInterval")
            cfg["advertising_interval"] = interval
    return _result("Success", cfg)


def _handler(_args, request):
    operation = request.get("operation")
    if operation == "config":
        return {"result": {"configuration": configuration(request.get("configuration"))}}
    if operation == "encode":
        if not isinstance(request.get("configuration"), dict):
            raise InputError("configuration must be a JSON object")
        data = encode(request["configuration"])
        return {"result": {"data_block_hex": data.hex().upper(), "octets": len(data)}}
    if operation == "decode":
        return {"result": decode(_hex_bytes(request.get("data_block"), "data_block"))}
    raise InputError("operation must be config, encode, or decode")


if __name__ == "__main__":
    run_cli("ble_gap_data", _handler, description=__doc__)
