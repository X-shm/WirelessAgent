"""Compare LE125K/LE500K waveform and ideal RX with R2026a."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ble_ideal_receiver import receive
from ble_waveform import generate

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "ble_coded_phy_samples.json").read_text(encoding="utf-8"))
for case in cases:
    message = np.asarray(case["message"], dtype=np.uint8)
    waveform, _ = generate(message, mode=case["mode"],
                           channel_index=case["channel_index"],
                           samples_per_symbol=case["samples_per_symbol"],
                           pulse_length=case["pulse_length"],
                           modulation_index=case["modulation_index"],
                           whiten_status=case["whiten_status"])
    expected = np.asarray(case["waveform_real"]) + 1j * np.asarray(case["waveform_imag"])
    assert waveform.size == expected.size, (case["mode"], waveform.size, expected.size)
    error = float(np.max(np.abs(waveform - expected)))
    assert error < 1e-10, (case["mode"], case["pulse_length"], error)
    try:
        bits, address = receive(waveform, mode=case["mode"],
                                channel_index=case["channel_index"],
                                samples_per_symbol=case["samples_per_symbol"],
                                whiten_status=case["whiten_status"],
                                pulse_length=case["pulse_length"])
    except Exception as exc:
        raise AssertionError((case["mode"], case["pulse_length"],
                              case["modulation_index"], str(exc))) from exc
    assert bits.tolist() == case["bits"], (case["mode"], "bits")
    assert address.tolist() == case["access_address"], (case["mode"], "access_address")
with tempfile.TemporaryDirectory() as folder:
    sample = cases[0]
    path = str(Path(folder) / "waveform.npz")
    request = {"message": sample["message"], "mode": sample["mode"],
               "channel_index": sample["channel_index"],
               "samples_per_symbol": sample["samples_per_symbol"],
               "pulse_length": sample["pulse_length"]}
    tx = subprocess.run([sys.executable, str(ROOT / "tools" / "ble_waveform.py"),
                         "--input", json.dumps(request), "--output_file", path,
                         "--inline_limit", "1"], capture_output=True, text=True)
    assert tx.returncode == 0, tx.stdout + tx.stderr
    assert json.loads(tx.stdout)["artifacts"][0]["path"] == path
    rx_request = {"waveform_file": path, "mode": sample["mode"],
                  "channel_index": sample["channel_index"],
                  "samples_per_symbol": sample["samples_per_symbol"],
                  "pulse_length": sample["pulse_length"]}
    rx = subprocess.run([sys.executable, str(ROOT / "tools" / "ble_ideal_receiver.py"),
                         "--input", json.dumps(rx_request)], capture_output=True, text=True)
    assert rx.returncode == 0, rx.stdout + rx.stderr
    assert json.loads(rx.stdout)["result"]["bits"] == sample["bits"]
print(f"PASS {len(cases)} BLE coded PHY waveform/receiver golden cases")
