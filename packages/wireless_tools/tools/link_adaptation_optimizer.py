"""Conservative LTE MCS/TBS recommendation from measured SNR and link margin."""
from __future__ import annotations
import argparse
import json
import sys

from lte_mcs import mcs
from lte_tbs import tbs


_THRESHOLDS = [-6.5, -4.0, -2.6, -1.0, 1.0, 2.0, 3.0, 4.5, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0]


def optimize_link(snr_db, nprb, table="PDSCH", layers=1, margin_db=2.0, min_mcs=0, max_mcs=28, bler_target=0.1):
    snr, nprb, layers = float(snr_db), int(nprb), int(layers)
    if not 1 <= nprb <= 110 or layers not in (1, 2, 3, 4) or not 0 < bler_target < 1:
        raise ValueError("invalid PRB, layer count or BLER target")
    min_mcs, max_mcs = max(0, int(min_mcs)), min(28, int(max_mcs))
    effective = snr-float(margin_db)
    selected = min_mcs
    for index in range(min_mcs, max_mcs+1):
        if effective >= _THRESHOLDS[index]:
            selected = index
    itbs, modulation, rv = mcs(selected, table)
    while itbs is None and selected > min_mcs:
        selected -= 1
        itbs, modulation, rv = mcs(selected, table)
    block = tbs(nprb, itbs, layers)
    return {"recommended_mcs": selected, "itbs": itbs, "modulation": modulation, "rv": rv, "tbs_bits_per_subframe": block, "estimated_peak_mbps": block/1000.0, "effective_snr_db": effective, "margin_db": float(margin_db), "bler_target": float(bler_target), "method": "conservative_threshold_plus_3gpp_tables"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snr_db", type=float, required=True)
    parser.add_argument("--nprb", type=int, required=True)
    parser.add_argument("--table", choices=["PDSCH", "PDSCHTable2", "PDSCHTable3", "PUSCH"], default="PDSCH")
    parser.add_argument("--layers", type=int, default=1)
    parser.add_argument("--margin_db", type=float, default=2.0)
    parser.add_argument("--min_mcs", type=int, default=0)
    parser.add_argument("--max_mcs", type=int, default=28)
    parser.add_argument("--bler_target", type=float, default=0.1)
    args = parser.parse_args()
    try:
        print(json.dumps(optimize_link(**vars(args))))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
