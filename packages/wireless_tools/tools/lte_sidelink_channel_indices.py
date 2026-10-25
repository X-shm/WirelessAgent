"""LTE Sidelink PSCCH/PSSCH data and DRS resource positions."""
from __future__ import annotations

import numpy as np


_DRS_SYMBOLS = {
    ("D2D", "normal"): (3, 10),
    ("D2D", "extended"): (2, 8),
    ("V2X", "normal"): (2, 5, 8, 11),
}


def sidelink_channel_indices(channel, drs=False, nrb=6, prb_set=None,
                             sidelink_mode="D2D", cyclic_prefix="Normal",
                             modulation="QPSK", index_base=0):
    nrb = int(nrb)
    mode = str(sidelink_mode).upper()
    cp = str(cyclic_prefix).lower()
    if (channel not in ("PSCCH", "PSSCH") or not 6 <= nrb <= 110 or
            (mode, cp) not in _DRS_SYMBOLS or index_base not in (0, 1)):
        raise ValueError("invalid Sidelink channel or grid configuration")
    if prb_set is None:
        prb_set = [0, 1] if mode == "V2X" and channel == "PSCCH" else [0]
    raw = np.asarray(prb_set, dtype=int)
    if raw.ndim == 0:
        raw = raw.reshape(1)
    if raw.ndim == 1:
        slots = (raw.tolist(), raw.tolist())
    elif raw.ndim == 2 and raw.shape[1] == 2:
        slots = (raw[:, 0].tolist(), raw[:, 1].tolist())
    else:
        raise ValueError("prb_set must be a vector or two-column slot allocation")
    if any(not slot or len(set(slot)) != len(slot) or
           any(p < 0 or p >= nrb for p in slot) for slot in slots):
        raise ValueError("prb_set outside Sidelink carrier or contains duplicates")
    if channel == "PSCCH":
        target = 1 if mode == "D2D" else 2
        if any(len(slot) != target for slot in slots):
            raise ValueError("PSCCH needs one D2D or two V2X PRBs per slot")
    if str(modulation).upper() not in ("QPSK", "16QAM"):
        raise ValueError("Sidelink modulation must be QPSK or 16QAM")
    nsym = 14 if cp == "normal" else 12
    drs_symbols = set(_DRS_SYMBOLS[(mode, cp)])
    symbols = [s for s in range(nsym) if (s in drs_symbols) == bool(drs)]
    slot_length = nsym//2
    positions = np.asarray(
        [[12*p+k+index_base, s+index_base, index_base]
         for s in symbols for p in sorted(slots[s//slot_length]) for k in range(12)],
        dtype=int)
    gd = len(positions)
    qm = 2 if channel == "PSCCH" or str(modulation).upper() == "QPSK" else 4
    return positions, {"G": qm*gd, "Gd": gd}
