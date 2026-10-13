"""Random rectangle/circle placement compatible with nodePositionRandom."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


def node_position_random(boundary_shape, boundary_dimension, center=(0, 0, 0),
                         num_nodes=1, z_coordinate=0, seed=None):
    shape = boundary_shape.lower()
    cx, cy, _ = map(float, center)
    num_nodes = int(num_nodes)
    if shape not in ("rectangle", "circle") or num_nodes <= 0:
        raise ValueError("shape must be rectangle/circle and num_nodes must be positive")
    rng = np.random.default_rng(seed)
    if shape == "rectangle":
        length, width = map(float, boundary_dimension)
        if length <= 0 or width <= 0:
            raise ValueError("rectangle dimensions must be positive")
        x = cx + (rng.random(num_nodes) - 0.5) * length
        y = cy + (rng.random(num_nodes) - 0.5) * width
        polygon = [[cx - length / 2, cy - width / 2], [cx + length / 2, cy - width / 2],
                   [cx + length / 2, cy + width / 2], [cx - length / 2, cy + width / 2]]
    else:
        radius = float(boundary_dimension[0])
        if radius <= 0:
            raise ValueError("circle radius must be positive")
        radial = radius * np.sqrt(rng.random(num_nodes))
        theta = 2 * np.pi * rng.random(num_nodes)
        x, y = cx + radial * np.cos(theta), cy + radial * np.sin(theta)
        polygon = {"center": [cx, cy], "radius": radius}
    positions = np.column_stack([x, y, np.full(num_nodes, float(z_coordinate))])
    return np.round(positions, 2).tolist(), polygon


def main():
    parser = argparse.ArgumentParser(description="Generate random node positions")
    parser.add_argument("--boundary_shape", required=True, choices=("rectangle", "circle"))
    parser.add_argument("--boundary_dimension", required=True, help="length,width or radius")
    parser.add_argument("--center", default="0,0,0")
    parser.add_argument("--num_nodes", type=int, default=1)
    parser.add_argument("--z_coordinate", type=float, default=0)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    try:
        dimension = [float(value) for value in args.boundary_dimension.split(",")]
        center = [float(value) for value in args.center.split(",")]
        positions, polygon = node_position_random(args.boundary_shape, dimension, center,
                                                   args.num_nodes, args.z_coordinate, args.seed)
        print(json.dumps({"positions": positions, "boundary": polygon}))
    except (ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
