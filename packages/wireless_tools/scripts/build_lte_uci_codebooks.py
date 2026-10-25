"""Build standalone LTE UCI generator matrices from R2026a oracle samples."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_uci_codes.json"
target = ROOT / "tools" / "_lte_uci_codebooks.json"

records = json.loads(source.read_text(encoding="utf-8"))
books = {"lteUCI": {}, "lteUCI3": {}}
for record in records:
    basis = record["basis"]
    if record["n"] == 1:
        basis = [basis]
    books[record["entry"]][str(record["n"])] = basis
target.write_text(json.dumps(books, separators=(",", ":")) + "\n", encoding="utf-8")
print(target)
