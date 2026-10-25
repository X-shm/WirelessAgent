"""LTE sidelink broadcast-channel RE positions including guard symbol."""
from __future__ import annotations

import numpy as np


_SYMBOLS = {
    ("D2D", "normal"): (0, 4, 5, 6, 7, 8, 9, 13),
    ("D2D", "extended"): (3, 4, 5, 6, 7, 11),
    ("V2X", "normal"): (0, 3, 5, 7, 8, 10, 13),
}


def psbch_indices(nrb=6, sidelink_mode="D2D", cyclic_prefix="Normal",
                   index_base=0):
    nrb = int(nrb)
    mode = str(sidelink_mode).upper()
    cp = str(cyclic_prefix).lower()
    if not 6 <= nrb <= 110 or (mode, cp) not in _SYMBOLS or index_base not in (0, 1):
        raise ValueError("invalid sidelink bandwidth, mode, prefix, or index base")
    start = (12*nrb-72)//2
    return np.asarray([[carrier+index_base, symbol+index_base, index_base]
                       for symbol in _SYMBOLS[(mode, cp)]
                       for carrier in range(start, start+72)], dtype=int)


def psbch_drs_indices(nrb=6, sidelink_mode="D2D", cyclic_prefix="Normal",
                       index_base=0):
    nrb = int(nrb)
    mode = str(sidelink_mode).upper()
    cp = str(cyclic_prefix).lower()
    if not 6 <= nrb <= 110 or (mode, cp) not in _SYMBOLS or index_base not in (0, 1):
        raise ValueError("invalid sidelink bandwidth, mode, prefix, or index base")
    symbols = ((4, 6, 9) if mode == "V2X" else
               (3, 10) if cp == "normal" else (2, 8))
    start = (12*nrb-72)//2
    return np.asarray([[carrier+index_base, symbol+index_base, index_base]
                       for symbol in symbols
                       for carrier in range(start, start+72)], dtype=int)
