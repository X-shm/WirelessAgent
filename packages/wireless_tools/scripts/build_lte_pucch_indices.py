"""Build standalone PUCCH data and DRS RE tables from verified samples."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_pucch_indices.json"
target = ROOT / "tools" / "_lte_pucch_indices.json"
table = {}
for item in json.loads(source.read_text(encoding="utf-8")):
    key = ",".join(map(str, (item["entry"], item["nrb"], item["ncellid"],
                            item["nsubframe"], item["cyclic_prefix"],
                            item["resource_idx"])))
    table[key] = item["indices"]
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
