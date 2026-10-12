"""Compare Classic/LE constructor descriptors against R2026a node objects."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bluetooth_nodes import InputError, create_nodes

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "bluetooth_nodes_samples.json").read_text(encoding="utf-8"))
total = 0
for case in cases:
    oracle = case["nodes"]
    if isinstance(oracle, dict):
        oracle = [oracle]
    request = case["request"]
    first = oracle[0]
    kwargs = {**request, "start_id": first["id"]}
    if case["kind"] == "classic":
        addresses = [node["node_address"] for node in oracle]
        if len(oracle) == 1:
            kwargs["lap"] = int(addresses[0][:6], 16)
            kwargs["uap"] = int(addresses[0][6:8], 16)
    got = create_nodes(case["kind"], **kwargs)
    assert len(got) == len(oracle), case
    for actual, expected in zip(got, oracle):
        assert actual["id"] == expected["id"]
        assert actual["name"] == expected["name"]
        assert actual["role"] == expected["role"]
        assert actual["position"] == expected["position"]
        assert actual["properties"] == expected["properties"]
        if case["kind"] == "classic" and len(oracle) > 1:
            # MATLAB assigns independent random addresses to vectorized nodes.
            assert actual["node_address"][-4:] == expected["node_address"][-4:]
        elif case["kind"] == "le":
            assert actual["node_address"] is None and expected["node_address"] == []
        else:
            assert actual["node_address"] == expected["node_address"]
        total += 1
for invalid in (
    {"kind": "le", "role": "broadcaster-observer", "positions": [[0, 0, 0], [1, 0, 0]]},
    {"kind": "classic", "role": "observer"},
    {"kind": "le", "properties": {"transmitter_power": 21}},
):
    try:
        create_nodes(**invalid)
    except InputError:
        pass
    else:
        raise AssertionError(f"invalid node request accepted: {invalid}")
print(f"PASS {total} Bluetooth Classic/LE node constructor golden cases")
