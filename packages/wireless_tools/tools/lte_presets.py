"""Offline LTE RMC and E-TM baseline configuration presets."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

_TABLE = json.loads(Path(__file__).with_name("_lte_presets.json").read_text(encoding="utf-8"))


def preset(entry: str, *, name=None, rc=None, tmn=None, bandwidth=None,
           bw=None, duplex_mode="FDD", total_subframes=10,
           tot_subframes=None, ncellid=None):
    if entry not in ("lteRMCDL", "lteRMCUL", "lteTestModel"):
        raise ValueError("unknown LTE preset family")
    default_name = {"lteRMCDL": "R.0", "lteRMCUL": "A1-1", "lteTestModel": "1.1"}[entry]
    selected_name = default_name if name is None and rc is None and tmn is None else (
        name if name is not None else rc if rc is not None else tmn)
    selected_bw = bandwidth if bandwidth is not None else bw
    if entry == "lteTestModel":
        selected_bw = "1.4MHz" if selected_bw is None else selected_bw
    elif selected_bw is not None:
        raise ValueError("bandwidth is only valid for lteTestModel")
    length = total_subframes if tot_subframes is None else tot_subframes
    if int(length) != 10:
        raise ValueError("LTE presets currently support TotSubframes=10")
    key = "|".join((entry, str(selected_name), str(duplex_mode).upper(),
                    "" if selected_bw is None else str(selected_bw)))
    if key not in _TABLE:
        raise ValueError("LTE preset name, bandwidth or duplex mode is outside the verified set")
    cfg = deepcopy(_TABLE[key])
    if ncellid is not None and int(ncellid) != cfg["NCellID"]:
        raise ValueError("test model supports only the standard default NCellID")
    return cfg
