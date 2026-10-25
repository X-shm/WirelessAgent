"""Public wnet class slice checks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from wnet_foundation import fifo_queue, mobility, node, technology_type, traffic


def main():
    assert technology_type(name="WLAN")["code"] == 1
    assert technology_type(code=109)["name"] == "Custom9"
    assert node(2, position=[1, 2, 3])["node_id"] == 2
    assert mobility(times=[0, 2], velocity=[1, 0, 0])["positions"].tolist() == [[0, 0, 0], [2, 0, 0]]
    assert traffic("networkTrafficFTP", {"fixed_file_size_mb": 1})["model"] == "networkTrafficFTP"
    out = fifo_queue([{"operation": "enqueue", "packet": [1], "packet_size": 3},
                      {"operation": "peek"}, {"operation": "dequeue"},
                      {"operation": "isFull"}], 1)
    assert out["results"][1]["packet"] == [1]
    assert out["results"][2]["packet"] == [1]
    assert out["current_size"] == out["current_size_bytes"] == 0
    capped = fifo_queue([{"operation": "enqueue", "packet": 1, "packet_size": 2},
                         {"operation": "setMaxSize", "max_size": 1},
                         {"operation": "enqueue", "packet": 2, "packet_size": 3}], 1)
    assert capped["results"][1]["changed"] is False
    assert capped["results"][2]["queued"] is False
    assert capped["current_size_bytes"] == 2
    print("PASS 5 public wnet namespace class slices")


if __name__ == "__main__":
    main()
