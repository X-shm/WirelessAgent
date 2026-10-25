"""Build standalone NB-IoT NPUSCH Data DRS sample table."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_npusch_drs.json"
target = ROOT / "tools" / "_lte_npusch_drs.json"
table = {}
for row in json.loads(source.read_text(encoding="utf-8")):
    subcarriers = row["subcarriers"] if isinstance(row["subcarriers"], list) else [row["subcarriers"]]
    key = ",".join(map(str, (row["spacing"], ":".join(map(str, subcarriers)),
                            row["ncellid"], row["slot"], row["nul_slots"])))
    table[key] = {field: row[field] for field in ("real", "imag", "state")}
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
