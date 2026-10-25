"""Single-layer PDSCH and localized EPDCCH DM-RS verified configurations."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_dmrs.json").read_text(encoding="utf-8"))


def dmrs_reference(entry: str, *, nrb=6, ncellid=0, nsubframe=0,
                   prb_set=None, rnti=1, epdcch_nid=0,
                   epdcch_type="Localized", epdcch_ecce=0,
                   ports=1, n_layers=1, cyclic_prefix="Normal",
                   duplex_mode="FDD", index_base=0):
    signal = entry.removesuffix("Indices")
    if signal not in ("lteDMRS", "lteEPDCCHDMRS"):
        raise ValueError("unknown LTE DM-RS entry")
    if (int(ports) != 1 or int(n_layers) != 1 or
            str(cyclic_prefix).lower() != "normal" or
            str(duplex_mode).upper() != "FDD" or index_base not in (0, 1)):
        raise ValueError("DM-RS subset supports one layer/CRS port, FDD Normal CP")
    if signal == "lteEPDCCHDMRS" and (str(epdcch_type).lower() != "localized" or
                                        int(epdcch_ecce) != 0 or int(rnti) != 1):
        raise ValueError("EPDCCH DM-RS subset supports Localized E-CCE 0 and RNTI 1")
    prbs = np.asarray([0] if prb_set is None else prb_set, dtype=int).reshape(-1).tolist()
    identity = int(rnti if signal == "lteDMRS" else epdcch_nid)
    key = f"{signal},{int(nrb)},{int(ncellid)},{int(nsubframe)},{':'.join(map(str, prbs))},{identity}"
    if key not in _TABLE:
        raise ValueError("DM-RS configuration is outside the verified parameter grid")
    row = _TABLE[key]
    symbols = np.asarray(row["real"]) + 1j*np.asarray(row["imag"])
    positions = np.asarray(row["indices"], dtype=int) - (1-index_base)
    return symbols, positions
