"""Independent NR resource grid creation and resource extraction."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def resource_grid(nrb: int, ports: int = 1, cyclic_prefix: str = "normal") -> np.ndarray:
    if not 1 <= nrb <= 275 or not 1 <= ports <= 64:
        raise ValueError("nrb must be 1..275 and ports must be 1..64")
    if cyclic_prefix not in ("normal", "extended"):
        raise ValueError("cyclic_prefix must be normal or extended")
    symbols = 14 if cyclic_prefix == "normal" else 12
    return np.zeros((12 * nrb, symbols, ports), dtype=np.complex128)


def extract_resources(
    indices: np.ndarray,
    grid: np.ndarray,
    index_base: str = "1based",
    index_style: str = "index",
) -> tuple[np.ndarray, np.ndarray]:
    """Extract identical RE positions from every grid plane.

    This implements nrExtractResources' allplanes mode for linear indices or
    [subcarrier,symbol,antenna] subscripts. The antenna subscript is ignored in
    allplanes mode, as indices select RE positions shared by every plane.
    """
    data = np.asarray(grid, dtype=np.complex128)
    if data.ndim not in (2, 3, 4):
        raise ValueError("grid must have 2, 3 or 4 dimensions")
    k, l = data.shape[:2]
    offset = 1 if index_base == "1based" else 0
    if index_base not in ("0based", "1based"):
        raise ValueError("index_base must be 0based or 1based")
    raw = np.asarray(indices)
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise ValueError("indices must be integers")
    if index_style == "index":
        if raw.ndim != 1:
            raise ValueError("linear indices must be a one-dimensional array")
        linear_positions = raw.astype(np.int64) - offset
        if np.any(linear_positions < 0) or np.any(linear_positions >= data.size):
            raise ValueError("linear index outside the resource grid")
        positions = linear_positions % (k * l)
    elif index_style == "subscript":
        if data.ndim < 3 or raw.ndim != 2 or raw.shape[1] != 3:
            raise ValueError("subscripts require a 3-D/4-D grid and an N×3 array")
        positions = (raw[:, 0].astype(np.int64) - offset) + k * (raw[:, 1].astype(np.int64) - offset)
    else:
        raise ValueError("index_style must be index or subscript")
    if np.any(positions < 0) or np.any(positions >= k * l):
        raise ValueError("index outside the first grid plane")
    # MATLAB linear indices are column-major in each subcarrier×symbol plane.
    output = data[positions % k, positions // k, ...]
    plane_numbers = np.arange(np.prod(data.shape[2:], dtype=int), dtype=np.int64).reshape(data.shape[2:], order="F")
    addressed = positions.reshape((-1,) + (1,) * (data.ndim - 2)) + (k * l) * plane_numbers
    if index_style == "subscript":
        coordinates = np.unravel_index(addressed.reshape(-1, order="F"), data.shape, order="F")
        return output, np.column_stack(coordinates) + offset
    return output, addressed + offset


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR resource grid operations")
    parser.add_argument("--operation", choices=("create", "extract"), required=True)
    parser.add_argument("--nrb", type=int, help="Number of resource blocks for create")
    parser.add_argument("--ports", type=int, default=1)
    parser.add_argument("--cyclic_prefix", choices=("normal", "extended"), default="normal")
    parser.add_argument("--grid", help="Complex grid JSON {real,imag} for extract")
    parser.add_argument("--indices", help="JSON array of linear indices or subscripts")
    parser.add_argument("--index_base", choices=("0based", "1based"), default="1based")
    parser.add_argument("--index_style", choices=("index", "subscript"), default="index")
    args = parser.parse_args()
    try:
        if args.operation == "create":
            if args.nrb is None:
                raise ValueError("create requires --nrb")
            result = resource_grid(args.nrb, args.ports, args.cyclic_prefix)
            payload = {"grid": complex_json(result), "shape": list(result.shape)}
        else:
            if args.grid is None or args.indices is None:
                raise ValueError("extract requires --grid and --indices")
            result, used = extract_resources(
                np.asarray(json.loads(args.indices)), parse_complex(args.grid), args.index_base, args.index_style
            )
            payload = {"resources": complex_json(result), "indices": used.tolist(), "shape": list(result.shape)}
        print(json.dumps(payload))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
