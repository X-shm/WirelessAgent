"""Serializable Bluetooth LE/mesh/CS configuration constructors (public properties)."""
from __future__ import annotations

from copy import deepcopy
import math

from _bluetooth_common import InputError, run_cli
from ble_l2cap import _hex_bytes


CHANNELS = list(range(37))
PHY = {"LE1M", "LE2M", "LE500K", "LE125K"}
DEFAULTS = {
    "bleCSConfig": dict(device_role="Initiator", step_mode=1, sequence_type="Sounding Sequence",
                        sequence_length=96, tone_duration=40, mode="LE1M", samples_per_symbol=8,
                        pulse_length=1, modulation_index=0.5, output_data_type="double"),
    "bluetoothLEBIGConfig": dict(seed_access_address="78E52493", phy_mode="LE1M", num_bis=1,
                                 iso_interval=0.005, bis_spacing=0.002238, sub_interval=0.002238,
                                 max_pdu=251, burst_number=1, pretransmission_offset=0,
                                 repetition_count=1, num_subevents=1, bis_arrangement="sequential",
                                 big_offset=0.0, receive_bis_numbers=[1], used_channels=CHANNELS,
                                 instant_offset=6, base_crc_initialization="1234"),
    "bluetoothLECISConfig": dict(iso_interval=0.020, num_subevents=1, sub_interval=None,
                                 burst_number=1, max_pdu=251, flush_timeout=1,
                                 cis_arrangement="sequential", tifs=0.00015, tmss=0.00015),
    "bluetoothLEConnectionConfig": dict(connection_interval=0.020, access_address="5DA44270",
                                       used_channels=CHANNELS, algorithm=1, hop_increment=5,
                                       crc_initialization="012345", supervision_timeout=1.0,
                                       phy_mode="LE1M", instant_offset=6, connection_offset=0.0,
                                       active_period=0.020, max_pdu=251, tifs=0.00015, tmces=0.00015),
    "bluetoothLEGAPConfig": dict(gap_procedure="none", max_connections=7,
                                 advertising_event_type="connectable and scannable undirected",
                                 advertising_interval=0.030, random_advertising=False,
                                 scan_interval=0.050, scan_window=0.030),
    "bluetoothLEPeriodicAdvConfig": dict(periodic_adv_interval=0.010, periodic_adv_offset=0.0,
                                         phy_mode="LE1M", used_channels=CHANNELS,
                                         periodic_adv_type="PADVB", num_subevents=1,
                                         subevent_interval=0.0075, num_response_slots=1,
                                         response_slot_delay=0.00125, response_slot_spacing=0.00025),
    "bluetoothMeshFriendshipConfig": dict(receive_delay=0.010, receive_window=0.001,
                                          poll_timeout=1.0),
    "bluetoothMeshProfileConfig": dict(element_address="0001", relay=False, friend=False,
                                       low_power=False, network_transmissions=1,
                                       network_transmit_interval=0.010, ttl=127,
                                       relay_retransmissions=1, relay_retransmit_interval=0.010),
}


def _number(value, key: str, low: float, high: float, *, integer: bool = False, multiple: float | None = None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f"{key} must be a finite number")
    if not low <= value <= high or (integer and int(value) != value):
        raise InputError(f"{key} must be in [{low}, {high}]" + (" and integer" if integer else ""))
    if multiple is not None and abs(value / multiple - round(value / multiple)) > 1e-7:
        raise InputError(f"{key} must be a multiple of {multiple}")


def _channels(value):
    if not isinstance(value, list) or len(value) < 2:
        raise InputError("used_channels must be a list of at least two channel indices")
    for channel in value:
        _number(channel, "used_channels element", 0, 36, integer=True)
    if len(set(value)) < 2:
        raise InputError("used_channels requires at least two distinct channels")
    return sorted(set(value))


def _cis_max_pdu(value):
    """Normalize CIS MaxPDU to one value or its directional [C2P, P2C] pair."""
    values = value if isinstance(value, list) else [value]
    if len(values) not in {1, 2}:
        raise InputError("bluetoothLECISConfig max_pdu must be an integer or one/two integers")
    for item in values:
        _number(item, "max_pdu", 1, 251, integer=True)
    return values[0] if len(values) == 1 else list(values)


