"""Linear-objective minimax adapter corresponding to MATLAB fminimax."""
from __future__ import annotations
import numpy as np
from optimization_common import bounds_arg, lin_constraints, options_arg, run_cli, scipy_optimize, vector, matrix


def solve(problem, options=None):
    options = options_arg(options)
    optimize = scipy_optimize()
    a_obj = matrix(problem["objective_matrix"], "objective_matrix")
    n = a_obj.shape[1]
    b_obj = vector(problem.get("objective_offset", np.zeros(a_obj.shape[0])), "objective_offset", length=a_obj.shape[0])
    aub, bub, aeq, beq = lin_constraints(problem.get("A_ub"), problem.get("b_ub"), problem.get("A_eq"), problem.get("b_eq"), n)
    aepi = np.c_[a_obj, -np.ones(a_obj.shape[0])]
    aub2 = np.c_[aub, np.zeros(aub.shape[0])] if aub is not None else None
    a_ub = aepi if aub2 is None else np.vstack([aepi, aub2])
    b_ub = -b_obj if bub is None else np.r_[-b_obj, bub]
    a_eq2 = np.c_[aeq, np.zeros(aeq.shape[0])] if aeq is not None else None
    bnds = bounds_arg(problem.get("bounds"), n) + [(None, None)]
    res = optimize.linprog(np.r_[np.zeros(n), 1.0], A_ub=a_ub, b_ub=b_ub,
                           A_eq=a_eq2, b_eq=beq, bounds=bnds, method="highs",
                           options={"maxiter": options["max_iterations"], "dual_feasibility_tolerance": options["tolerance"], "primal_feasibility_tolerance": options["tolerance"], "disp": options["display"]})
    if res.x is None:
        return {"x": None, "objective": None, "objective_values": None, "success": bool(res.success), "status": int(res.status), "message": str(res.message), "iterations": int(getattr(res, "nit", 0)), "method": "epigraph_LP_fminimax_subset"}
    vals = a_obj @ res.x[:n] + b_obj
    return {"x": res.x[:n].tolist(), "objective": float(np.max(vals)), "objective_values": vals.tolist(), "success": bool(res.success), "status": int(res.status), "message": str(res.message), "iterations": int(getattr(res, "nit", 0)), "method": "epigraph_LP_fminimax_subset"}


if __name__ == "__main__":
    run_cli(solve)
