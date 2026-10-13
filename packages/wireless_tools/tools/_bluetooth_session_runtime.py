"""Serializable runtime objects for the Bluetooth agent session protocol.

The public Bluetooth Toolbox APIs combine value-style configuration objects
with mutable node handles.  This module deliberately represents both as JSON
objects so that a CLI process can resume a simulation without retaining a
Python process or accepting arbitrary callback code.
"""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any, Callable

import numpy as np

from _bluetooth_common import InputError, bit_vector
from ble_angle_estimate import angle_configuration
from ble_att import configuration as att_configuration
from ble_channel_selection import _initial_dynamic, _settings, select
from ble_gap_data import configuration as gap_data_configuration
from ble_l2cap import configuration as l2cap_configuration
from ble_ll_advertising import configuration as advertising_configuration
from ble_ll_data import configuration as data_configuration, control_configuration
from ble_network_config import DEFAULTS as LE_CONFIG_DEFAULTS, configuration as le_configuration
from bluetooth_classic_config import DEFAULTS as CLASSIC_CONFIG_DEFAULTS, create as classic_configuration
from bluetooth_packet_duration import packet_duration
from bluetooth_nodes import create_nodes
from bluetooth_path_loss import path_loss
from bluetooth_range import estimate as range_estimate


CONFIG_KINDS = {
    "bluetoothConnectionConfig": ("classic", "connection"),
    "bluetoothPhyConfig": ("classic", "phy"),
    "bluetoothWaveformConfig": ("classic", "waveform"),
    "bluetoothRFPHYTestConfig": ("classic", "rf_phy_test"),
    "bluetoothTestWaveformConfig": ("classic", "test_waveform"),
    **{name: ("le", name) for name in LE_CONFIG_DEFAULTS},
    "bleAngleEstimateConfig": ("adapter", "angle"),
    "bleL2CAPFrameConfig": ("adapter", "l2cap"),
    "bleATTPDUConfig": ("adapter", "att"),
    "bleGAPDataBlockConfig": ("adapter", "gap_data"),
    "bleLLAdvertisingChannelPDUConfig": ("adapter", "advertising"),
    "bleLLControlPDUConfig": ("adapter", "ll_control"),
    "bleLLDataChannelPDUConfig": ("adapter", "ll_data"),
    "bluetoothPathLossConfig": ("adapter", "path_loss"),
    "bluetoothRangeConfig": ("adapter", "range"),
}
NODE_KINDS = {"bluetoothNode": "classic", "bluetoothLENode": "le"}
SYSTEM_KINDS = {"bleChannelSelection"}
PUBLIC_OBJECT_KINDS = set(CONFIG_KINDS) | set(NODE_KINDS) | SYSTEM_KINDS

PATH_LOSS_DEFAULTS = {
    "environment": "Outdoor", "transmitter_antenna_gain": 0, "receiver_antenna_gain": 0,
    "transmitter_cable_loss": 0, "receiver_cable_loss": 0, "transmitter_antenna_height": 1,
    "receiver_antenna_height": 1, "path_loss_exponent": 2.2, "standard_deviation": 2.667,
    "random_stream": "Global stream", "seed": 73,
}
RANGE_DEFAULTS = {
    "environment": "Outdoor", "signal_power_type": "ReceiverSensitivity",
    "received_signal_power": -79, "mode": "LE1M", "receiver_sensitivity": -94,
    "link_margin": 15, "transmitter_power": 0, "transmitter_antenna_gain": 0,
    "receiver_antenna_gain": 0, "transmitter_cable_loss": 1.25, "receiver_cable_loss": 1.25,
    "transmitter_antenna_height": 1, "receiver_antenna_height": 1,
    "path_loss_exponent": 2.2, "standard_deviation": 2.667,
}


