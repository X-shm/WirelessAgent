"""LTE PDCCH REG interleaving and inverse, TS 36.211 section 6.8.5."""
from __future__ import annotations

import numpy as np

_COLUMNS = np.asarray([0,16,8,24,4,20,12,28,2,18,10,26,6,22,14,30,
                       1,17,9,25,5,21,13,29,3,19,11,27,7,23,15,31])


def pdcch_interleave(values, ncellid=0, inverse=False):
    data = np.asarray(values)
    cellid = int(ncellid)
    if data.ndim not in (1, 2) or data.shape[0] == 0 or data.shape[0] % 4:
        raise ValueError("PDCCH data must have a nonempty multiple of four rows")
    if not 0 <= cellid <= 503:
        raise ValueError("ncellid must be 0..503")
    reg = data.shape[0]//4
    rows = (reg+31)//32
    slots = np.pad(np.arange(reg), (rows*32-reg, 0), constant_values=-1)
    perm = slots.reshape(rows, 32)[:, _COLUMNS].T.reshape(-1)
    perm = np.roll(perm[perm >= 0], -(reg//2+cellid) % reg)
    positions = (4*perm[:, None]+np.arange(4)).reshape(-1)
    if inverse:
        output = np.empty_like(data)
        output[positions] = data
        return output
    return data[positions]
