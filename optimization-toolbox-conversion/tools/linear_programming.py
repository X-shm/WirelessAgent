"""Linear programming adapter corresponding to MATLAB linprog."""
from __future__ import annotations
from optimization_common import bounds_arg, lin_constraints, options_arg, result_json, run_cli, scipy_optimize, vector


def solve(problem, options=None):
    options = options_arg(options)
    optimize = scipy_optimize()
    c = vector(problem["c"], "c")
    n = c.size
    aub, bub, aeq, beq = lin_constraints(problem.get("A_ub"), problem.get("b_ub"), problem.get("A_eq"), problem.get("b_eq"), n)
    res = optimize.linprog(c, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                           bounds=bounds_arg(problem.get("bounds"), n), method="highs",
                           options={"maxiter": options["max_iterations"], "dual_feasibility_tolerance": options["tolerance"], "primal_feasibility_tolerance": options["tolerance"], "disp": options["display"]})
    if res.x is None:
        return {"x": None, "objective": None, "success": bool(res.success), "status": int(res.status), "message": str(res.message), "iterations": int(getattr(res, "nit", 0)), "method": "HiGHS_linprog"}
    return result_json(res, res.x, float(res.fun), "HiGHS_linprog")


if __name__ == "__main__":
    run_cli(solve)
