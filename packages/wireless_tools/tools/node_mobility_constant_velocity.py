"""Stateless trajectory form of nodeMobilityConstantVelocity."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


def constant_velocity(initial_position, velocity, times):
    p0 = np.asarray(initial_position, dtype=float)
    vel = np.asarray(velocity, dtype=float)
    t = np.asarray(times, dtype=float)
    if p0.shape != (3,) or vel.shape != (3,) or t.ndim != 1:
        raise ValueError("initial_position and velocity need 3 values; times must be a vector")
    if np.any(~np.isfinite(t)) or np.any(t < 0):
        raise ValueError("times must be finite and nonnegative")
    return p0[None, :] + t[:, None] * vel[None, :]


def _csv(text):
    return [float(value) for value in text.split(",")]


def main():
    parser = argparse.ArgumentParser(description="Constant-velocity mobility trajectory")
    parser.add_argument("--initial_position", required=True, help="x,y,z")
    parser.add_argument("--velocity", required=True, help="vx,vy,vz")
    parser.add_argument("--times", required=True, help="comma-separated seconds")
    args = parser.parse_args()
    try:
        trajectory = constant_velocity(_csv(args.initial_position), _csv(args.velocity), _csv(args.times))
        print(json.dumps({"times": _csv(args.times), "positions": trajectory.tolist(),
                          "velocity": _csv(args.velocity)}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
