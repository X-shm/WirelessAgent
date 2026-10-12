"""Validate BLE localization estimates against R2026a golden samples."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ble_position_estimate import estimate

samples = json.loads(
    (ROOT / "matlab_oracle" / "samples" / "bluetooth_core_samples.json").read_text(encoding="utf-8")
)["positions"]
for sample in samples:
    kwargs = {
        name: sample[name]
        for name in ("distance", "direction")
        if sample[name]
    }
    got = estimate(sample["locator_positions"], sample["method"], **kwargs)
    expected = np.asarray(sample["position"], dtype=float)
    error = np.max(np.abs(got - expected))
    assert got.shape == expected.shape and error < 1e-10, (sample["method"], error)
print(f"PASS {len(samples)} BLE position-estimate golden samples")
