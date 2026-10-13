"""Bit-error counting compatible with the common biterr modes."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


def _broadcast_pair(x, y):
    a = np.asarray(x, dtype=np.int64)
    b = np.asarray(y, dtype=np.int64)
    if np.any(a < 0) or np.any(b < 0) or a.size == 0 or b.size == 0:
        raise ValueError("x and y must contain nonnegative integers")
    if a.shape == b.shape:
        return a, b
    if a.ndim == 2 and b.ndim == 1:
        if b.size == a.shape[0]:
            b = b[:, None]
        elif b.size == a.shape[1]:
            b = b[None, :]
    elif b.ndim == 2 and a.ndim == 1:
        if a.size == b.shape[0]:
            a = a[:, None]
        elif a.size == b.shape[1]:
            a = a[None, :]
    try:
        return np.broadcast_arrays(a, b)
    except ValueError as exc:
        raise ValueError(f"incompatible shapes {a.shape} and {b.shape}") from exc


def bit_errors(x, y, k=None, mode="overall"):
    a, b = _broadcast_pair(x, y)
    maximum = int(max(np.max(a), np.max(b)))
    min_k = max(1, maximum.bit_length())
    k = min_k if k is None else int(k)
    if k < min_k:
        raise ValueError(f"k must be at least {min_k}")
    individual = np.vectorize(lambda value: int(value).bit_count(), otypes=[np.int64])(np.bitwise_xor(a, b))
    mode = mode.lower()
    if mode == "overall":
        num = int(individual.sum())
        ratio = num / (individual.size * k)
    elif mode == "column-wise":
        if individual.ndim != 2:
            raise ValueError("column-wise mode requires matrix-compatible inputs")
        num = individual.sum(axis=0)
        ratio = num / (individual.shape[0] * k)
    elif mode == "row-wise":
        if individual.ndim != 2:
            raise ValueError("row-wise mode requires matrix-compatible inputs")
        num = individual.sum(axis=1)
        ratio = num / (individual.shape[1] * k)
    else:
        raise ValueError("mode must be overall, column-wise, or row-wise")
    return num, ratio, individual, k


def _json_value(value):
    return value.tolist() if isinstance(value, np.ndarray) else value


def main():
    parser = argparse.ArgumentParser(description="Count bit errors")
    parser.add_argument("--x", required=True, help="JSON integer array")
    parser.add_argument("--y", required=True, help="JSON integer array")
    parser.add_argument("--k", type=int)
    parser.add_argument("--mode", choices=("overall", "column-wise", "row-wise"), default="overall")
    args = parser.parse_args()
    try:
        num, ratio, individual, k = bit_errors(json.loads(args.x), json.loads(args.y), args.k, args.mode)
        print(json.dumps({"num_errors": _json_value(num), "error_ratio": _json_value(ratio), "individual": individual.tolist(), "k": k}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
