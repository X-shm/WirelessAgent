"""Small quadratic-objective, linear-constraint subset of MATLAB fmincon."""
from __future__ import annotations
import numpy as np
from optimization_common import bounds_arg, lin_constraints, options_arg, result_json, run_cli, scipy_optimize, vector, matrix


def solve(problem, options=None):
    options = options_arg(options)
    optimize = scipy_optimize()
    h = matrix(problem["H"], "H")
    if h.shape[0] != h.shape[1] or not np.allclose(h, h.T, atol=1e-10):
        raise ValueError("H must be a square symmetric matrix")
    n = h.shape[0]
    f = vector(problem.get("f", np.zeros(n)), "f", length=n)
    x0 = vector(problem["x0"], "x0", length=n)
    aub, bub, aeq, beq = lin_constraints(problem.get("A_ub"), problem.get("b_ub"), problem.get("A_eq"), problem.get("b_eq"), n)
    constraints = []
    if aub is not None:
        constraints.append({"type": "ineq", "fun": lambda x: bub - aub @ x, "jac": lambda x: -aub})
    if aeq is not None:
        constraints.append({"type": "eq", "fun": lambda x: beq - aeq @ x, "jac": lambda x: -aeq})
    res = optimize.minimize(lambda x: 0.5 * x @ h @ x + f @ x, x0,
                            jac=lambda x: h @ x + f, method="SLSQP",
                            bounds=bounds_arg(problem.get("bounds"), n), constraints=constraints,
                            options={"maxiter": options["max_iterations"], "ftol": options["tolerance"], "disp": options["display"]})
    return result_json(res, res.x, 0.5 * res.x @ h @ res.x + f @ res.x, "SLSQP_quadratic_subset_of_fmincon")


if __name__ == "__main__":
    run_cli(solve)
