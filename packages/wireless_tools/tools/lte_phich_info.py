"""LTE FDD PHICH resource geometry, TS 36.211 section 6.9."""
from __future__ import annotations

import math


def phich_info(nrb=6, ng="One", cyclic_prefix="Normal",
               phich_duration="Normal", duplex_mode="FDD"):
    nrb = int(nrb)
    cp = str(cyclic_prefix).lower()
    duration = str(phich_duration).lower()
    mode = str(duplex_mode).upper()
    factors = {"sixth": 1/6, "half": 1/2, "one": 1, "two": 2}
    factor = factors.get(str(ng).lower())
    if not 6 <= nrb <= 110:
        raise ValueError("nrb must be 6..110")
    if factor is None or cp not in ("normal", "extended") or duration not in ("normal", "extended"):
        raise ValueError("invalid Ng, cyclic prefix, or PHICH duration")
    if mode != "FDD":
        raise ValueError("PHICH resource geometry currently supports FDD only")
    units = math.ceil(factor*nrb/8)
    groups = units*(2 if cp == "extended" else 1)
    sequences = 4 if cp == "extended" else 8
    return {"NREG": 3*units, "NRE": 12*units,
            "NPHICH": groups*sequences, "NGroups": groups,
            "NMappingUnits": units, "NSequences": sequences,
            "PHICHDuration": 3 if duration == "extended" else 1}
