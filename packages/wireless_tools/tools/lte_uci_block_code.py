"""PUCCH format 2/3 UCI block codes, with exact short-block soft decoding."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_uci_codebooks.json").read_text(encoding="utf-8"))


def _basis(kind: str, length: int) -> np.ndarray:
    if kind not in _TABLE or str(length) not in _TABLE[kind]:
        raise ValueError(f"{kind} supports input lengths 1..{13 if kind == 'lteUCI' else 22}")
    return np.asarray(_TABLE[kind][str(length)], dtype=np.uint8)


def encode(kind: str, bits) -> np.ndarray:
    data = np.asarray(bits, dtype=int).reshape(-1)
    basis = _basis(kind, len(data))
    if np.any((data != 0) & (data != 1)):
        raise ValueError("UCI bits must be binary")
    return (data @ basis) % 2


@lru_cache(maxsize=22)
def _all_codewords(kind: str, length: int):
    basis = _basis(kind, length)
    values = np.arange(1 << length, dtype=np.uint32)
    messages = ((values[:, None] >> np.arange(length, dtype=np.uint32)) & 1).astype(np.uint8)
    codewords = (messages @ basis) % 2
    return messages, codewords


def decode(kind: str, soft_bits, length: int) -> np.ndarray:
    n = int(length)
    if not 1 <= n <= 11:
        raise ValueError("exact soft decoding currently supports 1..11 information bits")
    received = np.asarray(soft_bits, dtype=float).reshape(-1)
    expected = 20 if kind == "lteUCI" else 48
    if len(received) != expected or not np.all(np.isfinite(received)):
        raise ValueError(f"{kind} requires {expected} finite soft bits")
    messages, codewords = _all_codewords(kind, n)
    metric = (2*codewords.astype(np.float64)-1) @ received
    return messages[int(np.argmax(metric))].astype(int)
