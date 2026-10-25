"""Soft Viterbi decoder for LTE rate-1/3 tail-biting convolutional blocks."""
from __future__ import annotations

import numpy as np

from lte_convolutional_codec import _transition

_INCOMING = [[] for _ in range(64)]
for _state in range(64):
    for _bit in (0, 1):
        _next, _out = _transition(_state, _bit)
        _INCOMING[_next].append((_state, _bit, tuple(2*v-1 for v in _out)))
_SOURCE = np.asarray([[item[0] for item in row] for row in _INCOMING], dtype=int)
_BIT = np.asarray([[item[1] for item in row] for row in _INCOMING], dtype=np.int8)
_SIGN = np.asarray([[item[2] for item in row] for row in _INCOMING], dtype=float)


def decode_tailbiting(soft):
    data = np.asarray(soft, dtype=float).reshape(-1)
    if len(data) % 3 or len(data) < 18 or not np.all(np.isfinite(data)):
        raise ValueError("soft convolutional block must have three finite streams")
    length = len(data)//3
    observations = data.reshape(3, length).T
    best_metric = np.inf
    best_bits = None
    rows = np.arange(64)
    for initial in range(64):
        metrics = np.full(64, np.inf)
        metrics[initial] = 0
        previous = np.empty((length, 64), dtype=np.int8)
        decisions = np.empty((length, 64), dtype=np.int8)
        for t, observed in enumerate(observations):
            candidates = metrics[_SOURCE] - np.sum(_SIGN*observed, axis=2)
            branch = np.argmin(candidates, axis=1)
            metrics = candidates[rows, branch]
            previous[t] = _SOURCE[rows, branch]
            decisions[t] = _BIT[rows, branch]
        if metrics[initial] < best_metric:
            bits = np.empty(length, dtype=int)
            state = initial
            for t in range(length-1, -1, -1):
                bits[t] = decisions[t, state]
                state = int(previous[t, state])
            best_metric = metrics[initial]
            best_bits = bits
    return best_bits, float(best_metric)
