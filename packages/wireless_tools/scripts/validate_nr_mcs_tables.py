"""Validate the implemented PDSCH MCS tables against MATLAB golden samples."""
from __future__ import annotations

from nr_sample_utils import Checks, add_tools_to_path, load_golden_samples


IMPLEMENTED_TABLES = (
    "QAM64Table",
    "QAM256Table",
    "QAM64LowSETable",
    "QAM1024Table",
)


def main() -> int:
    samples = load_golden_samples("nr_mcs_tables.json")
    if samples is None:
        return 77

    add_tools_to_path()
    from nr_mcs_tables import get_mcs_table

    checks = Checks()
    for table_name in IMPLEMENTED_TABLES:
        case = samples.get(table_name)
        if isinstance(case, list):
            case = case[0]
        if not isinstance(case, dict):
            checks.check(f"MCS {table_name} sample", False, "missing table")
            continue

        expected_rows = {
            index: (qm, rate)
            for index, qm, rate in zip(
                case["mcs_index"], case["qm"], case["target_code_rate"], strict=True
            )
            if index is not None
        }
        actual_rows = {row[0]: (row[2], row[3]) for row in get_mcs_table(table_name)}
        checks.check(
            f"MCS {table_name} row set",
            actual_rows.keys() == expected_rows.keys(),
            f"expected={len(expected_rows)} actual={len(actual_rows)}",
        )
        for index, (expected_qm, expected_rate) in expected_rows.items():
            actual_qm, actual_rate = actual_rows[index]
            checks.check(
                f"MCS {table_name}[{index}]",
                actual_qm == expected_qm and actual_rate == expected_rate,
                f"expected=(Qm={expected_qm}, R={expected_rate}) "
                f"actual=(Qm={actual_qm}, R={actual_rate})",
            )
    return checks.finish("MCS-table golden checks")


if __name__ == "__main__":
    raise SystemExit(main())
