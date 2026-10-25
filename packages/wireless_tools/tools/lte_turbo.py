"""LTE 8-state PCCC encoder with TS 36.212 QPP interleaver and trellis tails."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_QPP = {int(k): tuple(v) for k, v in json.loads(
    Path(__file__).with_name("_lte_turbo_qpp.json").read_text(encoding="utf-8")).items()}


def qpp_indices(size: int) -> np.ndarray:
    if size not in _QPP:
        raise ValueError("input length must be a TS 36.212 legal Turbo block size (40..6144)")
    f1, f2 = _QPP[size]
    i = np.arange(size, dtype=np.int64)
    positions = (f1*i + f2*i*i) % size
    if len(np.unique(positions)) != size:
        raise RuntimeError("QPP coefficients do not form a permutation")
    return positions


def _constituent(data: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # g0(D)=1+D^2+D^3 (feedback), g1(D)=1+D+D^3 (parity).
    previous_1 = previous_2 = previous_3 = 0
    parity = np.empty(len(data), dtype=np.int8)
    for index, value in enumerate(data):
        feedback = int(value) ^ previous_2 ^ previous_3
        parity[index] = feedback ^ previous_1 ^ previous_3
        previous_1, previous_2, previous_3 = feedback, previous_1, previous_2
    tail_systematic = np.empty(3, dtype=np.int8)
    tail_parity = np.empty(3, dtype=np.int8)
    for index in range(3):
        terminal_input = previous_2 ^ previous_3
        feedback = terminal_input ^ previous_2 ^ previous_3
        tail_systematic[index] = terminal_input
        tail_parity[index] = feedback ^ previous_1 ^ previous_3
        previous_1, previous_2, previous_3 = feedback, previous_1, previous_2
    assert (previous_1, previous_2, previous_3) == (0, 0, 0)
    return parity, tail_systematic, tail_parity


def turbo_encode(bits) -> np.ndarray:
    raw = np.asarray(bits, dtype=np.int64).reshape(-1)
    size = len(raw)
    permutation = qpp_indices(size)
    if np.any(raw > 1):
        raise ValueError("Turbo input must contain binary bits or negative filler markers")
    data = np.where(raw < 0, 0, raw).astype(np.int8)
    first_parity, first_systematic_tail, first_parity_tail = _constituent(data)
    second_parity, second_systematic_tail, second_parity_tail = _constituent(data[permutation])
    streams = np.empty((3, size+4), dtype=np.int8)
    streams[0, :size] = data
    streams[1, :size] = first_parity
    streams[2, :size] = second_parity
    filler = raw < 0
    streams[0, :size][filler] = -1
    streams[1, :size][filler] = -1

    # TS 36.212 section 5.1.3.2.2 distributes 12 termination bits over
    # the four final positions of the three output streams.
    x, z = first_systematic_tail, first_parity_tail
    xp, zp = second_systematic_tail, second_parity_tail
    streams[:, size] = (x[0], z[0], x[1])
    streams[:, size+1] = (z[1], x[2], z[2])
    streams[:, size+2] = (xp[0], zp[0], xp[1])
    streams[:, size+3] = (zp[1], xp[2], zp[2])
    return streams.reshape(-1)


_STATES = np.arange(8, dtype=int)
_NEXT = np.empty((8, 2), dtype=int)
_PARITY = np.empty((8, 2), dtype=int)
for _state in range(8):
    _s1, _s2, _s3 = (_state >> 2) & 1, (_state >> 1) & 1, _state & 1
    for _input in (0, 1):
        _feedback = _input ^ _s2 ^ _s3
        _NEXT[_state, _input] = (_feedback << 2) | (_s1 << 1) | _s2
        _PARITY[_state, _input] = _feedback ^ _s1 ^ _s3


def _max_log_map(systematic, parity, a_priori):
    count = len(systematic)
    alpha = np.full((count+1, 8), -np.inf)
    beta = np.full((count+1, 8), -np.inf)
    alpha[0, 0] = 0.
    beta[count, 0] = 0.
    input_sign = np.array([1., -1.])
    parity_sign = 1. - 2.*_PARITY
    for time in range(count):
        branch = .5*((systematic[time]+a_priori[time])*input_sign[None, :] +
                     parity[time]*parity_sign)
        np.maximum.at(alpha[time+1], _NEXT.ravel(), (alpha[time, :, None]+branch).ravel())
        alpha[time+1] -= np.max(alpha[time+1])
    for time in range(count-1, -1, -1):
        branch = .5*((systematic[time]+a_priori[time])*input_sign[None, :] +
                     parity[time]*parity_sign)
        beta[time] = np.max(branch + beta[time+1, _NEXT], axis=1)
        beta[time] -= np.max(beta[time])
    posterior = np.empty(count)
    for time in range(count):
        branch = .5*((systematic[time]+a_priori[time])*input_sign[None, :] +
                     parity[time]*parity_sign)
        metric = alpha[time, :, None] + branch + beta[time+1, _NEXT]
        posterior[time] = np.max(metric[:, 0]) - np.max(metric[:, 1])
    return posterior


def turbo_decode(soft_bits, iterations=5) -> np.ndarray:
    soft = np.asarray(soft_bits, dtype=float).reshape(-1)
    if len(soft) % 3:
        raise ValueError("Turbo decoder expects three equal coded streams")
    size = len(soft)//3 - 4
    permutation = qpp_indices(size)
    if not np.all(np.isfinite(soft)) or not 1 <= int(iterations) <= 30:
        raise ValueError("finite soft bits and iterations 1..30 required")
    # MATLAB's Soft demapper uses positive values for bit 1; the
    # Max-Log-MAP implementation below uses log(P(0)/P(1)).
    d0, d1, d2 = -soft.reshape(3, size+4)
    upper_systematic = np.concatenate((d0[:size], [d0[size], d2[size], d1[size+1]]))
    upper_parity = np.concatenate((d1[:size], [d1[size], d0[size+1], d2[size+1]]))
    lower_systematic = np.concatenate((d0[:size][permutation],
                                       [d0[size+2], d2[size+2], d1[size+3]]))
    lower_parity = np.concatenate((d2[:size], [d1[size+2], d0[size+3], d2[size+3]]))
    a_priori = np.zeros(size)
    inverse = np.argsort(permutation)
    for _ in range(int(iterations)):
        upper_posterior = _max_log_map(
            upper_systematic, upper_parity, np.pad(a_priori, (0, 3)))
        upper_extrinsic = upper_posterior[:size] - upper_systematic[:size] - a_priori
        lower_a_priori = upper_extrinsic[permutation]
        lower_posterior = _max_log_map(
            lower_systematic, lower_parity, np.pad(lower_a_priori, (0, 3)))
        lower_extrinsic = lower_posterior[:size] - lower_systematic[:size] - lower_a_priori
        a_priori = lower_extrinsic[inverse]
    return (lower_posterior[:size][inverse] < 0).astype(np.int8)
