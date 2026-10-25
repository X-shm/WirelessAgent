"""NB-IoT NPUSCH demodulation-reference positions for FDD slots."""
from __future__ import annotations

import numpy as np


def npusch_drs_indices(spacing_khz=15, npusch_format="Data", subcarrier_set=None,
                       duplex_mode="FDD", index_base=0):
    spacing = float(spacing_khz)
    if spacing not in (3.75, 15.0):
        raise ValueError("spacing_khz must be 3.75 or 15")
    if str(duplex_mode).upper() != "FDD":
        raise ValueError("this subset supports FDD slots only")
    kind = str(npusch_format).lower()
    if kind not in ("data", "control"):
        raise ValueError("npusch_format must be Data or Control")
    if index_base not in (0, 1):
        raise ValueError("index_base must be 0 or 1")
    carriers = ([0] if subcarrier_set is None else
                list(np.asarray(subcarrier_set, dtype=int).reshape(-1)))
    if not carriers or len(set(carriers)) != len(carriers):
        raise ValueError("subcarrier_set must contain distinct carriers")
    upper = 48 if spacing == 3.75 else 12
    if any(not 0 <= k < upper for k in carriers):
        raise ValueError("subcarrier_set outside NB-IoT uplink grid")
    if kind == "control" or spacing == 3.75:
        if len(carriers) != 1:
            raise ValueError("Control and 3.75 kHz DRS require one carrier")
    elif len(carriers) not in (1, 3, 6, 12):
        raise ValueError("Data DRS carrier count must be 1, 3, 6, or 12")

    symbols = ([4] if kind == "data" and spacing == 3.75 else
               [3] if kind == "data" else
               [0, 1, 2] if spacing == 3.75 else [2, 3, 4])
    return np.asarray([[k+index_base, l+index_base, index_base]
                       for l in symbols for k in sorted(carriers)], dtype=int)
