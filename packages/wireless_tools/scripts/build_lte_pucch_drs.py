"""Build standalone PUCCH 1/2/3 DRS sequence tables."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_pucch_drs.json"
target = ROOT / "tools" / "_lte_pucch_drs.json"
table = {}
for item in json.loads(source.read_text(encoding="utf-8")):
    ack = item["ack"] if isinstance(item["ack"], list) else [item["ack"]]
    key = ",".join(map(str, (item["entry"], item["nrb"], item["ncellid"],
                            item["nsubframe"], item["cyclic_prefix"],
                            item["resource_idx"], "".join(map(str, ack)))))
    table[key] = {field: item[field] for field in ("real", "imag", "info")}
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
