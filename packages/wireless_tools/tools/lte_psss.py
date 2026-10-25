"""Primary LTE sidelink synchronization sequence and subframe positions."""
from __future__ import annotations

import numpy as np
import json
from pathlib import Path


_SSSS_BITS = np.asarray(json.loads(Path(__file__).with_name("_lte_ssss_binary.json")
                                  .read_text(encoding="utf-8")), dtype=np.uint8)
if _SSSS_BITS.shape != (2, 336, 62) or np.any(_SSSS_BITS > 1):
    raise RuntimeError("invalid LTE SSSS sequence table")


def ssss(nslid=0, sidelink_mode="D2D"):
    nslid = int(nslid)
    mode = str(sidelink_mode).upper()
    if not 0 <= nslid <= 335:
        raise ValueError("nslid must be 0..335")
    if mode not in ("D2D", "V2X"):
        raise ValueError("sidelink_mode must be D2D or V2X")
    values = 1 - 2*_SSSS_BITS[0 if mode == "D2D" else 1, nslid].astype(np.int8)
    return np.tile(values.astype(complex), 2)


def psss(nslid=0, nrb=6, cyclic_prefix="Normal", index_base=0):
    nslid, nrb = int(nslid), int(nrb)
    if not 0 <= nslid <= 335 or not 6 <= nrb <= 110:
        raise ValueError("nslid must be 0..335 and nrb 6..110")
    cp = str(cyclic_prefix).lower()
    if cp not in ("normal", "extended") or index_base not in (0, 1):
        raise ValueError("invalid cyclic prefix or index base")
    root = 26 if nslid < 168 else 37
    n = np.arange(62)
    m = np.where(n < 31, n, n+1)
    sequence = np.exp(-1j*np.pi*root*m*(m+1)/63)
    values = np.tile(sequence, 2)
    first = (12*nrb-62)//2
    symbols = (1, 2) if cp == "normal" else (0, 1)
    positions = np.asarray([[k+index_base, l+index_base, index_base]
                            for l in symbols for k in range(first, first+62)], dtype=int)
    return values, positions


def ssss_indices(nrb=6, cyclic_prefix="Normal", index_base=0):
    nrb = int(nrb)
    cp = str(cyclic_prefix).lower()
    if not 6 <= nrb <= 110 or cp not in ("normal", "extended") or index_base not in (0, 1):
        raise ValueError("invalid SSSS grid or index base")
    first = (12*nrb-62)//2
    symbols = (11, 12) if cp == "normal" else (9, 10)
    return np.asarray([[k+index_base, symbol+index_base, index_base]
                       for symbol in symbols for k in range(first, first+62)], dtype=int)
