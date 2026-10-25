"""Create a portable initial-point descriptor; partial adapter for optimwarmstart."""
from __future__ import annotations

from optimization_common import run_cli, vector


def solve(problem, options=None):
    solver = problem.get("solver")
    if solver not in {"quadprog", "lsqlin"}:
        raise ValueError("optimwarmstart subset supports quadprog or lsqlin")
    opts = problem.get("options")
    if not isinstance(opts, dict) or opts.get("algorithm") != "active-set":
        raise ValueError("options.algorithm must be 'active-set'")
    x0 = vector(problem.get("x0"), "x0")
    return {
        "solver": solver,
        "x0": x0.tolist(),
        "options": opts,
        "active_set_reuse": False,
        "coverage": "initial-point descriptor only; MATLAB active-set history is not serialized or reused",
    }


if __name__ == "__main__":
    run_cli(solve)
