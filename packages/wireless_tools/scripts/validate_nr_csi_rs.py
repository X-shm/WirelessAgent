"""Validate the implemented single-port CSI-RS subset against MATLAB samples."""
from __future__ import annotations

import numpy as np

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


def main() -> int:
    samples = load_golden_samples("nr_csi_rs.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_csi_rs import csi_rs_rb_indices, csi_rs_sequence

    checks = Checks()
    for case in samples:
        label = case["case_name"]
        actual = csi_rs_sequence(
            case["nid"],
            case["nslot"],
            case["nsym"],
            case["nprb"],
            case["density"],
        )
        expected = np.asarray(case["sym_real"], dtype=float) + 1j * np.asarray(
            case["sym_imag"], dtype=float
        )
        checks.check(
            f"CSI-RS {label} sequence",
            actual.shape == expected.shape and np.allclose(actual, expected, atol=1e-10),
            f"expected_len={len(expected)} actual_len={len(actual)}",
        )
        expected_rbs = np.asarray(case["rb_indices"], dtype=int)
        actual_rbs = csi_rs_rb_indices(case["nprb"], case["density"])
        checks.check(
            f"CSI-RS {label} continuous RB mapping",
            np.array_equal(actual_rbs, expected_rbs),
            f"expected={expected_rbs.tolist()} actual={actual_rbs.tolist()}",
        )
    return checks.finish("CSI-RS golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
