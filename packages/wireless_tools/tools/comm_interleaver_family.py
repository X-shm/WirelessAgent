"""Standalone algebraic, helical, and shift-register interleavers."""
from __future__ import annotations

from collections import deque
import math
import numpy as np

from _nr_remaining_common import run_cli


def _data(values):
    x = np.asarray(values).reshape(-1)
    if not len(x):
        raise ValueError("data must be nonempty")
    return x


def _algebraic_table(num: int, kind: str, k=None, h: int = 0, alpha=None):
    if kind.lower() == "takeshita-costello":
        if num < 2 or num & (num - 1) or k is None or k < 1 or k >= num or k % 2 != 1 or not 0 <= h < num:
            raise ValueError("Takeshita-Costello requires power-of-two num, odd k<num and 0<=h<num")
        m = np.arange(num)
        c = (k * m * (m + 1) // 2) % num
        d = np.roll(c, -1)
        return np.roll(d[np.argsort(c, kind="stable")], -h).astype(int)
    if kind.lower() == "welch-costas":
        p = num + 1
        if p < 3 or any(p % d == 0 for d in range(2, math.isqrt(p) + 1)):
            raise ValueError("Welch-Costas requires prime num+1")
        if alpha is None or not 1 < alpha < p or len({pow(alpha, j, p) for j in range(num)}) != num:
            raise ValueError("alpha must be primitive modulo num+1")
        return np.asarray([pow(alpha, j, p) - 1 for j in range(num)], dtype=int)
    raise ValueError("kind must be takeshita-costello or welch-costas")


def algintrlv(data, num: int, kind: str, k=None, h: int = 0, alpha=None):
    x = _data(data)
    if len(x) != num:
        raise ValueError("num must equal data length")
    table = _algebraic_table(num, kind, k, h, alpha)
    return {"data": x[table], "permutation": table}


def algdeintrlv(data, num: int, kind: str, k=None, h: int = 0, alpha=None):
    x = _data(data)
    if len(x) != num:
        raise ValueError("num must equal data length")
    table = _algebraic_table(num, kind, k, h, alpha)
    return {"data": x[np.argsort(table)], "permutation": table}


def _mux(data, delay, state=None):
    x = _data(data)
    lengths = list(map(int, delay))
    if not lengths or min(lengths) < 0:
        raise ValueError("delay must contain nonnegative integers")
    if state is None:
        queues = [deque([0] * n) for n in lengths]
        index = 0
    else:
        queues = [deque(row) for row in state["queues"]]
        index = int(state["next_branch"])
        if len(queues) != len(lengths) or any(len(q) != n for q, n in zip(queues, lengths)):
            raise ValueError("state queues do not match delay")
    output = []
    for value in x:
        queue = queues[index]
        if queue:
            output.append(queue.popleft())
            queue.append(value.item() if hasattr(value, "item") else value)
        else:
            output.append(value.item() if hasattr(value, "item") else value)
        index = (index + 1) % len(queues)
    return {"data": output, "state": {"queues": [list(q) for q in queues],
                                      "next_branch": index}}


def muxintrlv(data, delay, state=None):
    return _mux(data, delay, state)


def muxdeintrlv(data, delay, state=None):
    lengths = list(map(int, delay))
    if not lengths or min(lengths) < 0:
        raise ValueError("delay must contain nonnegative integers")
    return _mux(data, [max(lengths) - d for d in lengths], state)


def convintrlv(data, nrows: int, slope: int, state=None):
    if nrows < 1 or slope < 0:
        raise ValueError("nrows positive and slope nonnegative required")
    return muxintrlv(data, [k * slope for k in range(nrows)], state)


def convdeintrlv(data, nrows: int, slope: int, state=None):
    if nrows < 1 or slope < 0:
        raise ValueError("nrows positive and slope nonnegative required")
    return muxdeintrlv(data, [k * slope for k in range(nrows)], state)


def _matrix_blocks(data, rows: int, columns: int, inverse=False):
    x = _data(data)
    size = rows * columns
    if rows < 1 or columns < 1 or len(x) % size:
        raise ValueError("data length must be a multiple of rows*columns")
    blocks = []
    for start in range(0, len(x), size):
        block = x[start:start + size]
        blocks.extend(block.reshape(columns, rows).T.reshape(-1) if inverse else
                      block.reshape(rows, columns).T.reshape(-1))
    return blocks


def helintrlv(data, columns: int, groups: int, step: int, state=None):
    if columns < 1 or groups < 1 or step < 1:
        raise ValueError("columns, groups and step must be positive")
    arranged = _matrix_blocks(data, columns, groups)
    return muxintrlv(arranged, [k * step for k in range(columns)], state)


def heldeintrlv(data, columns: int, groups: int, step: int, state=None):
    if columns < 1 or groups < 1 or step < 1:
        raise ValueError("columns, groups and step must be positive")
    restored = muxdeintrlv(data, [k * step for k in range(columns)], state)
    restored["data"] = _matrix_blocks(restored["data"], columns, groups, True)
    return restored


def _helical_table(rows: int, columns: int, step: int):
    if rows < 1 or columns < 1 or step < 0:
        raise ValueError("rows/columns positive and step nonnegative required")
    return np.asarray([((row + step * col) % rows) * columns + col
                       for row in range(rows) for col in range(columns)], int)


def helscanintrlv(data, rows: int, columns: int, step: int):
    x = _data(data)
    table = _helical_table(rows, columns, step)
    if len(x) != len(table):
        raise ValueError("data length must equal rows*columns")
    return {"data": x[table], "permutation": table}


def helscandeintrlv(data, rows: int, columns: int, step: int):
    x = _data(data)
    table = _helical_table(rows, columns, step)
    if len(x) != len(table):
        raise ValueError("data length must equal rows*columns")
    return {"data": x[np.argsort(table)], "permutation": table}


if __name__ == "__main__":
    run_cli("Standalone algebraic, helical and shift-register interleavers", {
        "algintrlv": algintrlv, "algdeintrlv": algdeintrlv,
        "convintrlv": convintrlv, "convdeintrlv": convdeintrlv,
        "muxintrlv": muxintrlv, "muxdeintrlv": muxdeintrlv,
        "helintrlv": helintrlv, "heldeintrlv": heldeintrlv,
        "helscanintrlv": helscanintrlv, "helscandeintrlv": helscandeintrlv,
    })