def _rf_phy_test_id(config: dict[str, Any]) -> str | None:
    """Return the Bluetooth RF-PHY conformance case applicable to *config*.

    MATLAB deliberately exposes empty dependent properties for a valid
    configuration that has no assigned RF-PHY conformance case (for example,
    an uncoded-only test selected with LE500K).  Returning ``None`` preserves
    that distinction; it is not a configuration error.
    """
    test, mode, packet = config["test"], config["mode"], config["packet_type"]
    standard = config["modulation_index"] != 0.5
    if test == "Output power":
        if mode == "LE1M":
            return "RF-PHY/TRM/BV-15-C" if packet == "ConnectionCTE" else "RF-PHY/TRM/BV-01-C"
        if mode == "LE2M":
            return "RF-PHY/TRM/BV-22-C" if packet == "ConnectionCTE" else "RF-PHY/TRM/BV-19-C"
        return None
    if test == "Inband emissions":
        return {"LE1M": "RF-PHY/TRM/BV-03-C", "LE2M": "RF-PHY/TRM/BV-08-C"}.get(mode)
    if test == "Modulation characteristics":
        return {"LE1M": "RF-PHY/TRM/BV-05-C" if standard else "RF-PHY/TRM/BV-09-C",
                "LE2M": "RF-PHY/TRM/BV-10-C" if standard else "RF-PHY/TRM/BV-11-C",
                "LE125K": "RF-PHY/TRM/BV-13-C"}.get(mode)
    if test == "Carrier frequency offset and drift":
        if mode == "LE1M": return "RF-PHY/TRM/BV-16-C" if packet == "ConnectionCTE" else "RF-PHY/TRM/BV-06-C"
        if mode == "LE2M": return "RF-PHY/TRM/BV-17-C" if packet == "ConnectionCTE" else "RF-PHY/TRM/BV-12-C"
        return "RF-PHY/TRM/BV-14-C" if mode == "LE125K" else None
    slot = 2 * int(config["cte_type"][0]) + int(config["cte_type"][1])
    if test == "Tx power stability":
        if packet != "ConnectionCTE" or slot == 0:
            return None
        return {"LE1M": {1: "RF-PHY/TRM/PS/BV-01-C", 2: "RF-PHY/TRM/PS/BV-02-C"},
                "LE2M": {1: "RF-PHY/TRM/PS/BV-03-C", 2: "RF-PHY/TRM/PS/BV-04-C"}}.get(mode, {}).get(slot)
    receiver = {
        "C/I": {"LE1M": ("03", "15"), "LE2M": ("09", "21"), "LE500K": ("28", "34"), "LE125K": ("29", "35")},
        "Receiver sensitivity": {"LE1M": ("01", "14"), "LE2M": ("08", "20"), "LE500K": ("26", "32"), "LE125K": ("27", "33")},
        "PER report integrity": {"LE1M": ("07", "19"), "LE2M": ("13", "25"), "LE500K": ("30", "36"), "LE125K": ("31", "37")},
        "Blocking": {"LE1M": ("04", "16"), "LE2M": ("10", "22")},
        "Intermodulation": {"LE1M": ("05", "17"), "LE2M": ("11", "23")},
        "Maximum input signal level": {"LE1M": ("06", "18"), "LE2M": ("12", "24")},
    }
    if test in receiver:
        cases = receiver[test].get(mode)
        return f"RF-PHY/RCV/BV-{cases[0 if standard else 1]}-C" if cases else None
    if test == "IQ samples coherency":
        codes = {"LE1M": {0: "05", 1: "01", 2: "02"}, "LE2M": {0: "06", 1: "03", 2: "04"}}
        return f"RF-PHY/RCV/IQC/BV-{codes[mode][slot]}-C" if mode in codes else None
    if test == "IQ samples dynamic range":
        codes = {"LE1M": {0: "11", 1: "07", 2: "08"}, "LE2M": {0: "12", 1: "09", 2: "10"}}
        return f"RF-PHY/RCV/IQDR/BV-{codes[mode][slot]}-C" if mode in codes else None
    return None


def _rf_phy_derived(config: dict[str, Any]) -> dict[str, Any]:
    test = config["test"]
    test_id = _rf_phy_test_id(config)
    if test_id is None:
        return {"test_id": None, "frequency_span": None,
                "channel_filter_frequencies": [], "channel_filter_amplitudes": [],
                "payload_sequence": None, "interferer1_payload_sequence": None}
    payload = ("11111111" if config["mode"] == "LE125K" else "1110111001000100"
               if test == "Modulation characteristics" else
               "11111111" if test == "Carrier frequency offset and drift" and config["mode"] == "LE125K" else
               "11110000" if test == "Carrier frequency offset and drift" and config["packet_type"] == "ConnectionCTE" else
               "10101010" if test == "Carrier frequency offset and drift" else "PRBS9")
    return {"test_id": test_id,
            "frequency_span": 0 if test in {"Output power", "Tx power stability"} else 1e6,
            "channel_filter_frequencies": [value * (2 if config["mode"] == "LE2M" else 1)
                                           for value in [550e3, 650e3, 1e6, 2e6]],
            "channel_filter_amplitudes": [0.25, -3, -14, -44],
            "payload_sequence": payload,
            "interferer1_payload_sequence": "PRBS15"}


