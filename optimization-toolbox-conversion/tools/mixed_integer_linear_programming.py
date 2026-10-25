"""Mixed-integer linear programming adapter corresponding to MATLAB intlinprog."""
from __future__ import annotations
import numpy as np
from optimization_common import bounds_arg, lin_constraints, options_arg, result_json, run_cli, scipy_optimize, vector


def solve(problem, options=None):
    options = options_arg(options)
    optimize = scipy_optimize()
    from scipy.optimize import Bounds, LinearConstraint
    c = vector(problem["c"], "c")
    n = c.size
    integer = problem["integer_variables"]
    if not isinstance(integer, list) or any(not isinstance(i, int) or i < 0 or i >= n for i in integer):
        raise ValueError("integer_variables must be variable indices in [0,n)")
    integrality = np.zeros(n, dtype=int)
    integrality[integer] = 1
    aub, bub, aeq, beq = lin_constraints(problem.get("A_ub"), problem.get("b_ub"), problem.get("A_eq"), problem.get("b_eq"), n)
    rows, lower, upper = [], [], []
    if aub is not None:
        rows.append(aub); lower.extend([-np.inf] * len(bub)); upper.extend(bub.tolist())
    if aeq is not None:
        rows.append(aeq); lower.extend(beq.tolist()); upper.extend(beq.tolist())
    constraints = None if not rows else LinearConstraint(np.vstack(rows), np.asarray(lower), np.asarray(upper))
    bnd = bounds_arg(problem.get("bounds"), n)
    lb = np.asarray([-np.inf if a is None else a for a, _ in bnd])
    ub = np.asarray([np.inf if b is None else b for _, b in bnd])
    res = optimize.milp(c, integrality=integrality, bounds=Bounds(lb, ub), constraints=constraints,
                        options={"disp": options["display"], "node_limit": options["max_iterations"], "mip_rel_gap": options["tolerance"]})
    if res.x is None:
        return {"x": None, "objective": None, "success": bool(res.success), "status": int(res.status), "message": str(res.message), "iterations": int(getattr(res, "mip_node_count", 0) or 0), "method": "HiGHS_milp"}
    return result_json(res, res.x, float(res.fun), "HiGHS_milp")


if __name__ == "__main__":
    run_cli(solve)
