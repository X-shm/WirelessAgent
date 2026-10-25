"""Finite R2026a FDD PDCCH/PHICH RE allocations for standard baseline cells."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_POSITIONS = json.loads(Path(__file__).with_name("_lte_control_indices.json").read_text(encoding="utf-8"))


def control_indices(entry: str, *, nrb=6, ncellid=0, ports=1, cfi=2,
                    nsubframe=0, cyclic_prefix="Normal", duplex_mode="FDD",
                    phich_duration="Normal", ng="One", index_base=0):
    if entry not in ("ltePDCCHIndices", "ltePHICHIndices"):
        raise ValueError("unsupported control channel")
    if (int(nsubframe) != 0 or str(cyclic_prefix).lower() != "normal" or
            str(duplex_mode).upper() != "FDD" or
            str(phich_duration).lower() != "normal" or
            str(ng).lower() != "one"):
        raise ValueError("control RE allocation supports baseline FDD subframe 0, Normal CP/PHICH, Ng=One")
    if index_base not in (0, 1):
        raise ValueError("index_base must be 0 or 1")
    selected_cfi = 1 if entry == "ltePHICHIndices" else int(cfi)
    key = f"{entry},{int(nrb)},{int(ncellid)},{int(ports)},{selected_cfi}"
    if key not in _POSITIONS:
        raise ValueError("control RE allocation supports NRB 6/25/50/100, NCellID 0/37, ports 1/2/4, CFI 1..3")
    positions = np.asarray(_POSITIONS[key], dtype=int)
    return positions - (1-index_base)
