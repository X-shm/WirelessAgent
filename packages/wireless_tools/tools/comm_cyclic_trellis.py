"""Binary cyclic-code, syndrome and trellis analysis slices."""
from __future__ import annotations

import itertools
import math

import numpy as np

from _nr_remaining_common import run_cli


def _binary_matrix(value, name):
    a = np.asarray(value, int)
    if a.ndim != 2 or not a.size or np.any((a != 0) & (a != 1)):
        raise ValueError(f"{name} must be a nonempty binary matrix")
    return a.astype(np.uint8)


def _poly(value):
    p = np.asarray(value, int).reshape(-1)
    if len(p) < 2 or p[0] != 1 or p[-1] != 1 or np.any((p != 0) & (p != 1)):
        raise ValueError("binary polynomial requires leading and constant coefficients")
    return p


def _remainder(dividend, divisor):
    work = np.asarray(dividend, np.uint8).copy()
    d = np.asarray(divisor, np.uint8)
    for i in range(len(work)-len(d)+1):
        if work[i]:
            work[i:i+len(d)] ^= d
    return work[-(len(d)-1):] if len(d) > 1 else np.array([], np.uint8)


def cyclpoly(n: int, k: int, option="first"):
    if not 1 <= k <= n <= 255 or n-k > 16:
        raise ValueError("supported n<=255 and degree n-k<=16")
    degree = n-k
    if degree == 0:
        return {"polynomials_ascending": [[1]]}
    candidates = []
    for middle in itertools.product((0, 1), repeat=degree-1):
        p = np.array([1, *middle, 1], np.uint8)
        if not np.any(_remainder([1]+[0]*(n-1)+[1], p)):
            candidates.append(p.tolist())
    if not candidates:
        raise ValueError("no cyclic generator polynomial for (n,k)")
    if option in ("first", "min"):
        selected = [min(candidates, key=lambda p: (sum(p), p))] if option == "min" else [candidates[0]]
    elif option == "max":
        selected = [max(candidates, key=lambda p: (sum(p), p))]
    elif option == "all":
        selected = candidates
    else:
        raise ValueError("option must be first/min/max/all")
    return {"polynomials_ascending": selected}


def cyclgen(n: int, p, option="system"):
    polynomial = _poly(p)
    m, k = len(polynomial)-1, n-len(polynomial)+1
    if n < 2 or k < 1 or np.any(_remainder([1]+[0]*(n-1)+[1], polynomial)):
        raise ValueError("p must divide x^n+1 with 0 < degree < n")
    if option == "system":
        parity = np.zeros((k, m), np.uint8)
        for i in range(k):
            # MATLAB's ascending polynomial order: remainder of x^(m+i).
            ascending = np.r_[np.zeros(m+i, np.uint8), 1]
            parity[i] = _remainder(ascending[::-1], polynomial[::-1])[::-1]
        generator = np.c_[parity, np.eye(k, dtype=np.uint8)]
        checks = np.c_[np.eye(m, dtype=np.uint8), parity.T]
    elif option == "nonsys":
        generator = np.zeros((k, n), np.uint8)
        for i in range(k):
            generator[i, i:i+m+1] = polynomial
        checks = _nullspace_checks(generator)
    else:
        raise ValueError("option must be system or nonsys")
    return {"parity_check": checks, "generator": generator, "message_length": k}


def _nullspace_checks(generator):
    a = generator.copy()
    k, n = a.shape
    pivots, row = [], 0
    for col in range(n):
        choices = np.flatnonzero(a[row:, col])
        if len(choices):
            pivot = row+choices[0]
            a[[row, pivot]] = a[[pivot, row]]
            for r in range(k):
                if r != row and a[r, col]:
                    a[r] ^= a[row]
            pivots.append(col)
            row += 1
            if row == k:
                break
    free = [j for j in range(n) if j not in pivots]
    checks = np.zeros((len(free), n), np.uint8)
    for i, col in enumerate(free):
        checks[i, col] = 1
        checks[i, pivots] = a[:, col]
    return checks


def gen2par(matrix):
    a = _binary_matrix(matrix, "matrix")
    rows, cols = a.shape
    if rows >= cols:
        raise ValueError("matrix needs fewer rows than columns")
    identity = np.eye(rows, dtype=np.uint8)
    if np.array_equal(a[:, :rows], identity):
        result = np.c_[a[:, rows:].T, np.eye(cols-rows, dtype=np.uint8)]
    elif np.array_equal(a[:, -rows:], identity):
        result = np.c_[np.eye(cols-rows, dtype=np.uint8), a[:, :cols-rows].T]
    else:
        raise ValueError("matrix must be systematic [I P] or [P I]")
    return {"matrix": result}


