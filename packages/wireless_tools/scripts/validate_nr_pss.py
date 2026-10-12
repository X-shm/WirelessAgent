"""Validate nr_pss against its deterministic MATLAB golden samples."""
from __future__ import annotations

import numpy as np

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


def main() -> int:
    samples = load_golden_samples("nr_pss.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_pss import pss, pss_indices

    checks = Checks()
    for case_name, case in samples.items():
        if case_name.startswith("ncellid"):
            expected = np.asarray(case["sym"], dtype=float)
            actual = pss(case["ncellid"])
            checks.check(
                f"PSS {case_name}",
                np.allclose(actual, expected, atol=1e-10),
                f"max_error={np.max(np.abs(actual - expected)):.2e}",
            )
        elif "indices" in case_name:
            base = "0based" if "0based" in case_name else "1based"
            actual = pss_indices(base)
            expected = np.asarray(case["indices"], dtype=int)
            checks.check(f"PSS {case_name}", np.array_equal(actual, expected))
    return checks.finish("PSS golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
