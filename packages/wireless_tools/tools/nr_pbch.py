"""nr_pbch - 5G NR Physical Broadcast Channel (PBCH) 编码/解码。

Implements TS 38.211 Section 7.3.3 PBCH processing.
MATLAB equivalent: nrPBCH(cw, ncellid, v) and nrPBCHDecode(sym, ncellid, v, nVar)

PBCH processing chain:
  Encode: BCH codeword -> PBCH PRBS scrambling -> QPSK modulation -> symbols
  Decode: symbols -> QPSK soft demodulation -> PBCH PRBS descrambling -> soft bits
"""
from __future__ import annotations

import argparse
import json
import sys
import os
import numpy as np

# Allow importing sibling modules when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nr_prbs import prbs
from nr_modulation import modulate, soft_demodulate


def pbch_prbs(ncellid: int, v: int, n: int, mapping: str = "binary") -> np.ndarray:
    """Generate PBCH scrambling sequence per TS 38.211 Section 7.3.3.1.

    The PBCH PRBS is the NR PRBS initialized with cinit = ncellid,
    starting at offset v*n and of length n.

    Args:
        ncellid: physical layer cell identity (0..1007)
        v: 2 or 3 LSBs of SS/PBCH block index (0..7)
        n: length of the sequence
        mapping: 'binary' (0/1) or 'signed' (1/-1, where 0->+1, 1->-1)

    Returns:
        PBCH scrambling sequence of length n
    """
    if ncellid < 0 or ncellid > 1007:
        raise ValueError(f"ncellid must be 0..1007, got {ncellid}")
    if v < 0 or v > 7:
        raise ValueError(f"v must be 0..7, got {v}")

    # PBCH PRBS = nrPRBS(cinit=ncellid, [v*n, n])
    return prbs(ncellid, [v * n, n], mapping)


def pbch_encode(cw: np.ndarray, ncellid: int, v: int) -> np.ndarray:
    """PBCH encoding: scramble + QPSK modulate.

    Args:
        cw: BCH codeword bits (length 864 per spec, but any even length works)
        ncellid: physical cell identity (0..1007)
        v: 2 or 3 LSBs of SS/PBCH block index (0..7)

    Returns:
        Complex QPSK symbols (length = len(cw)/2)
    """
    cw = np.asarray(cw, dtype=np.int8).reshape(-1)

    # Step 1: Generate PBCH PRBS and scramble
    c = pbch_prbs(ncellid, v, len(cw), mapping="binary")
    scrambled = cw ^ c

    # Step 2: QPSK modulation
    sym = modulate(scrambled, "QPSK")

    return sym


def pbch_decode(sym: np.ndarray, ncellid: int, v: int, nvar: float = 1e-10) -> np.ndarray:
    """PBCH decoding: QPSK soft demodulate + descramble.

    Args:
        sym: received PBCH complex symbols (length 432 per spec)
        ncellid: physical cell identity (0..1007)
        v: 2 or 3 LSBs of SS/PBCH block index (0..7)
        nvar: noise variance estimate for soft demodulation (default 1e-10)

    Returns:
        Soft bits (LLR values). Positive -> bit=0, negative -> bit=1.
        Length = 2 * len(sym).
    """
    sym = np.asarray(sym, dtype=np.complex128).reshape(-1)

    # Step 1: QPSK soft demodulation
    demod = soft_demodulate(sym, "QPSK", nvar)

    # Step 2: Generate PBCH PRBS in signed format (0->+1, 1->-1)
    c_signed = pbch_prbs(ncellid, v, len(demod), mapping="signed")

    # Step 3: Descramble by element-wise multiplication
    #   If PRBS bit = 0 (signed +1): soft bit unchanged
    #   If PRBS bit = 1 (signed -1): soft bit sign flipped (LLR reversed)
    soft_bits = demod * c_signed

    return soft_bits


def _parse_bits(text: str) -> np.ndarray:
    """Parse comma-separated bit string."""
    return np.array([int(b.strip()) for b in text.split(",") if b.strip()], dtype=np.int8)


def _parse_symbols_json(text: str) -> np.ndarray:
    """Parse JSON symbols in format {"real":[...], "imag":[...]}."""
    data = json.loads(text)
    real = np.array(data["real"], dtype=np.float64)
    imag = np.array(data["imag"], dtype=np.float64)
    return real + 1j * imag


def main():
    parser = argparse.ArgumentParser(
        description="5G NR PBCH encoder/decoder (TS 38.211 Sec 7.3.3)"
    )
    parser.add_argument(
        "--mode", choices=["encode", "decode"], required=True,
        help="Operation mode: encode or decode"
    )
    parser.add_argument(
        "--bits", type=str, default=None,
        help="Comma-separated input bits for encode mode (e.g. 0,1,1,0)"
    )
    parser.add_argument(
        "--symbols", type=str, default=None,
        help='JSON symbols for decode mode: {"real":[...],"imag":[...]}'
    )
    parser.add_argument(
        "--ncellid", type=int, required=True,
        help="Physical cell ID (0..1007)"
    )
    parser.add_argument(
        "--v", type=int, required=True,
        help="2 or 3 LSBs of SS/PBCH block index (0..7)"
    )
    parser.add_argument(
        "--nvar", type=float, default=1e-10,
        help="Noise variance for soft demodulation (decode mode, default 1e-10)"
    )
    args = parser.parse_args()

    try:
        if args.mode == "encode":
            if not args.bits:
                raise ValueError("encode mode requires --bits")
            cw = _parse_bits(args.bits)
            sym = pbch_encode(cw, args.ncellid, args.v)
            result = {
                "symbols_real": sym.real.tolist(),
                "symbols_imag": sym.imag.tolist(),
                "n_symbols": int(len(sym)),
            }
        else:  # decode
            if not args.symbols:
                raise ValueError("decode mode requires --symbols")
            sym = _parse_symbols_json(args.symbols)
            soft_bits = pbch_decode(sym, args.ncellid, args.v, args.nvar)
            result = {
                "soft_bits": soft_bits.tolist(),
                "n_bits": int(len(soft_bits)),
            }

        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