def syndtable(h):
    checks = _binary_matrix(h, "h")
    rows, cols = checks.shape
    if rows > 12 or cols > 32:
        raise ValueError("syndrome table limited to 12 checks and 32 bits")
    leaders = [None] * (1 << rows)
    for weight in range(cols+1):
        for positions in itertools.combinations(range(cols), weight):
            word = np.zeros(cols, np.uint8)
            word[list(positions)] = 1
            syndrome = (checks @ word) & 1
            index = sum(int(bit) << (rows-1-i) for i, bit in enumerate(syndrome))
            if leaders[index] is None:
                leaders[index] = word.tolist()
        if all(item is not None for item in leaders):
            break
    if any(item is None for item in leaders):
        raise ValueError("parity-check rows are linearly dependent")
    return {"coset_leaders": leaders}


def _trellis(t):
    if not isinstance(t, dict):
        raise ValueError("trellis must be an object")
    fields = ("numInputSymbols", "numOutputSymbols", "numStates", "nextStates", "outputs")
    if any(key not in t for key in fields):
        raise ValueError("trellis fields missing")
    ni, no, ns = (int(t[key]) for key in fields[:3])
    next_states = np.asarray(t["nextStates"], int)
    outputs = np.asarray(t["outputs"], int)
    if ni < 2 or no < 2 or ns < 1 or ni & (ni-1) or no & (no-1) or ns & (ns-1):
        raise ValueError("trellis dimensions must be powers of two")
    if next_states.shape != (ns, ni) or outputs.shape != (ns, ni) or np.any(next_states < 0) or np.any(next_states >= ns) or np.any(outputs < 0) or np.any(outputs >= no):
        raise ValueError("invalid transition or output matrices")
    return ni, no, ns, next_states, outputs


def istrellis(trellis):
    try:
        _trellis(trellis)
        return {"valid": True, "status": ""}
    except (ValueError, TypeError, KeyError) as exc:
        return {"valid": False, "status": str(exc)}


def iscatastrophic(trellis):
    ni, no, ns, states, outputs = _trellis(trellis)
    # Reachable zero-output cycle carrying nonzero input is catastrophic.
    reachable = {0}
    for _ in range(ns):
        reachable |= {int(states[s, u]) for s in tuple(reachable) for u in range(ni)}
    edges = {s: [(int(states[s, u]), u) for u in range(ni) if outputs[s, u] == 0]
             for s in reachable}
    for start in reachable:
        stack = [(start, False, {start})]
        while stack:
            state, nonzero, path = stack.pop()
            for target, symbol in edges[state]:
                flag = nonzero or symbol != 0
                if target == start and flag:
                    return {"catastrophic": True}
                if target not in path:
                    stack.append((target, flag, path | {target}))
    return {"catastrophic": False}


def distspec(trellis, n: int = 5, max_depth: int = 16):
    ni, no, ns, states, outputs = _trellis(trellis)
    if ni != 2 or n < 1 or max_depth < 1 or max_depth > 24:
        raise ValueError("binary input and 1<=max_depth<=24 required")
    events = {}
    stack = [(0, 0, 0, 0, 0)]  # state, depth, output weight, input weight, first input
    while stack:
        state, depth, distance, weight, first = stack.pop()
        if depth >= max_depth:
            continue
        for bit in range(ni):
            if depth == 0 and bit == 0:
                continue
            nxt = int(states[state, bit])
            d = distance + int(outputs[state, bit]).bit_count()
            w = weight + bit
            if nxt == 0:
                count, total = events.get(d, (0, 0))
                events[d] = (count+1, total+w)
            else:
                stack.append((nxt, depth+1, d, w, first))
    if not events:
        raise ValueError("no return-to-zero events found within max_depth")
    free = min(events)
    return {"dfree": free, "event": [events.get(d, (0, 0))[0] for d in range(free, free+n)],
            "weight": [events.get(d, (0, 0))[1] for d in range(free, free+n)],
            "max_depth": max_depth}


def _lfsr_masks(polynomial):
    p = _poly(polynomial)
    m = len(p)-1
    if m > 16:
        raise ValueError("LFSR degree limited to 16")
    state, masks = 1, []
    for _ in range((1 << m)-1):
        masks.append([(state >> (m-1-j)) & 1 for j in range(m)])
        feedback = (state >> (m-1)) & 1
        state = ((state << 1) & ((1 << m)-1))
        if feedback:
            state ^= sum(int(p[j]) << j for j in range(m))
    return masks


def shift2mask(prpoly, shift: int):
    masks = _lfsr_masks(prpoly)
    if int(shift) != shift:
        raise ValueError("shift must be integer")
    return {"mask": masks[shift % len(masks)]}


def mask2shift(prpoly, mask):
    masks = _lfsr_masks(prpoly)
    target = list(map(int, mask))
    if target not in masks:
        raise ValueError("mask does not occur in the LFSR period")
    return {"shift": masks.index(target)}


if __name__ == "__main__":
    run_cli("Binary cyclic and trellis analysis", {
        "cyclgen": cyclgen, "cyclpoly": cyclpoly, "gen2par": gen2par,
        "syndtable": syndtable, "istrellis": istrellis,
        "iscatastrophic": iscatastrophic, "distspec": distspec,
        "shift2mask": shift2mask, "mask2shift": mask2shift,
    })
