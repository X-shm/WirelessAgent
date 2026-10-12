"""Extract LTE resource elements using linear or subscript indices."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def extract_resources(grid, indices, index_format: str = "subscript", index_base: int = 0):
    array = np.asarray(grid, dtype=complex)
    idx = np.asarray(indices, dtype=int)
    if array.ndim not in (2, 3) or index_base not in (0, 1):
        raise ValueError("grid must be 2-D/3-D and index_base 0 or 1")
    zero = idx - index_base
    if index_format == "linear":
        zero = zero.reshape(-1)
        if np.any(zero < 0) or np.any(zero >= array.size):
            raise ValueError("linear index outside grid")
        values = array.reshape(-1, order="F")[zero]
        subscripts = np.column_stack(np.unravel_index(zero, array.shape, order="F"))
    elif index_format == "subscript":
        if zero.ndim != 2 or zero.shape[1] not in (2, 3) or zero.shape[1] != array.ndim:
            raise ValueError("subscript indices must have one column per grid dimension")
        if np.any(zero < 0) or any(np.any(zero[:, dim] >= array.shape[dim]) for dim in range(array.ndim)):
            raise ValueError("subscript index outside grid")
        subscripts = zero
        values = array[tuple(zero[:, dim] for dim in range(array.ndim))]
    else:
        raise ValueError("index_format must be linear or subscript")
    return values, subscripts + index_base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", required=True)
    parser.add_argument("--indices", required=True)
    parser.add_argument("--index_format", choices=["linear", "subscript"], default="subscript")
    parser.add_argument("--index_base", type=int, choices=[0, 1], default=0)
    args = parser.parse_args()
    try:
        values, subscripts = extract_resources(parse_complex(args.grid), json.loads(args.indices), args.index_format, args.index_base)
        print(json.dumps({"values": complex_json(values), "subscripts": subscripts.tolist(), "index_base": args.index_base}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
