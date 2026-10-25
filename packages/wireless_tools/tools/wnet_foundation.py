"""Python agent forms of public wnet namespace classes."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import run_cli


TECHNOLOGIES = {"WLAN": 1, "NR5G": 2, "BluetoothLE": 3,
                "BluetoothBREDR": 4, **{f"Custom{i}": 100+i for i in range(1, 10)}}


def technology_type(name=None, code=None):
    if name is not None and name not in TECHNOLOGIES:
        raise ValueError("unknown technology name")
    if code is not None and code not in TECHNOLOGIES.values():
        raise ValueError("unknown technology code")
    if name is not None and code is not None and TECHNOLOGIES[name] != code:
        raise ValueError("technology name and code differ")
    return {"constants": TECHNOLOGIES, "name": name or next((key for key, value in TECHNOLOGIES.items()
                                                              if value == code), None),
            "code": TECHNOLOGIES.get(name, code)}


def _position(value, field):
    array = np.asarray(value, float)
    if array.shape != (3,) or np.any(~np.isfinite(array)):
        raise ValueError(f"{field} must contain three finite coordinates")
    return array.tolist()


def node(node_id: int, name=None, position=(0, 0, 0), velocity=(0, 0, 0),
         technology_type=101, transmit_power_dbm=0, receive_sensitivity_dbm=-90,
         traffic=None):
    if int(node_id) != node_id or node_id < 1:
        raise ValueError("node_id must be a positive integer")
    if technology_type not in TECHNOLOGIES.values():
        raise ValueError("invalid technology_type")
    if not np.isfinite(transmit_power_dbm) or not np.isfinite(receive_sensitivity_dbm):
        raise ValueError("power values must be finite")
    if traffic is not None and not isinstance(traffic, dict):
        raise ValueError("traffic must be a traffic descriptor")
    return {"node_id": int(node_id), "name": name or f"Node{node_id}",
            "position": _position(position, "position"),
            "velocity": _position(velocity, "velocity"),
            "technology_type": technology_type, "transmit_power_dbm": float(transmit_power_dbm),
            "receive_sensitivity_dbm": float(receive_sensitivity_dbm), "traffic": traffic}


def mobility(model="constant_velocity", initial_position=(0, 0, 0), times=None,
             velocity=(0, 0, 0), **parameters):
    if times is None:
        return {"abstract_class": "wnet.Mobility", "models": ["constant_velocity", "random_walk", "random_waypoint"]}
    if model == "constant_velocity":
        from node_mobility_constant_velocity import constant_velocity
        samples = constant_velocity(initial_position, velocity, times)
        return {"times": times, "positions": samples}
    raise ValueError("use dedicated node_mobility_random_walk/random_waypoint for sampled random models")


def traffic(model=None, params=None):
    choices = ["networkTrafficFTP", "networkTrafficOnOff", "networkTrafficVideoConference", "networkTrafficVoIP"]
    if model is None:
        return {"abstract_class": "wnet.Traffic", "models": choices}
    if model not in choices or not isinstance(params, dict):
        raise ValueError("model must be a public traffic class and params a JSON object")
    return {"model": model, "params": params}


def fifo_queue(operations, max_size: int = 100):
    if int(max_size) != max_size or max_size < 1 or not isinstance(operations, list):
        raise ValueError("positive max_size and operations list required")
    queue, lengths, results = [], [], []
    for operation in operations:
        if not isinstance(operation, dict):
            raise ValueError("each operation must be an object")
        kind = operation.get("operation")
        if kind == "enqueue":
            size = operation.get("packet_size", 0)
            if int(size) != size or size < 0:
                raise ValueError("packet_size must be a nonnegative integer")
            queued = len(queue) < max_size
            if queued:
                queue.append(operation.get("packet"))
                lengths.append(int(size))
            results.append({"queued": queued})
        elif kind == "dequeue":
            results.append({"packet": queue.pop(0) if queue else []})
            if lengths:
                lengths.pop(0)
        elif kind == "peek":
            results.append({"packet": queue[0] if queue else []})
        elif kind == "isFull":
            results.append({"full": len(queue) == max_size})
        elif kind == "setMaxSize":
            value = operation.get("max_size")
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError("new max_size must be a positive integer")
            if queue and value <= len(queue):
                results.append({"max_size": max_size, "changed": False,
                                "warning": "new MaxSize must exceed CurrentSize"})
            else:
                max_size = value
                results.append({"max_size": max_size, "changed": True})
        else:
            raise ValueError("operation must be enqueue/dequeue/peek/isFull/setMaxSize")
    return {"results": results, "current_size": len(queue),
            "current_size_bytes": sum(lengths), "max_size": max_size,
            "queue": queue}


if __name__ == "__main__":
    run_cli("Public wnet namespace class slices", {
        "wnet.FIFOQueue": fifo_queue, "wnet.Mobility": mobility,
        "wnet.Node": node, "wnet.TechnologyType": technology_type,
        "wnet.Traffic": traffic,
    })
