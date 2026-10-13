"""Validate the implemented PDSCH DM-RS subset against MATLAB samples."""
from __future__ import annotations

import numpy as np

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


def main() -> int:
    samples = load_golden_samples("nr_dmrs.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_dmrs import dmrs_sequence, dmrs_subcarrier_locations

    checks = Checks()
    for case in samples:
        label = case["case_name"]
        actual = dmrs_sequence(
            case["ncellid"],
            case["nscid"],
            case["nslot"],
            case["nsym"],
            case["nprb"],
            case["config_type"],
            case["nsymbols"],
        )
        expected = np.asarray(case["sym_real"], dtype=float) + 1j * np.asarray(
            case["sym_imag"], dtype=float
        )
        checks.check(
            f"DM-RS {label} sequence",
            actual.shape == expected.shape and np.allclose(actual, expected, atol=1e-10),
            f"expected_len={len(expected)} actual_len={len(actual)}",
        )
        expected_locations = np.asarray(case["subcarrier_locations"], dtype=int)
        actual_locations = dmrs_subcarrier_locations(case["config_type"], port=0)
        checks.check(
            f"DM-RS {label} subcarrier locations",
            np.array_equal(actual_locations, expected_locations),
            f"expected={expected_locations.tolist()} actual={actual_locations.tolist()}",
        )
    return checks.finish("DM-RS golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
