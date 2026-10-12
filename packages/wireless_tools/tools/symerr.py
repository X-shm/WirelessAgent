"""Symbol-error counting compatible with the common symerr modes."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from biterr import _broadcast_pair


def symbol_errors(x, y, mode="overall"):
    a, b = _broadcast_pair(x, y)
    individual = (a != b).astype(np.int64)
    mode = mode.lower()
    if mode == "overall":
        num = int(individual.sum())
        ratio = num / individual.size
    elif mode == "column-wise":
        if individual.ndim != 2:
            raise ValueError("column-wise mode requires matrix-compatible inputs")
        num = individual.sum(axis=0)
        ratio = num / individual.shape[0]
    elif mode == "row-wise":
        if individual.ndim != 2:
            raise ValueError("row-wise mode requires matrix-compatible inputs")
        num = individual.sum(axis=1)
        ratio = num / individual.shape[1]
    else:
        raise ValueError("mode must be overall, column-wise, or row-wise")
    return num, ratio, individual


def _json_value(value):
    return value.tolist() if isinstance(value, np.ndarray) else value


def main():
    parser = argparse.ArgumentParser(description="Count symbol errors")
    parser.add_argument("--x", required=True, help="JSON integer array")
    parser.add_argument("--y", required=True, help="JSON integer array")
    parser.add_argument("--mode", choices=("overall", "column-wise", "row-wise"), default="overall")
    args = parser.parse_args()
    try:
        num, ratio, individual = symbol_errors(json.loads(args.x), json.loads(args.y), args.mode)
        print(json.dumps({"num_errors": _json_value(num), "error_ratio": _json_value(ratio), "individual": individual.tolist()}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