def _adapter_configuration(kind: str, properties: dict) -> dict:
    if kind == "angle":
        return angle_configuration(properties)
    factories = {"l2cap": l2cap_configuration, "att": att_configuration,
                 "gap_data": gap_data_configuration, "advertising": advertising_configuration,
                 "ll_control": control_configuration, "ll_data": data_configuration}
    if kind in factories:
        return factories[kind](properties)
    if kind == "path_loss":
        unknown = set(properties) - set(PATH_LOSS_DEFAULTS)
        if unknown:
            raise InputError("unsupported path-loss configuration fields: " + ", ".join(sorted(unknown)))
        config = {**PATH_LOSS_DEFAULTS, **properties}
        # Reuse the production argument validator without consuming random
        # state: an explicit zero shadowing value makes this deterministic.
        path_loss(1.0, **config, shadow_fading_db=0)
        return config
    if kind == "range":
        unknown = set(properties) - set(RANGE_DEFAULTS)
        if unknown:
            raise InputError("unsupported range configuration fields: " + ", ".join(sorted(unknown)))
        config = {**RANGE_DEFAULTS, **properties}
        range_estimate(config)
        return config
    raise InputError("unsupported adapter configuration")


def _configuration(object_type: str, properties: dict) -> dict:
    family, kind = CONFIG_KINDS[object_type]
    if family == "classic":
        return classic_configuration(kind, properties)
    if family == "le":
        return le_configuration(kind, properties)
    return _adapter_configuration(kind, properties)


def _finite_number(value: Any, name: str, *, lower: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f"{name} must be a finite number")
    value = float(value)
    if lower is not None and value < lower:
        raise InputError(f"{name} must be at least {lower}")
    return value


