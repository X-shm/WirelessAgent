"""Selected PUSCH ACK, RI and CQI short-block coding and soft ML decoding."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_ul_control_codes.json").read_text(encoding="utf-8"))
_BPS = {"QPSK": 2, "16QAM": 4, "64QAM": 6}


def _entry(kind, length, qd, modulation):
    key = f"{kind},{length},{qd},{modulation}"
    if key not in _TABLE:
        raise ValueError("ACK/RI/CQI configuration is outside the verified length, Qd and modulation grid")
    return _TABLE[key]


def _message(bits):
    values = np.asarray(bits, dtype=int).reshape(-1)
    if not len(values) or np.any((values != 0) & (values != 1)):
        raise ValueError("control information must be a nonempty binary vector")
    return values


def encode(kind, bits, *, qd=None, modulation="QPSK"):
    values = _message(bits)
    modulation = str(modulation).upper()
    if modulation not in _BPS:
        raise ValueError("modulation must be QPSK, 16QAM or 64QAM")
    if qd is None:
        qd = 16 if kind == "lteCQI" else 4
    row = _entry(kind, len(values), int(qd), modulation)
    if kind == "lteCQI":
        basis = np.asarray(row["basis"], dtype=int)
        return (values @ basis) % 2
    index = int(sum(int(bit) << i for i, bit in enumerate(values)))
    return np.asarray(row["full"][index], dtype=int)


@lru_cache(maxsize=105)
def _codewords(kind, length, qd, modulation):
    row = _entry(kind, length, qd, modulation)
    values = np.arange(1 << length, dtype=np.uint32)
    messages = ((values[:, None] >> np.arange(length, dtype=np.uint32)) & 1).astype(int)
    if kind == "lteCQI":
        basis = np.asarray(row["basis"], dtype=int)
        coded = (messages @ basis) % 2
    else:
        coded = np.asarray(row["full"], dtype=int)
    return messages, coded


def decode(kind, soft_bits, length, *, qd=None, modulation="QPSK"):
    n = int(length)
    modulation = str(modulation).upper()
    if modulation not in _BPS:
        raise ValueError("modulation must be QPSK, 16QAM or 64QAM")
    if qd is None:
        qd = 16 if kind == "lteCQI" else 4
    qd = int(qd)
    received = np.asarray(soft_bits, dtype=float).reshape(-1)
    if len(received) != qd*_BPS[modulation] or not np.all(np.isfinite(received)):
        raise ValueError("soft input length must equal Qd times modulation order")
    if kind in ("lteACK", "lteRI") and n == 1 and np.any(
            (abs(received) > 0) & (abs(received) < .5)):
        raise ValueError("one-bit ACK/RI DTX thresholding is outside the verified soft-input subset")
    messages, codewords = _codewords(kind, n, qd, modulation)
    signs = np.where(codewords >= 0, 2*codewords-1, 0)
    metric = signs.astype(float) @ received
    return messages[int(np.argmax(metric))]
