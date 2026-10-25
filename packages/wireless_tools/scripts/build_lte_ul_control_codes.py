"""Build ACK/RI short codewords and CQI generator matrices."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_ul_control_codes.json"
target = ROOT / "tools" / "_lte_ul_control_codes.json"
table = {}
for item in json.loads(source.read_text(encoding="utf-8")):
    key = ",".join(map(str, (item["entry"], item["n"], item["qd"],
                            item["modulation"])))
    if item["entry"] == "lteCQI":
        table[key] = {"basis": [item["basis"]] if item["n"] == 1 else item["basis"]}
    else:
        table[key] = {"full": item["full"]}
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
