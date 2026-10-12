"""LTE-compatible error-vector-magnitude metrics."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def evm(measured=None, reference=None, error_vector=None):
    if error_vector is not None:
        normalized = np.asarray(error_vector, dtype=complex)
    else:
        measured = np.asarray(measured, dtype=complex)
        reference = np.asarray(reference, dtype=complex)
        if measured.shape != reference.shape or measured.size == 0:
            raise ValueError("measured and reference must be nonempty arrays with equal shape")
        power = math.sqrt(float(np.mean(np.abs(reference.reshape(-1)) ** 2)))
        if power == 0:
            power = 1.0
        normalized = (measured - reference) / power
    magnitudes = np.abs(normalized.reshape(-1))
    if magnitudes.size == 0:
        raise ValueError("error vector must not be empty")
    rms = math.sqrt(float(np.mean(magnitudes ** 2)))
    peak = float(np.max(magnitudes))
    rms_db = -math.inf if rms == 0 else 20.0 * math.log10(rms)
    return normalized, rms, peak, rms_db


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--measured")
    parser.add_argument("--reference")
    parser.add_argument("--error_vector")
    args = parser.parse_args()
    try:
        if args.error_vector is not None:
            normalized, rms, peak, rms_db = evm(error_vector=parse_complex(args.error_vector))
        else:
            if args.measured is None or args.reference is None:
                raise ValueError("provide measured+reference or error_vector")
            normalized, rms, peak, rms_db = evm(parse_complex(args.measured), parse_complex(args.reference))
        print(json.dumps({"rms": rms, "peak": peak, "rms_percent": 100*rms, "peak_percent": 100*peak, "rms_db": rms_db, "error_vector": complex_json(normalized)}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
