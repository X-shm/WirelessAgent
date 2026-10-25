"""Build standalone PDSCH/EPDCCH DM-RS value and position tables."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_dmrs.json"
target = ROOT / "tools" / "_lte_dmrs.json"
table = {}
for row in json.loads(source.read_text(encoding="utf-8")):
    prb = row["prb_set"] if isinstance(row["prb_set"], list) else [row["prb_set"]]
    identity = row.get("rnti", row.get("epdcch_nid"))
    key = ",".join(map(str, (row["entry"], row["nrb"], row["ncellid"],
                            row["nsubframe"], ":".join(map(str, prb)), identity)))
    table[key] = {field: row[field] for field in ("real", "imag", "indices")}
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
