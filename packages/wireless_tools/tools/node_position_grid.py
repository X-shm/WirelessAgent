"""Rectangular grid placement compatible with nodePositionGrid's main forms."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


def node_position_grid(boundary_dimension, center=(0, 0, 0), grid_size=(1, 1),
                       num_nodes_per_cell=1, placement_type="center", z_coordinate=0,
                       x_delta=None, y_delta=None, seed=None):
    length, width = map(float, boundary_dimension)
    cx, cy, _ = map(float, center)
    rows, cols = map(int, grid_size)
    count = int(num_nodes_per_cell)
    placement = placement_type.lower()
    if length <= 0 or width <= 0 or rows <= 0 or cols <= 0 or count <= 0:
        raise ValueError("dimensions, grid sizes, and node counts must be positive")
    if placement not in ("center", "bottom-left", "random"):
        raise ValueError("placement_type must be center, bottom-left, or random")
    if placement != "random" and count != 1:
        raise ValueError("num_nodes_per_cell must be 1 for non-random placement")
    rng = np.random.default_rng(seed)
    positions = []
    cells = []
    cell_length, cell_width = length / cols, width / rows
    left, top = cx - length / 2, cy + width / 2
    for col in range(cols):
        for row in range(rows):
            x0 = left + col * cell_length
            y1 = top - row * cell_width
            y0 = y1 - cell_width
            cells.append([[x0, y0], [x0 + cell_length, y0],
                          [x0 + cell_length, y1], [x0, y1]])
            for _index in range(count):
                if x_delta is not None or y_delta is not None:
                    dx = cell_length if x_delta is None else float(x_delta)
                    dy = cell_width if y_delta is None else float(y_delta)
                    x = cx - (cols - 1) * dx / 2 + col * dx
                    y = cy + (rows - 1) * dy / 2 - row * dy
                elif placement == "center":
                    x, y = x0 + cell_length / 2, y0 + cell_width / 2
                elif placement == "bottom-left":
                    x, y = x0, y0
                else:
                    x = x0 + rng.random() * cell_length
                    y = y0 + rng.random() * cell_width
                positions.append([round(x, 2), round(y, 2), float(z_coordinate)])
    return positions, cells


def _csv_numbers(text, cast=float):
    return [cast(value) for value in text.split(",")]


def main():
    parser = argparse.ArgumentParser(description="Generate rectangular grid node positions")
    parser.add_argument("--boundary_dimension", required=True, help="length,width")
    parser.add_argument("--center", default="0,0,0", help="x,y,z")
    parser.add_argument("--grid_size", default="1,1", help="rows,cols")
    parser.add_argument("--num_nodes_per_cell", type=int, default=1)
    parser.add_argument("--placement_type", choices=("center", "bottom-left", "random"), default="center")
    parser.add_argument("--z_coordinate", type=float, default=0)
    parser.add_argument("--x_delta", type=float)
    parser.add_argument("--y_delta", type=float)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    try:
        positions, cells = node_position_grid(
            _csv_numbers(args.boundary_dimension), _csv_numbers(args.center),
            _csv_numbers(args.grid_size, int), args.num_nodes_per_cell,
            args.placement_type, args.z_coordinate, args.x_delta, args.y_delta, args.seed)
        print(json.dumps({"positions": positions, "cell_polygons": cells}))
    except (ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
