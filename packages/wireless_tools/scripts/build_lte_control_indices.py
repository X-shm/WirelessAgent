"""Build standalone baseline LTE control RE allocations from oracle samples."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_control_indices.json"
target = ROOT / "tools" / "_lte_control_indices.json"
records = json.loads(source.read_text(encoding="utf-8"))
table = {}
for item in records:
    # PHICH resources are independent of CFI for the supported normal-duration case.
    if item["entry"] == "ltePHICHIndices" and item["cfi"] != 1:
        continue
    key = ",".join(str(item[field]) for field in
                   ("entry", "nrb", "ncellid", "ports", "cfi"))
    table[key] = item["indices"]
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
