"""Validate nr_tbs against its deterministic MATLAB golden samples."""
from __future__ import annotations

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


def main() -> int:
    samples = load_golden_samples("nr_tbs.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_tbs import tbs

    checks = Checks()
    for case_name, case in samples.items():
        actual = tbs(
            case["modulation"],
            case["nlayers"],
            case["nPRB"],
            case["NREPerPRB"],
            case["tcr"],
            case["xOh"],
            case["tbScaling"],
        )
        checks.check(
            f"TBS {case_name}",
            actual == case["tbs"],
            f"expected={case['tbs']} actual={actual}",
        )
    return checks.finish("TBS golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
