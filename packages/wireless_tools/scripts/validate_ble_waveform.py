"""Validate LE1M/LE2M waveform generation against R2026a golden samples."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ble_waveform import generate

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "bluetooth_core_samples.json").read_text(encoding="utf-8"))["waveforms"]
for sample in samples:
    got, _ = generate(
        np.asarray(sample["message"], dtype=np.uint8), sample["mode"],
        sample["channel_index"], sample["samples_per_symbol"],
        pulse_length=sample["pulse_length"],
    )
    expected = np.asarray(sample["real"]) + 1j * np.asarray(sample["imag"])
    error = np.max(np.abs(got - expected))
    assert got.shape == expected.shape and error < 1e-11, (sample["mode"], error)
print(f"PASS {len(samples)} BLE waveform golden samples")
