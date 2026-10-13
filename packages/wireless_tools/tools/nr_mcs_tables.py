"""nr_mcs_tables - 5G NR MCS and CQI lookup tables.

Implements TS 38.214 Tables 5.1.3.1-1..4 (PDSCH MCS).
MATLAB equivalent: nrPDSCHMCSTables
"""
from __future__ import annotations
import argparse
import json
import sys

# Table format: [MCS, Modulation, Qm, TargetCodeRate(float), SpectralEfficiency]
# TCR values extracted from MATLAB nrPDSCHMCSTables golden samples

# ── PDSCH MCS Table 5.1.3.1-1 (64QAM Table) ──
PDSCH_MCS_TABLE_1 = [
    [ 0, "QPSK", 2, 0.1171875, 0.2344],
    [ 1, "QPSK", 2, 0.1533203125, 0.3066],
    [ 2, "QPSK", 2, 0.1884765625, 0.377],
    [ 3, "QPSK", 2, 0.2451171875, 0.4902],
    [ 4, "QPSK", 2, 0.30078125, 0.6016],
    [ 5, "QPSK", 2, 0.3701171875, 0.7402],
    [ 6, "QPSK", 2, 0.4384765625, 0.877],
    [ 7, "QPSK", 2, 0.513671875, 1.0273],
    [ 8, "QPSK", 2, 0.587890625, 1.1758],
    [ 9, "QPSK", 2, 0.6630859375, 1.3262],
    [10, "16QAM", 4, 0.33203125, 1.3281],
    [11, "16QAM", 4, 0.369140625, 1.4766],
    [12, "16QAM", 4, 0.423828125, 1.6953],
    [13, "16QAM", 4, 0.478515625, 1.9141],
    [14, "16QAM", 4, 0.5400390625, 2.1602],
    [15, "16QAM", 4, 0.6015625, 2.4063],
    [16, "16QAM", 4, 0.642578125, 2.5703],
    [17, "64QAM", 6, 0.427734375, 2.5664],
    [18, "64QAM", 6, 0.455078125, 2.7305],
    [19, "64QAM", 6, 0.5048828125, 3.0293],
    [20, "64QAM", 6, 0.5537109375, 3.3223],
    [21, "64QAM", 6, 0.6015625, 3.6094],
    [22, "64QAM", 6, 0.650390625, 3.9023],
    [23, "64QAM", 6, 0.7021484375, 4.2129],
    [24, "64QAM", 6, 0.75390625, 4.5234],
    [25, "64QAM", 6, 0.802734375, 4.8164],
    [26, "64QAM", 6, 0.8525390625, 5.1152],
    [27, "64QAM", 6, 0.888671875, 5.332],
    [28, "64QAM", 6, 0.92578125, 5.5547],
    [29, "QPSK", 2, None, None],
    [30, "16QAM", 4, None, None],
    [31, "64QAM", 6, None, None],
]

