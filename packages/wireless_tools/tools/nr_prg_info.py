"""Independent NR precoding resource block group mapping."""
from __future__ import annotations

import argparse
import json
import math
import sys


def prg_info(n_size_grid: int, n_start_grid: int = 0, prg_size: int | None = None) -> dict:
    if not 1 <= n_size_grid <= 275 or n_start_grid < 0:
        raise ValueError("n_size_grid must be 1..275 and n_start_grid must be nonnegative")
    if prg_size is None:
        return {"NPRG": 1, "PRGSet": [1] * n_size_grid}
    if prg_size not in (2, 4):
        raise ValueError("prg_size must be 2, 4, or omitted for wideband")
    n_crb = n_start_grid + n_size_grid
    return {
        "NPRG": math.ceil(n_crb / prg_size),
        "PRGSet": [((n_start_grid + rb) // prg_size) + 1 for rb in range(n_size_grid)],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR PRG bundling information")
    parser.add_argument("--n_size_grid", type=int, required=True)
    parser.add_argument("--n_start_grid", type=int, default=0)
    parser.add_argument("--prg_size", type=int, choices=(2, 4), help="Omit for wideband")
    args = parser.parse_args()
    try:
        print(json.dumps(prg_info(args.n_size_grid, args.n_start_grid, args.prg_size)))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
