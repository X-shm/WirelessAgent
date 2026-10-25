"""Build standalone LTE sidelink DRS values for verified configurations."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "matlab_oracle" / "samples" / "lte_sidelink_drs.json"
target = ROOT / "tools" / "_lte_sidelink_drs.json"


def key(entry, cfg):
    if entry == "ltePSBCHDRS":
        return f"{entry}|{cfg['NSLID']}"
    prb = cfg["PRBSet"]
    if isinstance(prb, int):
        prb = [prb]
    return "|".join(map(str, [entry, cfg.get("SidelinkMode", "D2D"),
                               cfg.get("CyclicPrefixSL", "Normal"), cfg["NSLRB"],
                               ",".join(map(str, prb)), cfg.get("NSAID", 0),
                               cfg.get("NXID", 0), cfg.get("NSubframePSSCH", 0)]))


table = {}
for record in json.loads(source.read_text(encoding="utf-8")):
    table[key(record["entry"], record["config"])] = {
        "real": record["real"], "imag": record["imag"], "info": record["info"]}
target.write_text(json.dumps(table, separators=(",", ":")) + "\n", encoding="utf-8")
print(target, len(table))
