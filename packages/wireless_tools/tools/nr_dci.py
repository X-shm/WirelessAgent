"""nr_dci - 5G NR Downlink Control Information encoding and scrambling.

Implements TS 38.212 Section 7.3 DCI channel coding.
MATLAB equivalent: nrDCIEncode plus its PDCCH scrambling subset.

Processing chain:
  TX: (24 leading ones + DCI bits) → CRC24C(RNTI) →
      DCI bits + CRC → Polar encode → rate-match → codeword
"""
from __future__ import annotations
import argparse
import json
import sys
import os
import numpy as np

# Import our tools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nr_crc import _crc_encode_bits
from nr_polar import polar_encode, polar_rate_match


def dci_encode(dci_bits: np.ndarray, rnti: int, edci: int) -> np.ndarray:
    """Encode DCI message per TS 38.212 Section 7.3.

    Args:
        dci_bits: DCI message bits (length 12..140)
        rnti: RNTI value (0..65535)
        edci: Rate-matched output length

    Returns:
        Encoded codeword of length edci
    """
    dci_bits = np.asarray(dci_bits, dtype=np.int8).flatten()

    # TS 38.212 7.3.2 specifies 24 leading one bits *for the CRC calculation*.
    # They are not Polar information bits: Polar receives the original DCI
    # payload followed by the RNTI-masked CRC24C parity bits.
    crc_input = np.concatenate([np.ones(24, dtype=np.int8), dci_bits])
    crc_bits = _crc_encode_bits(crc_input, "24C", rnti)[-24:]
    c_with_crc = np.concatenate([dci_bits, crc_bits])
    encoded = polar_encode(c_with_crc, edci, nmax=9, iil=True)
    return polar_rate_match(encoded, len(c_with_crc), edci)


def dci_scramble(codeword: np.ndarray, n_id: int, n_rnti: int) -> np.ndarray:
    """Scramble DCI codeword per TS 38.211 7.3.2.3.

    cinit = nRNTI * 2^16 + nID (mod 2^31)

    Args:
        codeword: encoded DCI bits
        n_id: pdcch-DMRS-ScramblingID or NCellID
        n_rnti: C-RNTI

    Returns:
        Scrambled codeword
    """
    from nr_prbs import prbs
    cinit = int((n_rnti * (2**16) + n_id) % (2**31))
    seq = prbs(cinit, len(codeword))
    return (codeword ^ seq).astype(np.int8)


def main():
    parser = argparse.ArgumentParser(description="5G NR DCI encoder (TS 38.212 Sec 7.3)")
    parser.add_argument("--dci-bits", required=True, help="DCI message bits (comma-separated)")
    parser.add_argument("--rnti", type=int, required=True, help="RNTI (0..65535)")
    parser.add_argument("--edci", type=int, help="Encode-mode rate-matched output length")
    subparsers = parser.add_subparsers(dest="mode")
    enc = subparsers.add_parser("encode", help="Encode DCI")
    scr = subparsers.add_parser("scramble", help="Scramble encoded DCI")
    scr.add_argument("--n-id", type=int, required=True, help="Scrambling ID")
    args = parser.parse_args()

    if args.mode != "scramble" and args.edci is None:
        parser.error("--edci is required for DCI encoding")

    try:
        bits = np.array([int(x) for x in args.dci_bits.split(",")], dtype=np.int8)

        if args.mode == "scramble":
            scrambled = dci_scramble(bits, args.n_id, args.rnti)
            result = {
                "rnti": args.rnti,
                "n_id": args.n_id,
                "cinit": int((args.rnti * (2**16) + args.n_id) % (2**31)),
                "codeword": scrambled.astype(int).tolist(),
            }
        else:
            # Default: encode
            codeword = dci_encode(bits, args.rnti, args.edci)
            result = {
                "rnti": args.rnti,
                "edci": args.edci,
                "dci_len": len(bits),
                "k": len(bits) + 24,  # DCI payload + CRC24C
                "codeword": codeword.astype(int).tolist(),
            }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
