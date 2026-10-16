"""Standalone single-codeword NR PDSCH physical-layer soft decode."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex
from nr_layer_map import layer_demap
from nr_modulation import soft_demodulate
from nr_prbs import prbs


def pdsch_decode(
    symbols: np.ndarray, modulation: str, nid: int, rnti: int, nvar: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(symbols, dtype=np.complex128)
    if values.ndim == 1:
        values = values[:, None]
    if values.ndim != 2 or values.shape[0] == 0 or not 1 <= values.shape[1] <= 4:
        raise ValueError("symbols must be a nonempty N×L matrix with 1..4 layers")
    if not 0 <= nid <= 1023 or not 0 <= rnti <= 65535:
        raise ValueError("nid must be 0..1023 and rnti must be 0..65535")
    if nvar < 0:
        raise ValueError("nvar must be nonnegative")
    demapped = layer_demap(values, values.shape[1])
    llr = soft_demodulate(demapped, modulation, nvar)
    cinit = (rnti << 15) + nid
    sequence = prbs(cinit, len(llr))
    return llr * (1 - 2 * sequence.astype(int)), demapped


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR PDSCH soft-bit decode")
    parser.add_argument("--symbols", required=True, help="Complex N×L array JSON {real,imag}")
    parser.add_argument("--modulation", required=True)
    parser.add_argument("--nid", type=int, required=True)
    parser.add_argument("--rnti", type=int, required=True)
    parser.add_argument("--nvar", type=float, default=1e-10)
    args = parser.parse_args()
    try:
        bits, demapped = pdsch_decode(parse_complex(args.symbols), args.modulation, args.nid, args.rnti, args.nvar)
        print(json.dumps({"soft_bits": bits.tolist(), "constellation": complex_json(demapped), "n_bits": len(bits)}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
