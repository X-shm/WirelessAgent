"""Independent NR DL-SCH / UL-SCH transport coding dimensions."""
from __future__ import annotations

import argparse
import json
import math
import sys

from nr_ldpc import _ZC_SET


_ZC = sorted({size for group in _ZC_SET.values() for size in group})


def sch_info(tbs: int, tcr: float, uplink: bool = False) -> dict:
    """Calculate TS 38.212 TB CRC, base graph and LDPC block dimensions."""
    if not isinstance(tbs, int) or tbs < 0:
        raise ValueError("tbs must be a nonnegative integer")
    if not 0 < tcr < 1:
        raise ValueError("tcr must be between 0 and 1")
    bgn = 2 if tbs <= 292 or (tbs <= 3824 and tcr <= 0.67) or tcr <= 0.25 else 1
    crc_len = 0 if tbs == 0 else (16 if tbs <= 3824 else 24)
    crc_name = "16" if tbs <= 3824 else "24A"
    if tbs == 0:
        result = {"CRC": crc_name, "L": 0, "BGN": bgn, "C": 1,
                  "Lcb": 0, "F": 0, "Zc": 2, "K": 0, "N": 0}
    else:
        b = tbs + crc_len
        kcb = 8448 if bgn == 1 else 3840
        lcb = 0 if b <= kcb else 24
        c = 1 if lcb == 0 else math.ceil(b / (kcb - lcb))
        bits_per_block = math.ceil((b + c * lcb) / c)
        if bgn == 1:
            kb = 22
        elif b > 640:
            kb = 10
        elif b > 560:
            kb = 9
        elif b > 192:
            kb = 8
        else:
            kb = 6
        zc = next(size for size in _ZC if kb * size >= bits_per_block)
        k = (22 if bgn == 1 else 10) * zc
        n = (66 if bgn == 1 else 50) * zc
        result = {"CRC": crc_name, "L": crc_len, "BGN": bgn, "C": c,
                  "Lcb": lcb, "F": k - bits_per_block, "Zc": zc, "K": k, "N": n}
    if uplink:
        result.update({"GULSCH": [], "GACK": 0, "GCSI1": 0, "GCSI2": 0,
                       "GACKRvd": 0, "QdACK": 0, "QdCSI1": 0, "QdCSI2": 0})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone NR DL-SCH / UL-SCH coding information")
    parser.add_argument("--direction", choices=("dl", "ul"), required=True)
    parser.add_argument("--tbs", type=int, required=True, help="Transport block bits")
    parser.add_argument("--tcr", type=float, required=True, help="Target code rate")
    args = parser.parse_args()
    try:
        print(json.dumps(sch_info(args.tbs, args.tcr, args.direction == "ul")))
    except (ValueError, StopIteration) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