# ── PDSCH MCS Table 5.1.3.1-2 (256QAM Table) ──
PDSCH_MCS_TABLE_2 = [
    [ 0, "QPSK", 2, 0.1171875, 0.2344],
    [ 1, "QPSK", 2, 0.1884765625, 0.377],
    [ 2, "QPSK", 2, 0.30078125, 0.6016],
    [ 3, "QPSK", 2, 0.4384765625, 0.877],
    [ 4, "QPSK", 2, 0.587890625, 1.1758],
    [ 5, "16QAM", 4, 0.369140625, 1.4766],
    [ 6, "16QAM", 4, 0.423828125, 1.6953],
    [ 7, "16QAM", 4, 0.478515625, 1.9141],
    [ 8, "16QAM", 4, 0.5400390625, 2.1602],
    [ 9, "16QAM", 4, 0.6015625, 2.4063],
    [10, "16QAM", 4, 0.642578125, 2.5703],
    [11, "64QAM", 6, 0.455078125, 2.7305],
    [12, "64QAM", 6, 0.5048828125, 3.0293],
    [13, "64QAM", 6, 0.5537109375, 3.3223],
    [14, "64QAM", 6, 0.6015625, 3.6094],
    [15, "64QAM", 6, 0.650390625, 3.9023],
    [16, "64QAM", 6, 0.7021484375, 4.2129],
    [17, "64QAM", 6, 0.75390625, 4.5234],
    [18, "64QAM", 6, 0.802734375, 4.8164],
    [19, "64QAM", 6, 0.8525390625, 5.1152],
    [20, "256QAM", 8, 0.66650390625, 5.332],
    [21, "256QAM", 8, 0.6943359375, 5.5547],
    [22, "256QAM", 8, 0.736328125, 5.8906],
    [23, "256QAM", 8, 0.7783203125, 6.2266],
    [24, "256QAM", 8, 0.8212890625, 6.5703],
    [25, "256QAM", 8, 0.8642578125, 6.9141],
    [26, "256QAM", 8, 0.89501953125, 7.1602],
    [27, "256QAM", 8, 0.92578125, 7.4063],
    [28, "QPSK", 2, None, None],
    [29, "16QAM", 4, None, None],
    [30, "64QAM", 6, None, None],
    [31, "256QAM", 8, None, None],
]

# ── PDSCH MCS Table 5.1.3.1-3 (64QAM Low SE) ──
PDSCH_MCS_TABLE_3 = [
    [ 0, "QPSK", 2, 0.029296875, 0.0586],
    [ 1, "QPSK", 2, 0.0390625, 0.0781],
    [ 2, "QPSK", 2, 0.048828125, 0.0977],
    [ 3, "QPSK", 2, 0.0625, 0.125],
    [ 4, "QPSK", 2, 0.076171875, 0.1523],
    [ 5, "QPSK", 2, 0.0966796875, 0.1934],
    [ 6, "QPSK", 2, 0.1171875, 0.2344],
    [ 7, "QPSK", 2, 0.1533203125, 0.3066],
    [ 8, "QPSK", 2, 0.1884765625, 0.377],
    [ 9, "QPSK", 2, 0.2451171875, 0.4902],
    [10, "QPSK", 2, 0.30078125, 0.6016],
    [11, "QPSK", 2, 0.3701171875, 0.7402],
    [12, "QPSK", 2, 0.4384765625, 0.877],
    [13, "QPSK", 2, 0.513671875, 1.0273],
    [14, "QPSK", 2, 0.587890625, 1.1758],
    [15, "16QAM", 4, 0.33203125, 1.3281],
    [16, "16QAM", 4, 0.369140625, 1.4766],
    [17, "16QAM", 4, 0.423828125, 1.6953],
    [18, "16QAM", 4, 0.478515625, 1.9141],
    [19, "16QAM", 4, 0.5400390625, 2.1602],
    [20, "16QAM", 4, 0.6015625, 2.4063],
    [21, "64QAM", 6, 0.427734375, 2.5664],
    [22, "64QAM", 6, 0.455078125, 2.7305],
    [23, "64QAM", 6, 0.5048828125, 3.0293],
    [24, "64QAM", 6, 0.5537109375, 3.3223],
    [25, "64QAM", 6, 0.6015625, 3.6094],
    [26, "64QAM", 6, 0.650390625, 3.9023],
    [27, "64QAM", 6, 0.7021484375, 4.2129],
    [28, "64QAM", 6, 0.75390625, 4.5234],
    [29, "QPSK", 2, None, None],
    [30, "16QAM", 4, None, None],
    [31, "64QAM", 6, None, None],
]

