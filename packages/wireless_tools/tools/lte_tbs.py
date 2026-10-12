"""
LTE TBS Tool — LTE 传输块大小(TBS)查表工具 (3GPP TS 36.213 §7.1.7.2).

Replicates MATLAB lteTBS from the LTE Toolbox.
Looks up Table 7.1.7.2.1-1 (Release 15, 110 NPRB x 38 ITBS), plus the spatial
multiplexing layer translation for SMNLAYER 1..4.
  lteTBS(NPRB)            -> full 38-value column for NPRB (1..110)
  lteTBS(NPRB, ITBS)      -> TBS for the given TBS index (0..37)
  lteTBS(NPRB, ITBS, L)   -> TBS with L spatial multiplexing layers
ITBS=-1 means DTX: TBS=0.
Reserved entries are NaN (returned as null).
The tables are dumped from MATLAB's compiled lteTBS via lte_tbs_tables.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import numpy as np

_TABLES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'lte_tbs_tables.json'
)

_TABLES_CACHE: dict = {}


def _load_tables() -> dict:
    if _TABLES_CACHE:
        return _TABLES_CACHE
    with open(_TABLES_PATH, 'r', encoding='utf-8') as f:
        d = json.load(f)
    # JSON null (NaN) loads as None; float dtype turns it into nan.
    _TABLES_CACHE['nprb'] = np.array(d['nprb'], dtype=int)
    _TABLES_CACHE['tbs'] = {
        L: np.array(d[f'tbs{L}'], dtype=float) for L in (1, 2, 3, 4)
    }
    return _TABLES_CACHE


def _to_int_or_none(v: float):
    return None if np.isnan(v) else int(v)


def tbs(nprb: int, itbs=None, smnlayer: int = 1):
    """Look up transport block size.

    nprb: 1..110. itbs: None -> full column 0..37; int or iterable; -1 = DTX.
    smnlayer: 1..4 (spatial multiplexing layers).
    Scalar itbs in -> scalar TBS out.
    """
    tables = _load_tables()
    if not isinstance(nprb, int) or not (1 <= nprb <= 110):
        raise ValueError("NPRB must be an integer between 1 and 110.")
    if smnlayer not in (1, 2, 3, 4):
        raise ValueError("SMNLAYER must be one of 1, 2, 3, 4.")
    tab = tables['tbs'][smnlayer]  # 110 x 38

    if itbs is None:
        return [_to_int_or_none(v) for v in tab[nprb - 1, :]]

    scalar = isinstance(itbs, int) and not isinstance(itbs, bool)
    idxs = [itbs] if scalar else list(itbs)
    out = []
    for i in idxs:
        if isinstance(i, bool) or not isinstance(i, int):
            raise ValueError("ITBS must be an integer.")
        if i == -1:
            out.append(0)
        elif 0 <= i <= 37:
            out.append(_to_int_or_none(tab[nprb - 1, i]))
        else:
            raise ValueError("ITBS must be between -1 and 37.")
    return out[0] if scalar else out


def _parse_itbs(text: str):
    parts = [p for p in text.split(',') if p != '']
    vals = [int(p) for p in parts]
    return vals[0] if len(vals) == 1 else vals


def main():
    parser = argparse.ArgumentParser(description="LTE transport block size tool")
    parser.add_argument('--nprb', required=True, type=int, help="number of PRBs (1..110)")
    parser.add_argument('--itbs', help="TBS index, comma-separated (0..37, -1=DTX); omit for full column")
    parser.add_argument('--smnlayer', type=int, default=1, help="spatial multiplexing layers (1..4), default 1")
    args = parser.parse_args()

    try:
        itbs = None if not args.itbs else _parse_itbs(args.itbs)
        out = tbs(args.nprb, itbs, args.smnlayer)
    except ValueError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    result = {
        "nprb": args.nprb,
        "itbs": None if itbs is None else itbs,
        "smnlayer": args.smnlayer,
        "tbs": out,
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
