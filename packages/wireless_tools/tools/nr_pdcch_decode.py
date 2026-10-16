"""Standalone NR PDCCH soft QPSK demodulation and descrambling."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from _complex_io import parse_complex
from nr_modulation import soft_demodulate
from nr_prbs import prbs


def pdcch_decode(symbols: np.ndarray, nid: int, nrnti: int, nvar: float = 1e-10) -> np.ndarray:
    values = np.asarray(symbols, dtype=np.complex128)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("symbols must be a nonempty complex vector")
    if not 0 <= nid <= 65535 or not 0 <= nrnti <= 65519:
        raise ValueError("nid must be 0..65535 and nrnti must be 0..65519")
    if nvar < 0:
        raise ValueError("nvar must be nonnegative")
    llr = soft_demodulate(values, "QPSK", nvar)
    cinit = (nrnti * (2 ** 16) + nid) % (2 ** 31)
    bits = prbs(cinit, len(llr))
    return llr * (1 - 2 * bits.astype(int))


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR PDCCH soft-bit decode")
    parser.add_argument("--symbols", required=True, help="Complex vector JSON {real,imag}")
    parser.add_argument("--nid", type=int, required=True)
    parser.add_argument("--nrnti", type=int, required=True)
    parser.add_argument("--nvar", type=float, default=1e-10)
    args = parser.parse_args()
    try:
        output = pdcch_decode(parse_complex(args.symbols), args.nid, args.nrnti, args.nvar)
        print(json.dumps({"soft_bits": output.tolist(), "n_bits": len(output)}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
