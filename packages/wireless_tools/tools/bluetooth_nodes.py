"""Create serializable Bluetooth Classic/LE node descriptors for agent workflows."""
from __future__ import annotations

import math
import secrets

from _bluetooth_common import InputError, run_cli
from ble_network_config import configuration as network_configuration
from bluetooth_classic_config import create as classic_configuration


CLASSIC_ROLES = {"central", "peripheral"}
LE_ROLES = {"central", "peripheral", "isochronous-broadcaster",
            "synchronized-receiver", "broadcaster-observer", "broadcaster", "observer"}
RADIO_DEFAULTS = {"transmitter_gain": 0.0, "receiver_gain": 0.0,
                  "receiver_sensitivity": -100.0, "noise_figure": 0.0,
                  "interference_modeling": "overlapping-adjacent-channel",
                  "max_interference_offset": 100_000_000.0}
LE_DEFAULTS = {"transmitter_power": 20.0, "advertising_interval": 0.020,
               "random_advertising": False, "scan_interval": 0.005}


def _number(value, key, low=-math.inf, high=math.inf):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise InputError(f"{key} must be a finite number in [{low}, {high}]")


def _multiple(value, key, period):
    if abs(value / period - round(value / period)) > 1e-7:
        raise InputError(f"{key} must be a multiple of {period}")


def _radio(kind: str, properties: dict | None) -> dict:
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("properties must be a JSON object")
    defaults = {**RADIO_DEFAULTS, **(LE_DEFAULTS if kind == "le" else {})}
    unknown = set(properties) - set(defaults)
    if unknown:
        raise InputError("unsupported node properties: " + ", ".join(sorted(unknown)))
    cfg = {**defaults, **properties}
    for key in ("transmitter_gain", "receiver_gain", "receiver_sensitivity"):
        _number(cfg[key], key)
    _number(cfg["noise_figure"], "noise_figure", 0)
    _number(cfg["max_interference_offset"], "max_interference_offset", 0)
    if cfg["interference_modeling"] not in {"overlapping-adjacent-channel",
                                            "non-overlapping-adjacent-channel"}:
        raise InputError("unsupported interference_modeling")
    if kind == "le":
        _number(cfg["transmitter_power"], "transmitter_power", -20, 20)
        for key, low, high in (("advertising_interval", 0.02, 10485.759375),
                               ("scan_interval", 0.0025, 40.96)):
            _number(cfg[key], key, low, high)
            _multiple(cfg[key], key, 0.000625)
        if not isinstance(cfg["random_advertising"], bool):
            raise InputError("random_advertising must be boolean")
    return cfg


def _address(node_id: int, lap=None, uap=None) -> str:
    if lap is None:
        lap = secrets.randbelow((1 << 24) - 1) + 1
    if not isinstance(lap, int) or isinstance(lap, bool) or not 1 <= lap <= 0xFFFFFF:
        raise InputError("lap must be an integer in 1..0xFFFFFF")
    if 10390272 <= lap <= 10390335:
        lap += 64
    if uap is None:
        uap = secrets.randbelow(255) + 1
    if not isinstance(uap, int) or isinstance(uap, bool) or not 1 <= uap <= 255:
        raise InputError("uap must be an integer in 1..255")
    return f"{lap:06X}{uap:02X}{node_id:04X}"


def create_nodes(kind: str, *, role="peripheral", positions=None, names=None,
                 properties=None, start_id=1, lap=None, uap=None,
                 connection_config=None, gap_config=None, mesh_config=None) -> list[dict]:
    if kind not in {"classic", "le"}:
        raise InputError("kind must be classic or le")
    if role not in (CLASSIC_ROLES if kind == "classic" else LE_ROLES):
        raise InputError("unsupported role for node kind")
    if positions is None:
        positions = [[0.0, 0.0, 0.0]]
    elif isinstance(positions, list) and len(positions) == 3 and all(isinstance(x, (int, float)) for x in positions):
        positions = [positions]
    if not isinstance(positions, list) or not positions:
        raise InputError("positions must be a nonempty list of [x,y,z] vectors")
    if kind == "le" and role == "broadcaster-observer" and len(positions) > 1:
        raise InputError("mesh broadcaster-observer nodes cannot be vectorized")
    if not isinstance(start_id, int) or isinstance(start_id, bool) or start_id < 1 or start_id + len(positions) - 1 > 65535:
        raise InputError("start_id and node count must fit in 1..65535")
    for row in positions:
        if not isinstance(row, list) or len(row) != 3:
            raise InputError("each position must contain [x,y,z]")
        for coordinate in row:
            _number(coordinate, "position coordinate")
    if names is None:
        names = []
    elif isinstance(names, str):
        names = [names]
    if not isinstance(names, list) or any(not isinstance(name, str) or not name for name in names):
        raise InputError("names must be a string or list of nonempty strings")
    if len(names) > len(positions):
        raise InputError("names cannot exceed positions count")
    radio = _radio(kind, properties)
    if kind == "classic":
        if gap_config is not None or mesh_config is not None:
            raise InputError("classic nodes do not accept GAP/mesh configuration")
        conn = classic_configuration("connection", connection_config or {}) if connection_config is not None else None
    else:
        if connection_config is not None:
            conn = network_configuration("bluetoothLEConnectionConfig", connection_config)
        else:
            conn = None
        gap = network_configuration("bluetoothLEGAPConfig", gap_config or {})
        mesh = network_configuration("bluetoothMeshProfileConfig", mesh_config or {})
    nodes = []
    for index, position in enumerate(positions):
        node_id = start_id + index
        item = {"kind": kind, "id": node_id, "name": names[index] if index < len(names) else f"Node{node_id}",
                "role": role, "position": position, "properties": radio,
                "node_address": _address(node_id, lap, uap) if kind == "classic" else None,
                "connection_config": conn}
        if kind == "le":
            item["gap_config"] = gap
            item["mesh_config"] = mesh
        nodes.append(item)
    return nodes


def _handler(_args, request):
    nodes = create_nodes(request.get("kind"), role=request.get("role", "peripheral"),
                         positions=request.get("positions"), names=request.get("names"),
                         properties=request.get("properties"),
                         start_id=request.get("start_id", 1),
                         lap=request.get("lap"), uap=request.get("uap"),
                         connection_config=request.get("connection_config"),
                         gap_config=request.get("gap_config"),
                         mesh_config=request.get("mesh_config"))
    return {"result": {"nodes": nodes, "count": len(nodes)},
            "warnings": ["These are construction descriptors. For persistent node methods, traffic, "
                         "event subscriptions and deterministic simulation, use bluetooth_session."]}


if __name__ == "__main__":
    run_cli("bluetooth_nodes", _handler, description=__doc__)
