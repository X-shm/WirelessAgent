"""Compare Outdoor Bluetooth range inversion against R2026a."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bluetooth_range import estimate

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "bluetooth_outdoor_range_samples.json").read_text(encoding="utf-8"))
for case in cases:
    got = estimate(case["request"])
    assert np.max(np.abs(np.asarray(got["range_m"]) - case["range_m"])) < 1e-9, (
        case["request"], got["range_m"], case["range_m"])
    assert abs(got["path_loss_db"] - case["path_loss_db"]) < 1e-10
    assert abs(got["received_power_dbm"] - case["received_power_dbm"]) < 1e-10
print(f"PASS {len(cases)} Bluetooth Outdoor range golden cases")
