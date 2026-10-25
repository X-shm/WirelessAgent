"""Create normalized common solver options; partial adapter for MATLAB optimoptions."""
from __future__ import annotations

from optimization_common import options_arg, run_cli

SOLVERS = {
    "fmincon", "linprog", "quadprog", "intlinprog", "fminimax", "fgoalattain"
}


def solve(problem, options=None):
    solver = problem.get("solver")
    if solver not in SOLVERS:
        raise ValueError(f"solver must be one of: {', '.join(sorted(SOLVERS))}")
    settings = problem.get("settings", options or {})
    if not isinstance(settings, dict):
        raise ValueError("settings must be a JSON object")
    allowed = {"algorithm", "max_iterations", "tolerance", "display"}
    unknown = set(settings) - allowed
    if unknown:
        raise ValueError(f"unsupported common settings: {', '.join(sorted(unknown))}")
    common = {key: settings[key] for key in ("max_iterations", "tolerance", "display") if key in settings}
    normalized = options_arg(common)
    if "algorithm" in settings:
        algorithm = settings["algorithm"]
        if not isinstance(algorithm, str) or not algorithm.strip():
            raise ValueError("algorithm must be a nonempty string")
        normalized["algorithm"] = algorithm
    return {"solver": solver, "options": normalized, "coverage": "common normalized settings only; not full MATLAB option parity"}


if __name__ == "__main__":
    run_cli(solve)
