"""nr_tbs - 5G NR Transport Block Size determination.

Implements TS 38.214 Sections 5.1.3.2 (DL) / 6.1.4.2 (UL) TBS calculation.
MATLAB equivalent: nrTBS(modulation, nlayers, nPRB, NREPerPRB, tcr, xOh, tbScaling)
"""
from __future__ import annotations
import argparse
import json
import sys
import numpy as np
import math

# ── TBS lookup table (TS 38.214 Table 5.1.3.2-1) ──
# For Ninfo <= 3824, use this table
_TBS_TABLE = [
    24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136, 144,
    152, 160, 168, 176, 184, 192, 208, 224, 240, 256, 272, 288, 304, 320,
    336, 352, 368, 384, 408, 432, 456, 480, 504, 528, 552, 576, 608, 640,
    672, 704, 736, 768, 808, 848, 888, 928, 984, 1032, 1064, 1096, 1128,
    1160, 1192, 1224, 1256, 1288, 1320, 1352, 1416, 1480, 1544, 1608,
    1672, 1736, 1800, 1864, 1928, 2024, 2088, 2152, 2216, 2280, 2408,
    2472, 2536, 2600, 2664, 2728, 2792, 2856, 2976, 3104, 3240, 3368,
    3496, 3624, 3752, 3824,
]

_MOD_ORDER = {
    "pi/2-BPSK": 1,
    "BPSK": 1,
    "QPSK": 2,
    "16QAM": 4,
    "64QAM": 6,
    "256QAM": 8,
    "1024QAM": 10,
}


def _get_tbs_from_table(ninfo: int) -> int:
    """Look up TBS from table for Ninfo <= 3824 (TS 38.214 Table 5.1.3.2-1)."""
    if ninfo <= 0:
        return 0
    # Find the smallest TBS >= ninfo
    for tbs in _TBS_TABLE:
        if tbs >= ninfo:
            return tbs
    return _TBS_TABLE[-1]


def tbs(modulation: str, nlayers: int, nprb: int, nre_per_prb: int,
        tcr: float, xoh: int = 0, tb_scaling: float = 1.0) -> int:
    """Calculate Transport Block Size per TS 38.214.

    Args:
        modulation: 'QPSK', '16QAM', '64QAM', '256QAM', '1024QAM', 'pi/2-BPSK'
        nlayers: number of transmission layers (1..8)
        nprb: number of allocated PRBs (0..275)
        nre_per_prb: REs per PRB (0..156)
        tcr: target code rate (0 < tcr < 1)
        xoh: additional overhead (0, 6, 12, 18)
        tb_scaling: TB scaling factor (0.25, 0.5, 1.0)

    Returns:
        Transport block size in bits
    """
    mod_upper = modulation.upper().replace("/", "")
    if mod_upper not in _MOD_ORDER:
        raise ValueError(f"Unknown modulation: {modulation}")
    qm = _MOD_ORDER[mod_upper]

    if mod_upper == "PI/2-BPSK":
        qm = 1

    # Step 1: NRE'
    nre_prime = nre_per_prb - xoh
    if nre_prime < 0:
        nre_prime = 0

    # Step 2: NRE
    nre = min(156, nre_prime) * nprb

    if nre == 0:
        return 0

    # Step 3: Ninfo
    ninfo = int(tb_scaling * nre * tcr * qm * nlayers)

    if ninfo <= 0:
        return 0

    # Step 4: Determine TBS
    if ninfo <= 3824:
        # Use table
        n = max(3, int(math.floor(math.log2(ninfo))) - 6)
        nd_info = max(24, (2 ** n) * (ninfo // (2 ** n)))
        tbs_val = _get_tbs_from_table(nd_info)
    else:
        # Use formula
        n = int(math.floor(math.log2(ninfo - 24))) - 5
        nd_info = max(3840, (2 ** n) * round((ninfo - 24) / (2 ** n)))

        if tcr <= 0.25:
            c = math.ceil((nd_info + 24) / 3816)
        elif nd_info > 8424:
            c = math.ceil((nd_info + 24) / 8424)
        else:
            c = 1

        tbs_val = 8 * c * math.ceil((nd_info + 24) / (8 * c)) - 24

    return tbs_val


def main():
    parser = argparse.ArgumentParser(description="5G NR TBS calculator (TS 38.214 Sec 5.1.3.2)")
    parser.add_argument("--modulation", required=True, help="Modulation scheme")
    parser.add_argument("--nlayers", type=int, required=True, help="Number of layers (1..8)")
    parser.add_argument("--nprb", type=int, required=True, help="Number of PRBs (0..275)")
    parser.add_argument("--nre-per-prb", type=int, required=True, help="REs per PRB (0..156)")
    parser.add_argument("--tcr", type=float, required=True, help="Target code rate")
    parser.add_argument("--xoh", type=int, default=0, help="Additional overhead")
    parser.add_argument("--tb-scaling", type=float, default=1.0, help="TB scaling factor")
    args = parser.parse_args()

    try:
        result_tbs = tbs(args.modulation, args.nlayers, args.nprb,
                         args.nre_per_prb, args.tcr, args.xoh, args.tb_scaling)
        result = {
            "modulation": args.modulation,
            "nlayers": args.nlayers,
            "nPRB": args.nprb,
            "NREPerPRB": args.nre_per_prb,
            "tcr": args.tcr,
            "xOh": args.xoh,
            "tbScaling": args.tb_scaling,
            "tbs": result_tbs,
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
