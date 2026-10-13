"""Exercise persisted Bluetooth object methods, traffic, events and restore."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "bluetooth_session.py"


def call(session_file: str, operation: str, **values):
    request = {"operation": operation, "session_file": session_file, **values}
    completed = subprocess.run([sys.executable, str(TOOL), "--input", json.dumps(request)],
                               text=True, capture_output=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    answer = json.loads(completed.stdout)
    assert answer["ok"], answer
    return answer["result"]


with tempfile.TemporaryDirectory() as directory:
    session = str(Path(directory) / "simulation.sqlite")
    restored = str(Path(directory) / "restored.sqlite")
    created = call(session, "create_session")
    assert created["created"] and created["simulation_time"] == 0
    angle = call(session, "create_object", object_type="bleAngleEstimateConfig", new_object_id="angle",
                 properties={"array_size": 3, "element_spacing": 0.25})
    assert angle["value"]["element_position"] == [[0.0, 0.0, 0.0], [0.0, 0.25, 0.5], [0.0, 0.0, 0.0]]
    assert call(session, "invoke", object_id="angle", method="getNumElements")["result"]["num_elements"] == 3
    changed = call(session, "invoke", object_id="angle", method="set", arguments={"element_spacing": 0.5})
    assert changed["result"]["value"]["element_position"][1] == [0.0, 0.5, 1.0]
    path_config = call(session, "create_object", object_type="bluetoothPathLossConfig", new_object_id="path",
                       properties={"environment": "Industrial", "standard_deviation": 0})
    loss = call(session, "invoke", object_id="path", method="pathLoss", arguments={"distance": [1, 10]})
    assert len(loss["result"]["path_loss_db"]) == 2
    waveform_config = call(session, "create_object", object_type="bluetoothWaveformConfig", new_object_id="waveform",
                           properties={"packet_type": "FHS"})
    assert call(session, "invoke", object_id="waveform", method="getPayloadLength")["result"]["payload_length"] == 18
    cis = call(session, "create_object", object_type="bluetoothLECISConfig", new_object_id="cis",
               properties={"max_pdu": [100, 200]})
    assert cis["value"]["max_pdu"] == [100, 200]
    assert call(session, "invoke", object_id="cis", method="subeventLength",
                arguments={"phy_mode": "LE1M"})["result"]["subevent_length"] == 0.00286
    assert call(session, "invoke", object_id="cis", method="subeventLength",
                arguments={"phy_mode": "LE500K"})["result"]["subevent_length"] == 0.02094
    rf = call(session, "create_object", object_type="bluetoothRFPHYTestConfig", new_object_id="rf",
              properties={"test": "Modulation characteristics"})
    assert rf["value"]["test_id"] == "RF-PHY/TRM/BV-09-C"
    assert rf["value"]["payload_sequence"] == "1110111001000100"
    rf_cte = call(session, "create_object", object_type="bluetoothRFPHYTestConfig", new_object_id="rf_cte",
                  properties={"test": "Tx power stability", "packet_type": "ConnectionCTE", "cte_type": [0, 1]})
    assert rf_cte["value"]["test_id"] == "RF-PHY/TRM/PS/BV-01-C"
    rf_unassigned = call(session, "create_object", object_type="bluetoothRFPHYTestConfig", new_object_id="rf_unassigned",
                         properties={"test": "Blocking", "mode": "LE125K"})
    assert rf_unassigned["value"]["test_id"] is None and rf_unassigned["value"]["frequency_span"] is None
    central = call(session, "create_object", object_type="bluetoothLENode", new_object_id="central",
                   properties={"role": "central", "position": [0, 0, 0], "start_id": 1,
                               "name": "Central", "properties": {"transmitter_power": 0}})
    peripheral = call(session, "create_object", object_type="bluetoothLENode", new_object_id="peripheral",
                      properties={"role": "peripheral", "position": [1, 0, 0], "start_id": 2,
                                  "name": "Peripheral"})
    assert central["value"]["id"] == 1 and peripheral["value"]["id"] == 2
    connection = call(session, "create_object", object_type="bluetoothLEConnectionConfig", new_object_id="connection")
    bound = call(session, "invoke", object_id="connection", method="configureConnection",
                 arguments={"central_object_id": "central", "peripheral_object_id": "peripheral"})
    assert bound["result"]["peer_node_ids"] == [2]
    subscription = call(session, "subscribe", event_types=["PacketReceived", "PacketDropped"])
    call(session, "invoke", object_id="central", method="addMobility",
         arguments={"model": "constant_velocity", "velocity": [1, 0, 0]})
    source = call(session, "invoke", object_id="central", method="addTrafficSource",
                  arguments={"payload_bits": [1, 0, 1, 0], "interval": 0.01,
                             "destination_ids": [2], "max_packets": 2})
    assert source["result"]["traffic_source"]["id"] == 1
    run = call(session, "run", duration=0.015)["simulation"]
    assert run["transmissions"] == 2 and run["deliveries"] == 2 and run["drops"] == 0, run
    receiver = call(session, "get", object_id="peripheral")
    assert receiver["value"]["statistics"]["received_packets"] == 2
    events = call(session, "events", subscription_id=subscription["subscription_id"], limit=20)
    assert [item["event_type"] for item in events["events"]] == ["PacketReceived", "PacketReceived"]
    snapshot = call(session, "snapshot", include_events=True)["snapshot"]
    assert snapshot["simulation_time"] == 0.015 and len(snapshot["objects"]) == 10
    call(restored, "create_session")
    restore = call(restored, "restore", snapshot=snapshot)
    assert restore["restored_objects"] == 10
    restored_receiver = call(restored, "get", object_id="peripheral")
    assert restored_receiver["value"]["statistics"]["received_packets"] == 2
    deleted = call(restored, "delete_object", object_id="path")
    assert deleted["deleted"]
    call(session, "close_session", delete=True)
    call(restored, "close_session", delete=True)
print("PASS Bluetooth session object/event/snapshot integration")
