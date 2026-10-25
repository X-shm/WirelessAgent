"""Headless, deterministic network event simulation for agent workflows."""
from __future__ import annotations

import heapq
import math

from _nr_remaining_common import run_cli


def _vector(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{name} must have three coordinates")
    vector = [float(x) for x in value]
    if not all(math.isfinite(x) for x in vector):
        raise ValueError(f"{name} must be finite")
    return vector


def _positive(value, name, allow_zero=False):
    number = float(value)
    if not math.isfinite(number) or (number < 0 if allow_zero else number <= 0):
        raise ValueError(f"{name} must be {'nonnegative' if allow_zero else 'positive'} and finite")
    return number


def wireless_network_simulator(duration_s, nodes, transmissions=None, actions=None,
                               cancel_actions=None, channel_model="free_space",
                               frequency_hz=2.4e9, max_events=100000):
    """Run declarative addNodes/scheduleAction/cancelAction/run operations.

    Packet reception uses ideal or free-space line-of-sight path loss and a
    receiver sensitivity threshold. It does not execute user code callbacks.
    """
    duration_s = _positive(duration_s, "duration_s", allow_zero=True)
    frequency_hz = _positive(frequency_hz, "frequency_hz")
    if channel_model not in ("ideal", "free_space"):
        raise ValueError("channel_model must be ideal or free_space")
    if not isinstance(max_events, int) or not 1 <= max_events <= 1000000:
        raise ValueError("max_events must be an integer in [1,1000000]")
    if not isinstance(nodes, list) or not isinstance(transmissions or [], list) or not isinstance(actions or [], list):
        raise ValueError("nodes, transmissions and actions must be arrays")
    by_id = {}
    for item in nodes:
        if not isinstance(item, dict):
            raise ValueError("each node must be an object")
        node_id = item.get("node_id")
        if not isinstance(node_id, int) or isinstance(node_id, bool) or node_id < 1 or node_id in by_id:
            raise ValueError("node_id must be a unique positive integer")
        by_id[node_id] = {"node_id": node_id, "name": item.get("name", f"Node{node_id}"),
                          "position": _vector(item.get("position", [0, 0, 0]), "position"),
                          "velocity": _vector(item.get("velocity", [0, 0, 0]), "velocity"),
                          "receive_sensitivity_dbm": float(item.get("receive_sensitivity_dbm", -90)),
                          "transmit_power_dbm": float(item.get("transmit_power_dbm", 0))}
        if not all(math.isfinite(by_id[node_id][key]) for key in ("receive_sensitivity_dbm", "transmit_power_dbm")):
            raise ValueError("node power values must be finite")
    if not by_id:
        raise ValueError("at least one node is required")
    cancelled = set(cancel_actions or [])
    if not all(isinstance(x, (str, int)) for x in cancelled):
        raise ValueError("cancel_actions must contain action identifiers")
    queue = []
    serial = 0
    for action in actions or []:
        if not isinstance(action, dict):
            raise ValueError("each action must be an object")
        action_id = action.get("id", serial + 1)
        phase = action.get("phase", "during")
        if phase not in ("pre", "during", "post"):
            raise ValueError("action phase must be pre/during/post")
        time = _positive(action.get("time_s", 0), "action time", allow_zero=True)
        if phase == "during" and time > duration_s:
            raise ValueError("scheduled action exceeds simulation duration")
        heapq.heappush(queue, ((-1 if phase == "pre" else duration_s + 1 if phase == "post" else time),
                               serial, "action", action_id, action))
        serial += 1
    for packet in transmissions or []:
        if not isinstance(packet, dict):
            raise ValueError("each transmission must be an object")
        time = _positive(packet.get("time_s", 0), "transmission time", allow_zero=True)
        if time > duration_s:
            raise ValueError("transmission exceeds simulation duration")
        sender = packet.get("transmitter_id")
        receiver = packet.get("receiver_id")
        if sender not in by_id or receiver not in by_id or sender == receiver:
            raise ValueError("transmitter_id and receiver_id must be distinct registered nodes")
        size = packet.get("size_bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ValueError("size_bytes must be a nonnegative integer")
        heapq.heappush(queue, (time, serial, "transmission", None, packet))
        serial += 1
    if len(queue) > max_events:
        raise ValueError("event count exceeds max_events")
    events, results, executed = [], [], []
    while queue:
        sort_time, _, kind, action_id, data = heapq.heappop(queue)
        if kind == "action":
            if action_id not in cancelled:
                executed.append({"id": action_id, "phase": data.get("phase", "during"),
                                 "time_s": 0 if sort_time < 0 else duration_s if sort_time > duration_s else sort_time,
                                 "payload": data.get("payload")})
            continue
        time = sort_time
        sender = by_id[data["transmitter_id"]]
        receiver = by_id[data["receiver_id"]]
        tx_pos = [p + time * v for p, v in zip(sender["position"], sender["velocity"])]
        rx_pos = [p + time * v for p, v in zip(receiver["position"], receiver["velocity"])]
        distance = math.dist(tx_pos, rx_pos)
        tx_power = float(data.get("transmit_power_dbm", sender["transmit_power_dbm"]))
        if not math.isfinite(tx_power):
            raise ValueError("transmit_power_dbm must be finite")
        # Friis free-space loss in dB, with a 1 m floor to avoid singularity.
        path_loss = 0.0 if channel_model == "ideal" else 20 * math.log10(4 * math.pi * max(1.0, distance) * frequency_hz / 299792458)
        rx_power = tx_power - path_loss
        received = rx_power >= receiver["receive_sensitivity_dbm"]
        summary = {"time_s": time, "transmitter_id": sender["node_id"],
                   "receiver_id": receiver["node_id"], "size_bytes": data["size_bytes"],
                   "distance_m": distance, "path_loss_db": path_loss,
                   "received_power_dbm": rx_power, "received": received}
        results.append(summary)
        events.append({"EventName": "TransmissionStarted", "NodeID": sender["node_id"],
                       "NodeName": sender["name"], "Timestamp": time,
                       "EventData": {"ReceiverID": receiver["node_id"], "PacketSize": data["size_bytes"]}})
        events.append({"EventName": "ReceptionEnded", "NodeID": receiver["node_id"],
                       "NodeName": receiver["name"], "Timestamp": time,
                       "EventData": {"TransmitterID": sender["node_id"], "Received": received,
                                     "ReceivedPowerDBm": rx_power}})
    return {"current_time_s": duration_s, "end_time_s": duration_s,
            "nodes": list(by_id.values()), "channel_model": channel_model,
            "transmissions": results, "events": events, "executed_actions": executed,
            "cancelled_action_ids": sorted(cancelled, key=str)}


if __name__ == "__main__":
    run_cli("Wireless Network Toolbox declarative discrete event simulator", {
        "wirelessNetworkSimulator": wireless_network_simulator,
    })
