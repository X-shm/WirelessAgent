"""Shared JSON and SciPy helpers for Optimization Toolbox adapters.

These adapters implement documented problem classes, not MATLAB's complete
API surface. They are intended for small, deterministic WirelessAgent tasks.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import numpy as np


def json_arg(value: str, name: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--{name} must contain valid JSON: {exc.msg}") from exc


def vector(value: Any, name: str, *, length: int | None = None) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    if arr.ndim != 1 or not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be a finite 1-D array")
    if length is not None and arr.size != length:
        raise ValueError(f"{name} must contain {length} values")
    return arr


def matrix(value: Any, name: str, *, cols: int | None = None) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.ndim == 0:
        arr = arr.reshape(1, 1)
    if arr.ndim != 2 or not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be a finite 2-D array")
    if cols is not None and arr.shape[1] != cols:
        raise ValueError(f"{name} must have {cols} columns")
    return arr


def bounds_arg(value: Any, n: int) -> list[tuple[float | None, float | None]]:
    if value is None:
        return [(None, None)] * n
    if not isinstance(value, list) or len(value) != n:
        raise ValueError("bounds must have one [lower, upper] pair per variable")
    result = []
    for i, pair in enumerate(value):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError(f"bounds[{i}] must be [lower, upper]")
        lo = None if pair[0] is None else float(pair[0])
        hi = None if pair[1] is None else float(pair[1])
        if lo is not None and hi is not None and lo > hi:
            raise ValueError(f"bounds[{i}] lower bound exceeds upper bound")
        result.append((lo, hi))
    return result


def lin_constraints(a_ub: Any, b_ub: Any, a_eq: Any, b_eq: Any, n: int):
    aub = bub = aeq = beq = None
    if a_ub is not None or b_ub is not None:
        if a_ub is None or b_ub is None:
            raise ValueError("A_ub and b_ub must be supplied together")
        aub = matrix(a_ub, "A_ub", cols=n)
        bub = vector(b_ub, "b_ub", length=aub.shape[0])
    if a_eq is not None or b_eq is not None:
        if a_eq is None or b_eq is None:
            raise ValueError("A_eq and b_eq must be supplied together")
        aeq = matrix(a_eq, "A_eq", cols=n)
        beq = vector(b_eq, "b_eq", length=aeq.shape[0])
    return aub, bub, aeq, beq


def options_arg(value: Any) -> dict[str, Any]:
    options = {} if value is None else value
    if not isinstance(options, dict):
        raise ValueError("options must be a JSON object")
    allowed = {"max_iterations", "tolerance", "display"}
    unknown = set(options) - allowed
    if unknown:
        raise ValueError(f"unsupported options: {', '.join(sorted(unknown))}")
    out = {
        "max_iterations": int(options.get("max_iterations", 1000)),
        "tolerance": float(options.get("tolerance", 1e-8)),
        "display": bool(options.get("display", False)),
    }
    if out["max_iterations"] < 1 or out["tolerance"] <= 0:
        raise ValueError("max_iterations and tolerance must be positive")
    return out


def solve_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", required=True, help="JSON object with the solver inputs")
    parser.add_argument("--options", required=False, help="JSON solver options")
    return parser


def run_cli(solver, parser: argparse.ArgumentParser | None = None) -> None:
    parser = parser or solve_args()
    args = parser.parse_args()
    try:
        problem = json_arg(args.problem, "problem")
        options = options_arg(None if args.options is None else json_arg(args.options, "options"))
        if not isinstance(problem, dict):
            raise ValueError("problem must be a JSON object")
        print(json.dumps(solver(problem, options), ensure_ascii=False, allow_nan=False))
    except (ValueError, TypeError, KeyError, ImportError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


def scipy_optimize():
    try:
        import scipy.optimize as optimize
    except ImportError as exc:
        raise ImportError("This tool requires SciPy; install it with `pip install scipy>=1.11`.") from exc
    return optimize


def result_json(result, x: np.ndarray, objective: float, method: str) -> dict[str, Any]:
    return {
        "x": [float(v) for v in x],
        "objective": float(objective),
        "success": bool(result.success),
        "status": int(result.status),
        "message": str(result.message),
        "iterations": int(getattr(result, "nit", 0)),
        "method": method,
    }


def optional_array(problem: dict, key: str, n: int, *, matrix_value=False):
    value = problem.get(key)
    if value is None:
        return None
    return matrix(value, key, cols=n) if matrix_value else vector(value, key)
