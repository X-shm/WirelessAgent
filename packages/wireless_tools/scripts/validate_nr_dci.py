"""Validate DCI encoding and PDCCH scrambling against MATLAB samples."""
from __future__ import annotations

import numpy as np

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


def main() -> int:
    samples = load_golden_samples("nr_dci.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_dci import dci_encode, dci_scramble

    checks = Checks()
    for case in samples:
        label = case["case_name"]
        bits = np.asarray(case["dci_bits"], dtype=np.int8)
        expected_codeword = np.asarray(case["codeword"], dtype=np.int8)
        actual_codeword = dci_encode(bits, case["rnti"], case["edci"])
        checks.check(
            f"DCI {label} encode",
            np.array_equal(actual_codeword, expected_codeword),
            f"expected_len={len(expected_codeword)} actual_len={len(actual_codeword)}",
        )

        expected_scrambled = np.asarray(case["scrambled_codeword"], dtype=np.int8)
        actual_scrambled = dci_scramble(expected_codeword, case["n_id"], case["rnti"])
        checks.check(
            f"DCI {label} scramble",
            np.array_equal(actual_scrambled, expected_scrambled),
            f"expected_len={len(expected_scrambled)} actual_len={len(actual_scrambled)}",
        )
    return checks.finish("DCI golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
