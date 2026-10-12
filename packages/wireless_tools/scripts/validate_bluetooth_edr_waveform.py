"""Compare EDR2M/EDR3M packet waveforms against R2026a samples."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bluetooth_classic_waveform import generate

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "bluetooth_edr_waveform_samples.json").read_text(encoding="utf-8"))
for case in cases:
    wave, _ = generate(np.asarray(case["message"], dtype=np.uint8), {
        "mode": case["mode"], "packet_type": case["packet_type"],
        "payload_length": case["payload_length"]})
    assert wave.size == case["waveform_length"], case["packet_type"]
    indices = np.asarray(case["sample_indices"], dtype=int) - 1
    expected = np.asarray(case["waveform_real"]) + 1j * np.asarray(case["waveform_imag"])
    differences = np.abs(wave[indices] - expected)
    error = float(np.max(differences))
    if error >= 1e-10:
        first = int(np.flatnonzero(differences >= 1e-10)[0])
        raise AssertionError((case["packet_type"], error,
                              "first MATLAB sample index", int(indices[first] + 1),
                              "actual", wave[indices[first]], "expected", expected[first]))
print(f"PASS {len(cases)} Bluetooth EDR waveform golden cases")
