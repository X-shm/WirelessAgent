"""Single-port baseline EPDCCH data RE allocations and geometry."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_epdcch_indices.json").read_text(encoding="utf-8"))


def epdcch_indices(*, nrb=6, ncellid=0, nsubframe=0, prb_set=None,
                   cfi=2, epdcch_type="Localized", epdcch_ecce=0,
                   epdcch_nid=0, rnti=1, ports=1, cyclic_prefix="Normal",
                   duplex_mode="FDD", index_base=0):
    if (int(ports) != 1 or str(cyclic_prefix).lower() != "normal" or
            str(duplex_mode).upper() != "FDD" or int(epdcch_ecce) != 0 or
            int(epdcch_nid) != 0 or int(rnti) != 1 or index_base not in (0, 1)):
        raise ValueError("EPDCCH indexing supports baseline FDD, one CRS port, E-CCE 0, NID 0, RNTI 1")
    kind = str(epdcch_type).capitalize()
    if kind not in ("Localized", "Distributed"):
        raise ValueError("EPDCCHType must be Localized or Distributed")
    prbs = np.asarray([0] if prb_set is None else prb_set, dtype=int).reshape(-1).tolist()
    key = f"{int(nrb)},{int(ncellid)},{int(nsubframe)},{':'.join(map(str, prbs))},{int(cfi)},{kind}"
    if key not in _TABLE:
        raise ValueError("EPDCCH allocation is outside the verified parameter grid")
    row = _TABLE[key]
    return np.asarray(row["indices"], dtype=int) - (1-index_base), row["info"]