def _vector3(value: Any, name: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 3:
        raise InputError(f"{name} must contain three finite numbers")
    return [_finite_number(item, name) for item in value]


def _integer(value: Any, name: str, lower: int, upper: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not lower <= value <= upper:
        raise InputError(f"{name} must be an integer in {lower}..{upper}")
    return value


def _payload_bits(value: Any, length: Any) -> list[int]:
    if value is not None:
        return bit_vector(value, "traffic.payload_bits", max_length=251 * 8).tolist()
    octets = _integer(0 if length is None else length, "traffic.payload_length", 0, 251)
    # A zero-filled default is deterministic and makes the traffic descriptor
    # fully serializable.  Callers needing a test pattern pass payload_bits.
    return [0] * (octets * 8)


def _node_payload(descriptor: dict[str, Any]) -> dict[str, Any]:
    return {
        "descriptor": descriptor,
        "runtime": {
            "traffic_sources": [], "next_traffic_id": 1,
            "tx_buffer": [], "rx_buffer": [],
            "statistics": {
                "transmitted_packets": 0, "received_packets": 0,
                "dropped_packets": 0, "manual_received_packets": 0,
            },
            "connections": [],
            "mobility": None,
            "scheduler": {"policy": "round_robin"},
        },
    }


def create_object(object_type: str, properties: Any) -> dict[str, Any]:
    """Construct one serializable object payload from its public properties."""
    if object_type not in PUBLIC_OBJECT_KINDS:
        choices = ", ".join(sorted(PUBLIC_OBJECT_KINDS))
        raise InputError(f"object_type is unsupported; choose one of {choices}")
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise InputError("properties must be a JSON object")
    if object_type in CONFIG_KINDS:
        return {"configuration": _configuration(object_type, properties)}
    if object_type in NODE_KINDS:
        allowed = {
            "role", "position", "positions", "name", "names", "properties", "start_id",
            "lap", "uap", "connection_config", "gap_config", "mesh_config",
        }
        unknown = set(properties) - allowed
        if unknown:
            raise InputError("unsupported node fields: " + ", ".join(sorted(unknown)))
        values = dict(properties)
        if "position" in values:
            if "positions" in values:
                raise InputError("provide position or positions, not both")
            values["positions"] = [values.pop("position")]
        if "name" in values:
            if "names" in values:
                raise InputError("provide name or names, not both")
            values["names"] = [values.pop("name")]
        nodes = create_nodes(NODE_KINDS[object_type], **values)
        if len(nodes) != 1:
            raise InputError("a session object represents exactly one node; provide one position")
        return _node_payload(nodes[0])
    settings = _settings(properties)
    return {"settings": settings, "dynamic": _initial_dynamic()}


def public_value(object_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Return the stable public view without transient queues."""
    if object_type in CONFIG_KINDS:
        value = deepcopy(payload["configuration"])
        if object_type == "bluetoothRFPHYTestConfig":
            value.update(_rf_phy_derived(value))
        if payload.get("associations"):
            value["associations"] = deepcopy(payload["associations"])
        return value
    if object_type in NODE_KINDS:
        descriptor = deepcopy(payload["descriptor"])
        runtime = payload["runtime"]
        descriptor.update({
            "traffic_source_count": len(runtime["traffic_sources"]),
            "transmit_buffer_count": len(runtime["tx_buffer"]),
            "receive_buffer_count": len(runtime["rx_buffer"]),
            "statistics": deepcopy(runtime["statistics"]),
            "mobility": deepcopy(runtime["mobility"]),
            "scheduler": deepcopy(runtime["scheduler"]),
            "connections": deepcopy(runtime["connections"]),
        })
        return descriptor
    return {"settings": deepcopy(payload["settings"]), "dynamic": deepcopy(payload["dynamic"])}


def set_properties(object_type: str, payload: dict[str, Any], properties: Any) -> dict[str, Any]:
    if not isinstance(properties, dict) or not properties:
        raise InputError("properties must be a nonempty JSON object")
    if object_type in CONFIG_KINDS:
        current = dict(payload["configuration"])
        current.update(properties)
        payload["configuration"] = _configuration(object_type, current)
        return payload
    if object_type in NODE_KINDS:
        descriptor = payload["descriptor"]
        allowed = {"name", "position", "properties", "connection_config", "gap_config", "mesh_config"}
        unknown = set(properties) - allowed
        if unknown:
            raise InputError("unsupported mutable node fields: " + ", ".join(sorted(unknown)))
        base = {
            "role": descriptor["role"], "position": descriptor["position"], "name": descriptor["name"],
            "properties": descriptor["properties"], "connection_config": descriptor.get("connection_config"),
        }
        if object_type == "bluetoothLENode":
            base["gap_config"] = descriptor.get("gap_config")
            base["mesh_config"] = descriptor.get("mesh_config")
        base.update(properties)
        if object_type == "bluetoothNode":
            address = descriptor["node_address"]
            base["start_id"] = descriptor["id"]
            base["lap"] = int(address[:6], 16)
            base["uap"] = int(address[6:8], 16)
        else:
            base["start_id"] = descriptor["id"]
        recreated = create_object(object_type, base)
        recreated["runtime"] = payload["runtime"]
        return recreated
    updated = dict(payload["settings"])
    updated.update(properties)
    payload["settings"] = _settings(updated)
    return payload


def _append_buffer(buffer: list[dict[str, Any]], packet: dict[str, Any], name: str) -> None:
    if not isinstance(packet, dict):
        raise InputError(f"{name} must be a JSON object")
    if "bits" in packet:
        packet = dict(packet)
        packet["bits"] = bit_vector(packet["bits"], f"{name}.bits", max_length=251 * 8).tolist()
    buffer.append(deepcopy(packet))


def _traffic_source(node: dict[str, Any], arguments: Any, simulation_time: float) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise InputError("addTrafficSource arguments must be a JSON object")
    allowed = {"payload_bits", "payload_length", "interval", "start_time", "destination_ids", "max_packets", "name"}
    unknown = set(arguments) - allowed
    if unknown:
        raise InputError("unsupported traffic source fields: " + ", ".join(sorted(unknown)))
    interval = _finite_number(arguments.get("interval", 0.020), "traffic.interval", lower=0.000625)
    start_time = _finite_number(arguments.get("start_time", simulation_time), "traffic.start_time", lower=0)
    destinations = arguments.get("destination_ids", [])
    if not isinstance(destinations, list):
        raise InputError("traffic.destination_ids must be a list of node IDs")
    destinations = [_integer(item, "traffic.destination_ids item", 1, 65535) for item in destinations]
    if len(set(destinations)) != len(destinations):
        raise InputError("traffic.destination_ids must not contain duplicates")
    max_packets = arguments.get("max_packets")
    if max_packets is not None:
        max_packets = _integer(max_packets, "traffic.max_packets", 1, 1_000_000)
    runtime = node["runtime"]
    source_id = runtime["next_traffic_id"]
    runtime["next_traffic_id"] += 1
    source = {
        "id": source_id, "name": arguments.get("name", f"Traffic{source_id}"),
        "payload_bits": _payload_bits(arguments.get("payload_bits"), arguments.get("payload_length")),
        "interval": interval, "next_time": start_time, "destination_ids": destinations,
        "max_packets": max_packets, "sent_packets": 0,
    }
    if not isinstance(source["name"], str) or not source["name"]:
        raise InputError("traffic.name must be a nonempty string")
    runtime["traffic_sources"].append(source)
    return deepcopy(source)


def _add_mobility(node: dict[str, Any], arguments: Any, simulation_time: float) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise InputError("addMobility arguments must be a JSON object")
    if arguments.get("model", "constant_velocity") != "constant_velocity":
        raise InputError("only the deterministic constant_velocity mobility model is implemented")
    unknown = set(arguments) - {"model", "velocity"}
    if unknown:
        raise InputError("unsupported mobility fields: " + ", ".join(sorted(unknown)))
    velocity = _vector3(arguments.get("velocity"), "mobility.velocity")
    mobility = {"model": "constant_velocity", "velocity": velocity, "updated_at": simulation_time}
    node["runtime"]["mobility"] = mobility
    return deepcopy(mobility)


def _move(node: dict[str, Any], simulation_time: float) -> None:
    mobility = node["runtime"]["mobility"]
    if not mobility:
        return
    delta = simulation_time - mobility["updated_at"]
    if delta < -1e-12:
        raise InputError("simulation time cannot move backwards")
    if delta > 0:
        position = node["descriptor"]["position"]
        node["descriptor"]["position"] = [position[index] + delta * mobility["velocity"][index]
                                         for index in range(3)]
        mobility["updated_at"] = simulation_time


def _packet_relevant(receiver: dict[str, Any], packet: dict[str, Any]) -> bool:
    destination = packet.get("destination_id")
    return destination is None or destination == receiver["descriptor"]["id"]


def _received_power(transmitter: dict[str, Any], receiver: dict[str, Any]) -> float:
    tx_position = np.asarray(transmitter["descriptor"]["position"], dtype=float)
    rx_position = np.asarray(receiver["descriptor"]["position"], dtype=float)
    distance = max(float(np.linalg.norm(tx_position - rx_position)), 0.01)
    tx_radio = transmitter["descriptor"]["properties"]
    rx_radio = receiver["descriptor"]["properties"]
    loss = float(path_loss(distance, environment="Industrial", path_loss_exponent=2.0,
                           standard_deviation=0, transmitter_antenna_gain=tx_radio["transmitter_gain"],
                           receiver_antenna_gain=rx_radio["receiver_gain"])[0])
    power = tx_radio.get("transmitter_power", 20.0)
    return float(power - loss)


def _node_statistics(node: dict[str, Any]) -> dict[str, Any]:
    stats = deepcopy(node["runtime"]["statistics"])
    total = stats["received_packets"] + stats["dropped_packets"]
    stats["packet_error_rate"] = (stats["dropped_packets"] / total) if total else 0.0
    return stats


def invoke_object(
    object_type: str,
    payload: dict[str, Any],
    method: str,
    arguments: Any,
    simulation_time: float,
    emit: Callable[[str, str, dict[str, Any], float], None],
    object_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Invoke a supported method and return the updated payload plus result."""
    if not isinstance(method, str) or not method:
        raise InputError("method must be a nonempty string")
    if arguments is None:
        arguments = {}
    if object_type in CONFIG_KINDS:
        config = payload["configuration"]
        if object_type == "bleAngleEstimateConfig":
            if method == "getElementPosition":
                return payload, {"element_position": deepcopy(config["element_position"])}
            if method == "getNumElements":
                return payload, {"num_elements": config["array_size"]}
            if method == "validateConfig":
                return payload, {"valid": True}
        if object_type == "bluetoothPathLossConfig" and method == "pathLoss":
            if not isinstance(arguments, dict) or "distance" not in arguments:
                raise InputError("pathLoss requires {distance, optional shadow_fading_db}")
            allowed = {"distance", "shadow_fading_db"}
            if set(arguments) - allowed:
                raise InputError("pathLoss accepts distance and shadow_fading_db")
            values = dict(config)
            if "shadow_fading_db" in arguments:
                values["shadow_fading_db"] = arguments["shadow_fading_db"]
            result = path_loss(arguments["distance"], **values)
            return payload, {"path_loss_db": result.tolist()}
        if object_type == "bluetoothRangeConfig":
            if method == "estimate":
                return payload, range_estimate(config)
            if method == "pathLoss":
                if not isinstance(arguments, dict) or "distance" not in arguments:
                    raise InputError("pathLoss requires {distance}")
                values = {key: config[key] for key in PATH_LOSS_DEFAULTS if key in config}
                values["environment"] = config["environment"]
                values["transmitter_antenna_gain"] = config["transmitter_antenna_gain"]
                values["receiver_antenna_gain"] = config["receiver_antenna_gain"]
                values["transmitter_cable_loss"] = config["transmitter_cable_loss"]
                values["receiver_cable_loss"] = config["receiver_cable_loss"]
                values["transmitter_antenna_height"] = config["transmitter_antenna_height"]
                values["receiver_antenna_height"] = config["receiver_antenna_height"]
                values["path_loss_exponent"] = config["path_loss_exponent"]
                values["standard_deviation"] = config["standard_deviation"]
                values["shadow_fading_db"] = arguments.get("shadow_fading_db", 0)
                return payload, {"path_loss_db": path_loss(arguments["distance"], **values).tolist()}
            if method == "validateRxSensitivity":
                range_estimate(config)
                return payload, {"valid": True}
        if object_type == "bluetoothWaveformConfig":
            if method == "getPayloadLength":
                length = {"ID": 0, "NULL": 0, "POLL": 0, "FHS": 18,
                          "HV1": 10, "HV2": 20, "HV3": 30}.get(config["packet_type"], config["payload_length"])
                return payload, {"payload_length": length}
            if method == "getPhyConfigProperties":
                phy = classic_configuration("phy", {key: config[key] for key in
                    ("mode", "device_address", "modulation_index", "samples_per_symbol", "whiten_status", "whiten_initialization")})
                phy["has_extended_sco"] = config["packet_type"] in {"EV3", "EV4", "EV5", "2-EV3", "3-EV3", "2-EV5", "3-EV5"}
                phy["extended_sco_payload_length"] = config["payload_length"] if phy["has_extended_sco"] else phy["extended_sco_payload_length"]
                phy["is_id_packet"] = config["packet_type"] == "ID"
                return payload, {"phy_configuration": phy}
            if method == "validateConfig":
                return payload, {"valid": True}
        if object_type == "bluetoothLECISConfig" and method == "subeventLength":
            if not isinstance(arguments, dict) or set(arguments) != {"phy_mode"}:
                raise InputError("subeventLength requires exactly {phy_mode}")
            phy_mode = arguments["phy_mode"]
            if phy_mode not in {"LE1M", "LE2M", "LE500K", "LE125K"}:
                raise InputError("subeventLength phy_mode must be a Bluetooth LE PHY")
            # Bluetooth Toolbox uses the LE125K packet-duration expression
            # for both coded PHY choices in this timing calculation.
            duration_mode = "LE125K" if phy_mode == "LE500K" else phy_mode
            max_pdu = config["max_pdu"]
            pdu_lengths = max_pdu if isinstance(max_pdu, list) else [max_pdu, max_pdu]
            first, second = (packet_duration(duration_mode, "Disabled", int(length))[0]
                             for length in pdu_lengths)
            length_seconds = (first + second) / 1e6 + config["tifs"] + config["tmss"]
            return payload, {"subevent_length": length_seconds}
        if object_type in {"bluetoothRFPHYTestConfig", "bluetoothTestWaveformConfig"} and method == "validateConfig":
            return payload, {"valid": True}
        if method == "properties":
            return payload, {"configuration": public_value(object_type, payload)}
        if method == "reset":
            return create_object(object_type, {}), {"reset": True}
        raise InputError("unsupported configuration method; use properties, reset, or set for property assignment")
    if object_type == "bleChannelSelection":
        if method == "next":
            if not isinstance(arguments, dict):
                raise InputError("next arguments must be a JSON object")
            channels, dynamic = select(payload["settings"], dict(payload["dynamic"]),
                                       count=arguments.get("count", 1),
                                       isochronous_event_counter=arguments.get("isochronous_event_counter"),
                                       subevent_number=arguments.get("subevent_number"))
            payload["dynamic"] = dynamic
            return payload, {"channel_indices": channels, "event_counter": max(0, dynamic["event_counter"] - 1)}
        if method == "reset":
            payload["dynamic"] = _initial_dynamic()
            return payload, {"reset": True}
        raise InputError("bleChannelSelection supports next and reset")
    node = payload
    runtime = node["runtime"]
    if method == "addTrafficSource":
        source = _traffic_source(node, arguments, simulation_time)
        emit(object_id, "TrafficSourceAdded", {"source_id": source["id"], "name": source["name"]}, simulation_time)
        return payload, {"traffic_source": source}
    if method == "addMobility":
        mobility = _add_mobility(node, arguments, simulation_time)
        emit(object_id, "MobilityAdded", mobility, simulation_time)
        return payload, {"mobility": mobility}
    if method == "updateChannelList":
        if not isinstance(arguments, dict) or set(arguments) != {"used_channels"}:
            raise InputError("updateChannelList requires exactly {used_channels}")
        config = node["descriptor"].get("connection_config")
        if config is None:
            config = {} if object_type == "bluetoothLENode" else {"used_channels": list(range(79))}
        config = dict(config)
        config["used_channels"] = arguments["used_channels"]
        if object_type == "bluetoothLENode":
            node["descriptor"]["connection_config"] = le_configuration("bluetoothLEConnectionConfig", config)
        else:
            node["descriptor"]["connection_config"] = classic_configuration("connection", config)
        emit(object_id, "ChannelListUpdated", {"used_channels": config["used_channels"]}, simulation_time)
        return payload, {"configuration": deepcopy(node["descriptor"]["connection_config"])}
    if method == "configureScheduler":
        if object_type != "bluetoothNode":
            raise InputError("configureScheduler is a Bluetooth Classic node method")
        if not isinstance(arguments, dict) or set(arguments) - {"policy", "poll_interval"}:
            raise InputError("configureScheduler accepts policy and poll_interval")
        policy = arguments.get("policy", "round_robin")
        if policy not in {"round_robin", "strict_priority"}:
            raise InputError("scheduler.policy must be round_robin or strict_priority")
        scheduler = {"policy": policy}
        if "poll_interval" in arguments:
            scheduler["poll_interval"] = _finite_number(arguments["poll_interval"], "scheduler.poll_interval", lower=0.000625)
        runtime["scheduler"] = scheduler
        return payload, {"scheduler": deepcopy(scheduler)}
    if method == "pushReceivedPacket":
        packet = arguments.get("packet") if isinstance(arguments, dict) else None
        _append_buffer(runtime["rx_buffer"], packet, "packet")
        runtime["statistics"]["manual_received_packets"] += 1
        emit(object_id, "PacketReceived", {"manual": True}, simulation_time)
        return payload, {"receive_buffer_count": len(runtime["rx_buffer"])}
    if method == "pullTransmittedPacket":
        packet = runtime["tx_buffer"].pop(0) if runtime["tx_buffer"] else None
        return payload, {"packet": packet}
    if method == "isPacketRelevant":
        packet = arguments.get("packet") if isinstance(arguments, dict) else None
        if not isinstance(packet, dict):
            raise InputError("isPacketRelevant requires {packet: {...}}")
        return payload, {"relevant": _packet_relevant(node, packet)}
    if method == "statistics":
        return payload, {"statistics": _node_statistics(node)}
    if method == "kpi":
        stats = _node_statistics(node)
        return payload, {"kpi": {"packet_error_rate": stats["packet_error_rate"],
                                  "throughput_packets": stats["received_packets"]}}
    if method == "run":
        if not isinstance(arguments, dict) or set(arguments) != {"current_time"}:
            raise InputError("node run requires exactly {current_time}; use session run to deliver traffic")
        current = _finite_number(arguments["current_time"], "current_time", lower=0)
        _move(node, current)
        next_times = [source["next_time"] for source in runtime["traffic_sources"]
                      if source["max_packets"] is None or source["sent_packets"] < source["max_packets"]]
        return payload, {"next_invoke_time": min(next_times) if next_times else None,
                         "position": deepcopy(node["descriptor"]["position"])}
    if method == "registerEventCallback":
        raise InputError("arbitrary callbacks are not supported; use the session subscribe operation")
    raise InputError("unsupported node method")


def run_nodes(
    objects: dict[str, tuple[str, dict[str, Any]]],
    start_time: float,
    until: float,
    emit: Callable[[str, str, dict[str, Any], float], None],
) -> dict[str, Any]:
    """Advance the deterministic node simulation and return a compact summary."""
    if until < start_time:
        raise InputError("until must not be earlier than the current simulation time")
    nodes = {object_id: payload for object_id, (kind, payload) in objects.items() if kind in NODE_KINDS}
    for node in nodes.values():
        _move(node, until)
    transmissions = 0
    deliveries = 0
    drops = 0
    schedule: list[tuple[float, str, dict[str, Any]]] = []
    for source_id, node in nodes.items():
        for source in node["runtime"]["traffic_sources"]:
            while source["next_time"] <= until + 1e-12 and (source["max_packets"] is None or source["sent_packets"] < source["max_packets"]):
                if source["next_time"] >= start_time - 1e-12:
                    schedule.append((source["next_time"], source_id, source))
                source["next_time"] += source["interval"]
    for time, sender_id, source in sorted(schedule, key=lambda item: (item[0], item[1], item[2]["id"])):
        sender = nodes[sender_id]
        source["sent_packets"] += 1
        destinations = source["destination_ids"] or [node["descriptor"]["id"] for key, node in nodes.items() if key != sender_id]
        for destination_id in destinations:
            packet = {"bits": source["payload_bits"], "source_id": sender["descriptor"]["id"],
                      "destination_id": destination_id, "time": time, "traffic_source_id": source["id"]}
            sender["runtime"]["tx_buffer"].append(deepcopy(packet))
            sender["runtime"]["statistics"]["transmitted_packets"] += 1
            transmissions += 1
            emit(sender_id, "PacketTransmissionStarted", {"destination_id": destination_id,
                 "traffic_source_id": source["id"], "bit_count": len(source["payload_bits"])}, time)
            receivers = [(key, node) for key, node in nodes.items() if node["descriptor"]["id"] == destination_id]
            if not receivers:
                sender["runtime"]["statistics"]["dropped_packets"] += 1
                drops += 1
                emit(sender_id, "PacketDropped", {"reason": "unknown_destination", "destination_id": destination_id}, time)
                continue
            receiver_id, receiver = receivers[0]
            power = _received_power(sender, receiver)
            if power >= receiver["descriptor"]["properties"]["receiver_sensitivity"]:
                delivered = dict(packet)
                delivered["received_power_dbm"] = power
                receiver["runtime"]["rx_buffer"].append(delivered)
                receiver["runtime"]["statistics"]["received_packets"] += 1
                deliveries += 1
                emit(receiver_id, "PacketReceived", {"source_id": packet["source_id"],
                     "traffic_source_id": source["id"], "received_power_dbm": power}, time)
            else:
                receiver["runtime"]["statistics"]["dropped_packets"] += 1
                drops += 1
                emit(receiver_id, "PacketDropped", {"reason": "below_sensitivity", "source_id": packet["source_id"],
                     "received_power_dbm": power}, time)
    return {"start_time": start_time, "until": until, "transmissions": transmissions,
            "deliveries": deliveries, "drops": drops, "node_count": len(nodes)}
