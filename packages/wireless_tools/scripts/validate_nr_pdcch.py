"""Validate the PDCCH scrambling-plus-QPSK subset against MATLAB samples."""
from __future__ import annotations

import numpy as np

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


def main() -> int:
    samples = load_golden_samples("nr_pdcch.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_pdcch import pdcch

    checks = Checks()
    for case in samples:
        label = case["case_name"]
        actual = pdcch(
            np.asarray(case["codeword"], dtype=np.int8), case["n_id"], case["n_rnti"]
        )
        expected = np.asarray(case["sym_real"], dtype=float) + 1j * np.asarray(
            case["sym_imag"], dtype=float
        )
        checks.check(
            f"PDCCH {label}",
            actual.shape == expected.shape and np.allclose(actual, expected, atol=1e-10),
            f"expected_len={len(expected)} actual_len={len(actual)}",
        )
    return checks.finish("PDCCH golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