def configuration(kind: str, properties: dict | None = None) -> dict:
    if kind not in DEFAULTS:
        raise InputError("unsupported configuration kind")
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("properties must be a JSON object")
    cfg = deepcopy(DEFAULTS[kind])
    unknown = set(properties) - set(cfg)
    if unknown:
        raise InputError("unsupported properties: " + ", ".join(sorted(unknown)))
    cfg.update(properties)
    if "used_channels" in cfg:
        cfg["used_channels"] = _channels(cfg["used_channels"])
    for key, length in (("seed_access_address", 4), ("access_address", 4),
                        ("crc_initialization", 3), ("base_crc_initialization", 2),
                        ("element_address", 2)):
        if key in cfg:
            cfg[key] = _hex_bytes(cfg[key], key, length=length).hex().upper()
    if "element_address" in cfg and not 1 <= int(cfg["element_address"], 16) <= 0x7FFF:
        raise InputError("element_address must be a unicast address")
    if "phy_mode" in cfg and cfg["phy_mode"] not in PHY:
        raise InputError("unsupported phy_mode")
    if kind == "bleCSConfig":
        for key, allowed in (("device_role", {"Initiator", "Reflector"}),
                             ("step_mode", {0, 1, 2, 3}),
                             ("sequence_type", {"Random Sequence", "Sounding Sequence"}),
                             ("sequence_length", {32, 64, 96, 128}),
                             ("tone_duration", {10, 20, 40, 80}),
                             ("mode", {"LE1M", "LE2M", "LE2M 2BT"}),
                             ("pulse_length", {1, 2, 3, 4}),
                             ("output_data_type", {"single", "double"})):
            if cfg[key] not in allowed:
                raise InputError(f"unsupported {key}")
        _number(cfg["samples_per_symbol"], "samples_per_symbol", 2, 65536, integer=True)
        _number(cfg["modulation_index"], "modulation_index", 0.45, 0.55, multiple=0.005)
        if cfg["sequence_type"] == "Sounding Sequence" and cfg["sequence_length"] not in (32, 96) and cfg["step_mode"] in (1, 3):
            raise InputError("sounding sequence_length must be 32 or 96")
        if cfg["step_mode"] == 0 and cfg["tone_duration"] != 80:
            # MATLAB validates this combination at waveform generation time.
            pass
    elif kind == "bluetoothLEGAPConfig":
        if cfg["gap_procedure"] not in {"none", "connection establishment"}:
            raise InputError("unsupported gap_procedure")
        if cfg["advertising_event_type"] not in {"connectable and scannable undirected",
                                               "connectable directed low duty cycle",
                                               "connectable directed high duty cycle"}:
            raise InputError("unsupported advertising_event_type")
        _number(cfg["max_connections"], "max_connections", 1, 32, integer=True)
        for key, low, high in (("advertising_interval", 0.02, 10485.759375),
                               ("scan_interval", 0.0025, 40.96), ("scan_window", 0.0025, 40.96)):
            _number(cfg[key], key, low, high, multiple=0.000625)
        if cfg["scan_window"] > cfg["scan_interval"]:
            raise InputError("scan_window must not exceed scan_interval")
        if not isinstance(cfg["random_advertising"], bool):
            raise InputError("random_advertising must be boolean")
    elif kind == "bluetoothMeshFriendshipConfig":
        for key, low, high, step in (("receive_delay", 0.01, 0.255, 0.001),
                                    ("receive_window", 0.001, 0.255, 0.001),
                                    ("poll_timeout", 1, 345599.9, 0.1)):
            _number(cfg[key], key, low, high, multiple=step)
    elif kind == "bluetoothMeshProfileConfig":
        for key in ("relay", "friend", "low_power"):
            if not isinstance(cfg[key], bool):
                raise InputError(f"{key} must be boolean")
        if cfg["low_power"] and (cfg["relay"] or cfg["friend"]):
            raise InputError("low_power cannot coexist with relay or friend")
        for key in ("network_transmissions", "relay_retransmissions"):
            _number(cfg[key], key, 1, 8, integer=True)
        _number(cfg["ttl"], "ttl", 0, 127, integer=True)
        if cfg["ttl"] == 1:
            raise InputError("ttl 1 is invalid")
        for key in ("network_transmit_interval", "relay_retransmit_interval"):
            _number(cfg[key], key, 0.01, 0.32, multiple=0.01)
    else:
        if "iso_interval" in cfg:
            _number(cfg["iso_interval"], "iso_interval", 0.005, 4.0, multiple=0.00125)
        if "connection_interval" in cfg:
            _number(cfg["connection_interval"], "connection_interval", 0.0075, 4.0, multiple=0.00125)
        if "periodic_adv_interval" in cfg:
            _number(cfg["periodic_adv_interval"], "periodic_adv_interval", 0.0075, 81.91875, multiple=0.00125)
        if "max_pdu" in cfg:
            if kind == "bluetoothLECISConfig":
                cfg["max_pdu"] = _cis_max_pdu(cfg["max_pdu"])
            else:
                _number(cfg["max_pdu"], "max_pdu", 1, 251, integer=True)
        if "num_subevents" in cfg:
            _number(cfg["num_subevents"], "num_subevents", 1,
                    128 if kind == "bluetoothLEPeriodicAdvConfig" else 31, integer=True)
        if "algorithm" in cfg and cfg["algorithm"] not in (1, 2):
            raise InputError("algorithm must be 1 or 2")
        if "hop_increment" in cfg:
            _number(cfg["hop_increment"], "hop_increment", 5, 16, integer=True)
        if "instant_offset" in cfg:
            _number(cfg["instant_offset"], "instant_offset", 6, 65535, integer=True)
        if "bis_arrangement" in cfg and cfg["bis_arrangement"] not in {"sequential", "interleaved"}:
            raise InputError("unsupported bis_arrangement")
        if "cis_arrangement" in cfg and cfg["cis_arrangement"] not in {"sequential", "interleaved"}:
            raise InputError("unsupported cis_arrangement")
        if "periodic_adv_type" in cfg and cfg["periodic_adv_type"] not in {"PADVB", "PAwR"}:
            raise InputError("unsupported periodic_adv_type")
        for key, low, high in (("num_bis", 1, 31), ("burst_number", 1, 7),
                               ("pretransmission_offset", 0, 15), ("repetition_count", 1, 15),
                               ("flush_timeout", 1, 255), ("num_response_slots", 0, 255)):
            if key in cfg:
                _number(cfg[key], key, low, high, integer=True)
        if "receive_bis_numbers" in cfg:
            nums = cfg["receive_bis_numbers"]
            if not isinstance(nums, list) or not nums:
                raise InputError("receive_bis_numbers must be nonempty list")
            for num in nums:
                _number(num, "receive_bis_numbers element", 1, cfg["num_bis"], integer=True)
        for key, low, high in (("bis_spacing", 198e-6, 1.048575),
                               ("sub_interval", 198e-6, 1.048575),
                               ("big_offset", 0, 1e6), ("tifs", 0, 0.01),
                               ("tmss", 0, 0.01), ("tmces", 0, 0.01),
                               ("connection_offset", 0, 4.0), ("active_period", 0, 4.0),
                               ("supervision_timeout", 0.1, 32.0),
                               ("periodic_adv_offset", 0, 81.91875),
                               ("subevent_interval", 0.0075, 0.31875),
                               ("response_slot_delay", 0.00125, 0.3175),
                               ("response_slot_spacing", 0.00025, 0.031875)):
            if key in cfg and cfg[key] is not None:
                _number(cfg[key], key, low, high)
    return cfg


def _handler(_args, request):
    kind = request.get("kind")
    if request.get("operation") == "list":
        return {"result": {"kinds": list(DEFAULTS)}}
    return {"result": {"kind": kind, "configuration": configuration(kind, request.get("properties"))}}


if __name__ == "__main__":
    run_cli("ble_network_config", _handler, description=__doc__)
