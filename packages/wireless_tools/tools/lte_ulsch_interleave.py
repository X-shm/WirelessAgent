"""Data-only LTE UL-SCH bit matrix interleaving and inverse."""
from __future__ import annotations

import numpy as np

_BITS = {"QPSK": 2, "16QAM": 4, "64QAM": 6, "256QAM": 8}


def ulsch_interleave(data, cyclic_prefix="Normal", shortened=0,
                     modulation="QPSK", n_layers=1, inverse=False):
    values = np.asarray(data).reshape(-1)
    cp = str(cyclic_prefix).lower()
    mod = str(modulation).upper()
    if cp not in ("normal", "extended") or mod not in _BITS:
        raise ValueError("invalid cyclic prefix or modulation")
    if int(n_layers) != 1 or int(shortened) not in (0, 1):
        raise ValueError("data-only interleaver supports one layer and shortened 0/1")
    columns = (12 if cp == "normal" else 10)-int(shortened)
    qm = _BITS[mod]
    if len(values) % (columns*qm):
        raise ValueError("data length must contain complete UL-SCH matrix rows")
    rows = len(values)//(columns*qm)
    if inverse:
        return values.reshape(columns, rows, qm).transpose(1, 0, 2).reshape(-1)
    return values.reshape(rows, columns, qm).transpose(1, 0, 2).reshape(-1)
