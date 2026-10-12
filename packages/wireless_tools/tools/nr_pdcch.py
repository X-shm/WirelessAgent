"""nr_pdcch - 5G NR Physical Downlink Control Channel.

Implements TS 38.211 Section 7.3.2 PDCCH scrambling and modulation.
MATLAB equivalent: nrPDCCH(dciCW, nID, nRNTI)

Processing: Scramble → QPSK modulation
"""
from __future__ import annotations
import argparse
import json
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nr_prbs import prbs
from nr_modulation import modulate
from nr_dci import dci_scramble


def pdcch(codeword: np.ndarray, n_id: int, n_rnti: int) -> np.ndarray:
    """Generate PDCCH symbols from encoded DCI codeword.

    Args:
        codeword: encoded DCI codeword (binary)
        n_id: pdcch-DMRS-ScramblingID (0..65535) or NCellID (0..1007)
        n_rnti: C-RNTI (0..65535)

    Returns:
        Complex QPSK PDCCH symbols
    """
    # Step 1: Scrambling
    scrambled = dci_scramble(codeword, n_id, n_rnti)

    # Step 2: QPSK modulation
    symbols = modulate(scrambled, "QPSK")
    return symbols


def main():
    parser = argparse.ArgumentParser(description="5G NR PDCCH (TS 38.211 Sec 7.3.2)")
    parser.add_argument("--codeword", required=True, help="Encoded DCI codeword bits (comma-separated)")
    parser.add_argument("--n-id", type=int, required=True, help="Scrambling ID")
    parser.add_argument("--n-rnti", type=int, required=True, help="C-RNTI")
    args = parser.parse_args()

    try:
        bits = np.array([int(x) for x in args.codeword.split(",")], dtype=np.int8)
        sym = pdcch(bits, args.n_id, args.n_rnti)
        result = {
            "n_id": args.n_id,
            "n_rnti": args.n_rnti,
            "cinit": int((args.n_rnti * (2**16) + args.n_id) % (2**31)),
            "input_len": len(bits),
            "output_len": len(sym),
            "sym_real": sym.real.tolist(),
            "sym_imag": sym.imag.tolist(),
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
