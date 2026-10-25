"""Build standalone EPDCCH data RE allocations from R2026a oracle samples."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_epdcch_indices.json"
target = ROOT / "tools" / "_lte_epdcch_indices.json"
table = {}
for row in json.loads(source.read_text(encoding="utf-8"))["records"]:
    prb = row["prb_set"] if isinstance(row["prb_set"], list) else [row["prb_set"]]
    key = ",".join(map(str, (row["nrb"], row["ncellid"], row["nsubframe"],
                            ":".join(map(str, prb)), row["cfi"], row["epdcch_type"])))
    table[key] = {"indices": row["indices"], "info": row["info"]}
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
