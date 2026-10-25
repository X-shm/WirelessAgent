"""Viterbi equalization, trellis decode, and BCH product-code slices."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import complex_array, run_cli


def _binary(data):
    bits = np.asarray(data, int).reshape(-1)
    if not len(bits) or np.any((bits != 0) & (bits != 1)):
        raise ValueError("nonempty binary vector required")
    return bits


def _shape(n, k):
    nv, kv = np.asarray(n, int).reshape(-1), np.asarray(k, int).reshape(-1)
    if len(nv) != 2 or len(kv) != 2 or np.any(nv <= kv) or np.any(kv < 1):
        raise ValueError("n and k must contain two valid component dimensions")
    return nv, kv


def tpcenc(msg, n, k):
    from bch_code import encode
    nv, kv = _shape(n, k)
    bits = _binary(msg)
    if len(bits) != int(np.prod(kv)):
        raise ValueError("message length must equal product(k)")
    data = bits.reshape(tuple(kv), order="F")
    row_encoded = np.stack([encode(data[:, col], int(nv[0]), int(kv[0]))[0]
                            for col in range(kv[1])], axis=1)
    full = np.stack([encode(row_encoded[row], int(nv[1]), int(kv[1]))[0]
                     for row in range(nv[0])], axis=0)
    return {"codeword": full.reshape(-1, order="F"), "matrix": full}


def tpcdec(llr, n, k, iterations: int = 4):
    from bch_code import decode
    nv, kv = _shape(n, k)
    data = np.asarray(llr, float).reshape(-1)
    if len(data) != int(np.prod(nv)) or np.any(~np.isfinite(data)) or iterations < 1:
        raise ValueError("finite codeword LLR of length product(n) required")
    hard = (data < 0).astype(int).reshape(tuple(nv), order="F")
    for _ in range(iterations):
        for col in range(nv[1]):
            try:
                _, corrected, _, _ = decode(hard[:, col], int(nv[0]), int(kv[0]))
                hard[:, col] = corrected
            except ValueError:
                pass
        for row in range(nv[0]):
            try:
                _, corrected, _, _ = decode(hard[row], int(nv[1]), int(kv[1]))
                hard[row] = corrected
            except ValueError:
                pass
    return {"message": hard[:kv[0], :kv[1]].reshape(-1, order="F"),
            "corrected_codeword": hard.reshape(-1, order="F"),
            "iterations": iterations}


def mlseeq(x, chcffs, constellation, tblen: int = 5, opmode="rst", nsamp: int = 1):
    samples = complex_array(x).reshape(-1)
    channel = complex_array(chcffs).reshape(-1)
    symbols = complex_array(constellation).reshape(-1)
    if opmode != "rst" or nsamp != 1 or not 1 <= len(channel) <= 4 or not 2 <= len(symbols) <= 16 or tblen < 1:
        raise ValueError("supported MLSE slice: reset mode, one sample/symbol, channel length <=4, constellation <=16")
    if not len(samples) or np.any(~np.isfinite(samples)) or np.any(~np.isfinite(channel)) or np.any(~np.isfinite(symbols)):
        raise ValueError("finite nonempty samples, channel, constellation required")
    memory = len(channel)-1
    start = tuple([0]*memory)
    metrics = {start: 0.0}
    traces = []
    for received in samples:
        next_metrics, step = {}, {}
        for state, metric in metrics.items():
            for index, value in enumerate(symbols):
                predicted = channel[0]*value + sum(channel[t+1]*symbols[state[t]] for t in range(memory))
                next_state = (index, *state[:memory-1]) if memory else ()
                candidate = metric + abs(received-predicted)**2
                if candidate < next_metrics.get(next_state, float("inf")):
                    next_metrics[next_state] = candidate
                    step[next_state] = (state, index)
        metrics = next_metrics
        traces.append(step)
    state = min(metrics, key=metrics.get)
    decisions = []
    for step in reversed(traces):
        state, index = step[state]
        decisions.append(index)
    decisions.reverse()
    return {"symbols": symbols[decisions], "indices": decisions,
            "path_metric": min(metrics.values())}


def vitdeccore(code, trellis, tblen: int = 5, opmode="trunc", decision_type="hard"):
    if opmode not in ("trunc", "term") or decision_type != "hard" or tblen < 1:
        raise ValueError("supported Viterbi slice: hard-decision trunc/term mode")
    from comm_cyclic_trellis import _trellis
    ni, no, ns, transitions, outputs = _trellis(trellis)
    if ni != 2:
        raise ValueError("binary input trellis required")
    width = int(np.log2(no))
    bits = _binary(code)
    if len(bits) % width:
        raise ValueError("code length must be a multiple of trellis output width")
    received = bits.reshape(-1, width)
    metrics = np.full(ns, float("inf"))
    metrics[0] = 0
    previous = np.zeros((len(received), ns), int)
    selected = np.zeros((len(received), ns), int)
    for t, block in enumerate(received):
        nxt = np.full(ns, float("inf"))
        for state in range(ns):
            if not np.isfinite(metrics[state]):
                continue
            for bit in range(2):
                new_state = transitions[state, bit]
                out = int(outputs[state, bit])
                expected = [(out >> (width-1-j)) & 1 for j in range(width)]
                score = metrics[state] + np.count_nonzero(block != expected)
                if score < nxt[new_state]:
                    nxt[new_state] = score
                    previous[t, new_state] = state
                    selected[t, new_state] = bit
        metrics = nxt
    state = 0 if opmode == "term" else int(np.argmin(metrics))
    cost = metrics[state]
    decoded = np.zeros(len(received), np.uint8)
    for t in range(len(received)-1, -1, -1):
        decoded[t] = selected[t, state]
        state = previous[t, state]
    return {"decoded_bits": decoded, "path_metric": cost}


if __name__ == "__main__":
    run_cli("Sequence equalization and product-code slices", {
        "mlseeq": mlseeq, "tpcenc": tpcenc,
        "tpcdec": tpcdec, "vitdeccore": vitdeccore,
    })
