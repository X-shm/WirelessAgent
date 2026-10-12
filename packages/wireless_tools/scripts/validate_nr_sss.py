"""Validate nr_sss against its deterministic MATLAB golden samples."""
from __future__ import annotations

import numpy as np

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


def main() -> int:
    samples = load_golden_samples("nr_sss.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_sss import sss, sss_indices

    checks = Checks()
    for case_name, case in samples.items():
        if case_name.startswith("ncellid"):
            expected = np.asarray(case["sym"], dtype=float)
            actual = sss(case["ncellid"])
            checks.check(
                f"SSS {case_name}",
                np.allclose(actual, expected, atol=1e-10),
                f"max_error={np.max(np.abs(actual - expected)):.2e}",
            )
        elif "indices" in case_name:
            expected = np.asarray(case["indices"], dtype=int)
            checks.check("SSS 1based indices", np.array_equal(sss_indices("1based"), expected))
    return checks.finish("SSS golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
