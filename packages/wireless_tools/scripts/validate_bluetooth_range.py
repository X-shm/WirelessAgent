"""Validate Bluetooth range estimates against R2026a golden samples."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bluetooth_range import estimate

samples = json.loads(
    (ROOT / "matlab_oracle" / "samples" / "bluetooth_core_samples.json").read_text(encoding="utf-8")
)["ranges"]
for sample in samples:
    request = {key: value for key, value in sample.items() if key not in {"range_m", "path_loss_db", "received_power_dbm"}}
    got = estimate(request)
    for key, expected in (("range_m", sample["range_m"]), ("path_loss_db", sample["path_loss_db"]), ("received_power_dbm", sample["received_power_dbm"])):
        assert np.max(np.abs(np.asarray(got[key]) - np.asarray(expected))) < 1e-10, (sample["environment"], key, got[key], expected)
print(f"PASS {len(samples)} Bluetooth range golden samples")
