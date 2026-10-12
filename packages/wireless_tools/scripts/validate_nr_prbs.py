"""Validate nr_prbs against its deterministic MATLAB golden samples."""
from __future__ import annotations

import sys

import numpy as np

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


def main() -> int:
    samples = load_golden_samples("nr_prbs.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_prbs import prbs

    checks = Checks()
    for case_name, case in samples.items():
        expected = np.asarray(case["seq"], dtype=np.int8)
        if "offset" in case:
            actual = prbs(case["cinit"], [case["offset"], case["n"]])
        else:
            actual = prbs(case["cinit"], case["n"])
        checks.check(
            f"PRBS {case_name}",
            np.array_equal(actual.astype(np.int8), expected),
            f"mismatches={np.count_nonzero(actual != expected)}",
        )
    return checks.finish("PRBS golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
