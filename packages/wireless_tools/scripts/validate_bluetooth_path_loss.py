"""Validate deterministic Bluetooth path-loss cases against R2026a."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bluetooth_path_loss import path_loss

samples = json.loads(
    (ROOT / "matlab_oracle" / "samples" / "bluetooth_core_samples.json").read_text(encoding="utf-8")
)["path_loss"]
for sample in samples:
    kwargs = {name: sample[name] for name in sample if name not in {"distance", "path_loss_db"}}
    got = path_loss(sample["distance"], **kwargs)
    expected = np.asarray(sample["path_loss_db"], dtype=float)
    error = np.max(np.abs(got - expected))
    assert got.shape == expected.shape and error < 1e-10, (sample["environment"], error)
print(f"PASS {len(samples)} Bluetooth path-loss golden samples")
