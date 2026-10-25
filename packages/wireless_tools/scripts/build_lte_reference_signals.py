"""Build standalone baseline CSI-RS and PRS value/position tables."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_reference_signals.json"
target = ROOT / "tools" / "_lte_reference_signals.json"
table = {}
for item in json.loads(source.read_text(encoding="utf-8")):
    key = ",".join(map(str, (item["entry"], item["nrb"], item["ncellid"],
                            item["nsubframe"], item.get("csi_ref_ports", 0))))
    table[key] = {field: item[field] for field in ("real", "imag", "indices")}
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
