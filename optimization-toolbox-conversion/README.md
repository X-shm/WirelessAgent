# Optimization Toolbox adapters — P0/P1 supported subsets

This is a separate add-on package for the existing `wireless-matlab-tools` collection. It adds eight tools corresponding to the P0/P1 MATLAB Optimization Toolbox functions discussed for WirelessAgent: six solver adapters plus `optimoptions` and `optimwarmstart` utilities.

## Priority mapping

- **P0:** `fmincon` subset → `constrained_nonlinear_optimize`; `linprog` → `linear_programming`.
- **P1:** `quadprog` → `quadratic_programming`; `intlinprog` → `mixed_integer_linear_programming`; `fminimax` → `minimax_optimization`; `fgoalattain` → `goal_attainment_optimization`.
- `optimoptions` → `create_optimization_options` normalizes common settings for the six converted solvers; it does not reproduce every MATLAB option or solver-specific setting.
- `optimwarmstart` → `create_optimization_warmstart` supports the documented `quadprog`/`lsqlin` active-set case as a portable initial-point descriptor. MATLAB's active-constraint history is not serialized or reused by this adapter.

## Coverage and limits

The Python implementations use SciPy. `fmincon` and `quadprog` are limited to quadratic objectives with linear constraints and bounds; `fminimax` and `fgoalattain` are limited to linear objective functions and linear constraints. They do not claim full MATLAB API parity. Each solver takes one `--problem` JSON object and optional `--options` JSON object. See the per-tool schema for exact keys.

Install dependencies with `python -m pip install -r requirements.txt`.

## MATLAB reference samples

`matlab_oracle/gen_samples_optimization_toolbox.m` generates one reference JSON file per tool using MATLAB R2026a Optimization Toolbox. To regenerate the samples, run the generator from MATLAB, then run:

```powershell
python scripts/check_schemas.py
python scripts/validate_optimization_adapters.py
```

The sample files are included in `matlab_oracle/samples`. Validation covers one reference problem per tool, within the documented subsets. It does not establish complete MATLAB API equivalence.
