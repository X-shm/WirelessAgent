"""Compare EDR2M/EDR3M ideal receiver output to MATLAB R2026a."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bluetooth_classic_receiver import receive
from bluetooth_classic_waveform import generate

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "bluetooth_edr_receiver_samples.json").read_text(encoding="utf-8"))
for case in cases:
    kind = case["packet_type"]
    wave, _ = generate(np.asarray(case["message"], dtype=np.uint8), {
        "mode": case["mode"], "packet_type": kind,
        "payload_length": case["payload_length"]})
    props = {"mode": case["mode"], "is_id_packet": kind == "ID"}
    if "EV" in kind:
        props.update(has_extended_sco=True,
                     extended_sco_payload_length=case["payload_length"])
    decoded = receive(wave, props)
    info = decoded["decoded_info"]
    assert decoded["bits"] == case["bits"], kind
    assert info["packet_type"] == case["decoded_packet_type"], (kind, info)
    assert info["payload_length"] == case["decoded_payload_length"], kind
    assert info["lap"] == case["lap"], kind
    assert decoded["packet_valid"] == case["packet_valid"], (kind, decoded)
with tempfile.TemporaryDirectory() as folder:
    sample = next(item for item in cases if item["packet_type"] == "3-DH1")
    path = str(Path(folder) / "waveform.npz")
    tx = subprocess.run([sys.executable, str(ROOT / "tools" / "bluetooth_classic_waveform.py"),
                         "--input", json.dumps({"message": sample["message"],
                             "properties": {"mode": sample["mode"],
                                 "packet_type": sample["packet_type"],
                                 "payload_length": sample["payload_length"]}}),
                         "--output_file", path, "--inline_limit", "1"],
                        capture_output=True, text=True)
    assert tx.returncode == 0, tx.stdout + tx.stderr
    rx = subprocess.run([sys.executable, str(ROOT / "tools" / "bluetooth_classic_receiver.py"),
                         "--input", json.dumps({"waveform_file": path,
                             "properties": {"mode": sample["mode"]}})],
                        capture_output=True, text=True)
    assert rx.returncode == 0, rx.stdout + rx.stderr
    assert json.loads(rx.stdout)["result"]["bits"] == sample["bits"]
print(f"PASS {len(cases)} Bluetooth EDR receiver golden cases")
