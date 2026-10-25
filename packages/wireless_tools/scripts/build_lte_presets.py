"""Build standalone R2026a LTE reference preset configurations."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_presets.json"
target = ROOT / "tools" / "_lte_presets.json"

table = {}
for record in json.loads(source.read_text(encoding="utf-8"))["records"]:
    key = "|".join((record["entry"], record["name"], record["duplex"],
                    record.get("bandwidth", "")))
    table[key] = record["config"]
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
