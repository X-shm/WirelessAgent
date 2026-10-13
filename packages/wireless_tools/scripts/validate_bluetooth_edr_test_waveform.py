"""Compare EDR RF-PHY test waveforms against MATLAB R2026a."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bluetooth_test_waveform import generate

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "bluetooth_edr_test_waveform_samples.json").read_text(encoding="utf-8"))
for case in cases:
    wave, detail = generate({"mode": case["mode"],
                             "packet_type": case["packet_type"],
                             "payload_type": case["payload_type"]})
    assert wave.size == case["waveform_length"], case["packet_type"]
    assert len(detail["message_bits"]) == 8 * case["fixed_payload_length"]
    indices = np.asarray(case["sample_indices"], dtype=int) - 1
    expected = np.asarray(case["waveform_real"]) + 1j * np.asarray(case["waveform_imag"])
    error = float(np.max(np.abs(wave[indices] - expected)))
    assert error < 1e-10, (case["packet_type"], error)
print(f"PASS {len(cases)} Bluetooth EDR test waveform golden cases")
