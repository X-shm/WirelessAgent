"""Exercise public Wireless Network simulator, trace, IQ and support slices."""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from wnet_simulator import wireless_network_simulator
from wnet_logging import wireless_network_event_tracer, wireless_iq_logger
from wnet_support import wirelessnetwork_support_package_check


def main():
    nodes = [{"node_id": 1, "position": [0, 0, 0], "transmit_power_dbm": 20},
             {"node_id": 2, "position": [100, 0, 0], "receive_sensitivity_dbm": -90}]
    sim = wireless_network_simulator(
        1, nodes,
        transmissions=[{"time_s": .1, "transmitter_id": 1, "receiver_id": 2,
                        "size_bytes": 100}],
        actions=[{"id": "begin", "phase": "pre"}, {"id": "cancel", "time_s": .2},
                 {"id": "end", "phase": "post"}], cancel_actions=["cancel"])
    assert sim["current_time_s"] == 1
    assert sim["transmissions"][0]["received"] is True
    assert math.isclose(sim["transmissions"][0]["path_loss_db"], 80.052008, abs_tol=1e-5)
    assert [a["id"] for a in sim["executed_actions"]] == ["begin", "end"]
    assert [e["EventName"] for e in sim["events"]] == ["TransmissionStarted", "ReceptionEnded"]
    trace = wireless_network_event_tracer(sim["events"], event_name="ReceptionEnded", node_id=2)
    assert trace["count"] == 1 and trace["events"][0]["NodeID"] == 2
    assert wireless_network_event_tracer([{"EventName": "AppPacketGenerated", "NodeID": 1,
                                           "Timestamp": 0, "Payload": [1, 2]}])["events"][0].get("Payload") is None
    iq = wireless_iq_logger(1, {"real": [1, 0, -1, 0], "imag": [0, 1, 0, -1]},
                            2e6, sample_rate_hz=1e6)
    assert iq["sample_count"] == 2
    assert wirelessnetwork_support_package_check()["core_ready"]
    for method, args in ((wireless_network_simulator, (1, [{"node_id": 1}, {"node_id": 1}])),
                         (wireless_iq_logger, (1, [[1, 0]], 1e5))):
        try:
            method(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input accepted")
    print("PASS Wireless Network simulator, event tracer, IQ logger, support check")


if __name__ == "__main__":
    main()
