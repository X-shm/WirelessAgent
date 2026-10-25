"""Finite FDD single-antenna PUCCH 1/2/3 data and DRS RE allocations."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_pucch_indices.json").read_text(encoding="utf-8"))
_NAMES = frozenset(f"ltePUCCH{format}{drs}Indices"
                   for format in (1, 2, 3) for drs in ("", "DRS"))


def pucch_indices(entry: str, *, nrb=6, ncellid=0, nsubframe=0,
                  cyclic_prefix="Normal", resource_idx=0,
                  n_tx_ants=1, duplex_mode="FDD", index_base=0):
    if entry not in _NAMES:
        raise ValueError("unknown PUCCH resource entry")
    if (int(n_tx_ants) != 1 or str(duplex_mode).upper() != "FDD" or
            index_base not in (0, 1)):
        raise ValueError("PUCCH RE subset supports FDD and one transmit antenna")
    cp = "Extended" if str(cyclic_prefix).lower() == "extended" else "Normal"
    if str(cyclic_prefix).lower() not in ("normal", "extended"):
        raise ValueError("cyclic_prefix must be Normal or Extended")
    key = f"{entry},{int(nrb)},{int(ncellid)},{int(nsubframe)},{cp},{int(resource_idx)}"
    if key not in _TABLE:
        raise ValueError("PUCCH RE configuration is outside the verified parameter grid")
    return np.asarray(_TABLE[key], dtype=int) - (1-index_base)
