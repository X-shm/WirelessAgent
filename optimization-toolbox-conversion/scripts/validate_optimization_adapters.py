"""Validate the supported Python subsets against MATLAB-generated samples."""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "tools"))
from constrained_nonlinear_optimize import solve as solve_fmincon
from linear_programming import solve as solve_linprog
from quadratic_programming import solve as solve_quadprog
from mixed_integer_linear_programming import solve as solve_intlinprog
from minimax_optimization import solve as solve_fminimax
from goal_attainment_optimization import solve as solve_fgoalattain
from create_optimization_options import solve as create_options
from create_optimization_warmstart import solve as create_warmstart

SOLVERS = {
    "constrained_nonlinear_optimize": solve_fmincon,
    "linear_programming": solve_linprog,
    "quadratic_programming": solve_quadprog,
    "mixed_integer_linear_programming": solve_intlinprog,
    "minimax_optimization": solve_fminimax,
    "goal_attainment_optimization": solve_fgoalattain,
    "create_optimization_options": create_options,
    "create_optimization_warmstart": create_warmstart,
}


def close(actual, expected, tol=1e-6):
    if actual is None or expected is None:
        return actual is expected
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(close(a, e, tol) for a, e in zip(actual, expected))
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        return isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=tol, abs_tol=tol)
    return actual == expected


def main():
    passed = 0
    for name, solver in SOLVERS.items():
        path = BASE / "matlab_oracle" / "samples" / f"{name}_samples.json"
        if not path.exists():
            print(f"FAIL {name}: missing MATLAB sample {path.name}")
            continue
        samples = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(samples, list) or not samples:
            print(f"FAIL {name}: sample file must contain a nonempty array")
            continue
        ok = True
        for sample in samples:
            result = solver(sample["problem"], sample.get("options"))
            expected = sample["expected"]
            for field, value in expected.items():
                if not close(result.get(field), value):
                    print(f"FAIL {name}: {field}: got {result.get(field)!r}, expected {value!r}")
                    ok = False
        if ok:
            passed += 1
            print(f"PASS {name}: {len(samples)} MATLAB sample(s)")
    print(f"{passed}/{len(SOLVERS)} tools passed")
    return 0 if passed == len(SOLVERS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
