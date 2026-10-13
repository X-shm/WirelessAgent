"""LTE CQI selection from explicit wideband/subband SINR measurements."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np


_POLYNOMIALS = {
    "port0": (2.11, -9.24), "txdiversity": (2.15, -8.44),
    "cdd": (2.73, -7.29), "spatialmux": (2.64, -5.69),
    "multiuser": (2.64, -5.69), "port5": (2.11, -9.24),
    "port7-8": (2.11, -9.24), "port8": (2.11, -9.24), "port7-14": (2.11, -9.24),
}


def _index(sinr, thresholds):
    valid = np.flatnonzero(thresholds < sinr)
    return int(valid[-1]+1) if len(valid) else 0


def cqi_select(sinr_db, tx_scheme="Port0", reporting="Wideband", custom_thresholds=None):
    values = np.asarray(sinr_db, dtype=float).reshape(-1)
    if not len(values) or not np.all(np.isfinite(values)):
        raise ValueError("sinr_db must contain finite values")
    scheme, reporting = tx_scheme.lower(), reporting.lower()
    if scheme not in _POLYNOMIALS or reporting not in ("wideband", "subband"):
        raise ValueError("unsupported transmission scheme or reporting mode")
    if custom_thresholds is None:
        slope, intercept = _POLYNOMIALS[scheme]
        thresholds = slope*np.asarray([2]+list(range(2, 16)))+intercept
    else:
        thresholds = np.asarray(custom_thresholds, dtype=float)
        if thresholds.shape != (15,):
            raise ValueError("custom_thresholds must contain 15 SINR values")
    wideband_sinr = 10*math.log10(float(np.mean(10**(values/10))))
    wideband = _index(wideband_sinr, thresholds)
    subband = [_index(value, thresholds) for value in values]
    offsets = [min(max(value-wideband, -1), 2) for value in subband]
    report = [wideband] if reporting == "wideband" else [wideband]+offsets
    return {"cqi_report": report, "wideband_cqi": wideband, "subband_cqi": subband, "subband_offset_levels": offsets if reporting == "subband" else [], "wideband_sinr_db": wideband_sinr, "sinr_thresholds_db": thresholds.tolist(), "tx_scheme": tx_scheme}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sinr_db", required=True)
    parser.add_argument("--tx_scheme", default="Port0")
    parser.add_argument("--reporting", choices=["Wideband", "Subband"], default="Wideband")
    parser.add_argument("--custom_thresholds")
    args = parser.parse_args()
    try:
        thresholds = None if args.custom_thresholds is None else json.loads(args.custom_thresholds)
        print(json.dumps(cqi_select(json.loads(args.sinr_db), args.tx_scheme, args.reporting, thresholds)))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
