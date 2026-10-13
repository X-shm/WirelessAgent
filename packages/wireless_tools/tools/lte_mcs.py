"""
LTE MCS Tool — LTE 调制与编码方案(MCS)查表工具 (3GPP TS 36.213).

Replicates MATLAB lteMCS from the LTE Toolbox.
Maps MCS index IMCS -> (I_TBS, Modulation, RV) using tables:
  PDSCH       (Table 7.1.7.1-1)
  PDSCHTable2 (Table 7.1.7.1-1A, Release 12, up to 256QAM)
  PDSCHTable3 (Table 7.1.7.1-1B, Release 15, up to 1024QAM)
  PUSCH       (Table 8.6.1-1)
IMCS=-1 means DTX: ITBS=-1, MOD='QPSK', RV=0.
Reserved ITBS entries are NaN (returned as null); reserved MOD entries are ''.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Union

# Each entry: (itbs, mod, rv) lists indexed by IMCS 0..31. None = NaN (reserved).
_TABLES = {
    'PDSCH': (
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 11, 12, 13, 14, 15,
         15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, None, None, None],
        ['QPSK'] * 10 + ['16QAM'] * 7 + ['64QAM'] * 12 + ['QPSK', '16QAM', '64QAM'],
        [0] * 32,
    ),
    'PDSCHTABLE2': (
        [0, 2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
         21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, None, None, None, None],
        ['QPSK'] * 5 + ['16QAM'] * 6 + ['64QAM'] * 9 + ['256QAM'] * 8
        + ['QPSK', '16QAM', '64QAM', '256QAM'],
        [0] * 32,
    ),
    'PDSCHTABLE3': (
        [0, 2, 4, 6, 8, 11, 13, 15, 16, 18, 20, 21, 22, 23, 24, 25,
         27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, None, None, None, None, None],
        ['QPSK'] * 5 + ['16QAM'] * 3 + ['64QAM'] * 7 + ['256QAM'] * 8 + ['1024QAM'] * 4
        + ['QPSK', '16QAM', '64QAM', '256QAM', '1024QAM'],
        [0] * 32,
    ),
    'PUSCH': (
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 12, 13, 14, 15,
         16, 17, 18, 19, 19, 20, 21, 22, 23, 24, 25, 26, None, None, None],
        ['QPSK'] * 11 + ['16QAM'] * 10 + ['64QAM'] * 8 + ['', '', ''],
        [0] * 29 + [1, 2, 3],
    ),
}
_SUPPORTED_TABLES = tuple(_TABLES.keys())


def mcs(imcs, table: str = 'PDSCH'):
    """Look up MCS index -> (ITBS, Modulation, RV). Scalar in -> scalar out.

    imcs: int or iterable of ints, each in -1..31 (-1 = DTX).
    table: 'PDSCH' | 'PDSCHTable2' | 'PDSCHTable3' | 'PUSCH'.
    """
    t = table.upper()
    if t not in _TABLES:
        raise ValueError(
            f"Unsupported MCS table '{table}'. Supported: {list(_SUPPORTED_TABLES)}"
        )
    itbs_t, mod_t, rv_t = _TABLES[t]

    scalar = isinstance(imcs, int) and not isinstance(imcs, bool)
    idxs = [imcs] if scalar else list(imcs)
    itbs_out, mod_out, rv_out = [], [], []
    for im in idxs:
        if isinstance(im, bool) or not isinstance(im, int) or im < -1 or im > 31:
            raise ValueError("MCS index values must be integers between -1 and 31.")
        if im == -1:  # DTX
            itbs_out.append(-1)
            mod_out.append('QPSK')
            rv_out.append(0)
        else:
            itbs_out.append(itbs_t[im])
            mod_out.append(mod_t[im])
            rv_out.append(rv_t[im])
    if scalar:
        return itbs_out[0], mod_out[0], rv_out[0]
    return itbs_out, mod_out, rv_out


def _parse_imcs(text: str) -> list:
    return [int(x) for x in text.split(',') if x != '']


def main():
    parser = argparse.ArgumentParser(description="LTE MCS lookup tool")
    parser.add_argument('--imcs', required=True, help="MCS index or comma-separated list (-1..31, -1=DTX)")
    parser.add_argument('--table', default='PDSCH',
                        help="MCS table: PDSCH / PDSCHTable2 / PDSCHTable3 / PUSCH (default PDSCH)")
    args = parser.parse_args()

    imcs = _parse_imcs(args.imcs)
    scalar = len(imcs) == 1
    if scalar:
        imcs = imcs[0]
    try:
        itbs, mod, rv = mcs(imcs, args.table)
    except ValueError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    out = {"table": args.table, "imcs": imcs}
    if scalar:
        out.update({"itbs": itbs, "mod": mod, "rv": rv})
    else:
        out.update({"itbs": itbs, "mod": mod, "rv": rv})
    print(json.dumps(out, ensure_ascii=False))


if __name__ == '__main__':
    main()