# ── PDSCH MCS Table 5.1.3.1-4 (1024QAM) ──
PDSCH_MCS_TABLE_4 = [
    [ 0, "QPSK", 2, 0.1171875, 0.2344],
    [ 1, "QPSK", 2, 0.1884765625, 0.377],
    [ 2, "QPSK", 2, 0.4384765625, 0.877],
    [ 3, "16QAM", 4, 0.369140625, 1.4766],
    [ 4, "16QAM", 4, 0.478515625, 1.9141],
    [ 5, "16QAM", 4, 0.6015625, 2.4063],
    [ 6, "64QAM", 6, 0.455078125, 2.7305],
    [ 7, "64QAM", 6, 0.5048828125, 3.0293],
    [ 8, "64QAM", 6, 0.5537109375, 3.3223],
    [ 9, "64QAM", 6, 0.6015625, 3.6094],
    [10, "64QAM", 6, 0.650390625, 3.9023],
    [11, "64QAM", 6, 0.7021484375, 4.2129],
    [12, "64QAM", 6, 0.75390625, 4.5234],
    [13, "64QAM", 6, 0.802734375, 4.8164],
    [14, "64QAM", 6, 0.8525390625, 5.1152],
    [15, "256QAM", 8, 0.66650390625, 5.332],
    [16, "256QAM", 8, 0.6943359375, 5.5547],
    [17, "256QAM", 8, 0.736328125, 5.8906],
    [18, "256QAM", 8, 0.7783203125, 6.2266],
    [19, "256QAM", 8, 0.8212890625, 6.5703],
    [20, "256QAM", 8, 0.8642578125, 6.9141],
    [21, "256QAM", 8, 0.89501953125, 7.1602],
    [22, "256QAM", 8, 0.92578125, 7.4063],
    [23, "1024QAM", 10, 0.78662109375, 7.8662],
    [24, "1024QAM", 10, 0.8330078125, 8.3301],
    [25, "1024QAM", 10, 0.87939453125, 8.7939],
    [26, "1024QAM", 10, 0.92578125, 9.2578],
    [27, "QPSK", 2, None, None],
    [28, "16QAM", 4, None, None],
    [29, "64QAM", 6, None, None],
    [30, "256QAM", 8, None, None],
    [31, "1024QAM", 10, None, None],
]

_TABLE_MAP = {
    "QAM64Table": PDSCH_MCS_TABLE_1,
    "QAM256Table": PDSCH_MCS_TABLE_2,
    "QAM64LowSETable": PDSCH_MCS_TABLE_3,
    "QAM1024Table": PDSCH_MCS_TABLE_4,
}


def get_mcs_table(table_name: str) -> list:
    """Get PDSCH MCS table by name.

    Args:
        table_name: 'QAM64Table', 'QAM256Table', 'QAM64LowSETable', 'QAM1024Table'

    Returns:
        List of [mcs_index, modulation, qm, target_code_rate(float), spectral_efficiency]
    """
    if table_name not in _TABLE_MAP:
        raise ValueError(f"Unknown table: {table_name}")
    return _TABLE_MAP[table_name]


def get_mcs_info(mcs_index: int, table_name: str = "QAM64Table") -> dict:
    """Get MCS info for a specific index.

    Returns dict with modulation, qm, target_code_rate, spectral_efficiency.
    """
    table = get_mcs_table(table_name)
    for row in table:
        if row[0] == mcs_index:
            return {
                "mcs_index": mcs_index,
                "modulation": row[1],
                "qm": row[2],
                "target_code_rate": row[3],
                "spectral_efficiency": row[4],
            }
    raise ValueError(f"MCS index {mcs_index} not found in {table_name}")


def main():
    parser = argparse.ArgumentParser(description="5G NR MCS lookup tables (TS 38.214 Sec 5.1.3.1)")
    parser.add_argument("--table", choices=list(_TABLE_MAP.keys()),
                        default="QAM64Table", help="MCS table name")
    parser.add_argument("--mcs", type=int, default=None, help="Specific MCS index to look up")
    args = parser.parse_args()

    try:
        if args.mcs is not None:
            info = get_mcs_info(args.mcs, args.table)
            print(json.dumps(info, ensure_ascii=False))
        else:
            table = get_mcs_table(args.table)
            result = {
                "table_name": args.table,
                "entries": len(table),
                "mcs_index": [r[0] for r in table],
                "modulation": [r[1] for r in table],
                "qm": [r[2] for r in table],
                "target_code_rate": [r[3] for r in table],
                "spectral_efficiency": [r[4] for r in table],
            }
            print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
