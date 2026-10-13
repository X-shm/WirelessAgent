"""NR CRC Tool — 5G NR CRC 编解码工具 (3GPP TS 38.212 §5.1).

Replicates MATLAB nrCRCEncode / nrCRCDecode from the 5G Toolbox.
Polynomials: '6','11','16','24A','24B','24C'.
Verified against MATLAB golden samples.

CRC polynomials (binary, excluding leading x^L term — stored as coefficients):
  6:   x^6 + x^5 + 1
  11:  x^11 + x^10 + x^9 + x^5 + 1
  16:  x^16 + x^12 + x^5 + 1  (CRC-CCITT)
  24A: x^24 + x^23 + x^18 + x^17 + x^14 + x^11 + x^10 + x^7 + x^6 + x^5 + x^4 + x^3 + x + 1
  24B: x^24 + x^23 + x^6 + x^5 + x + 1
  24C: x^24 + x^23 + x^21 + x^20 + x^17 + x^15 + x^13 + x^12 + x^8 + x^4 + x^2 + x + 1
"""
from __future__ import annotations

import json
import os
import sys
import numpy as np

# CRC polynomials (excluding leading x^L — bit j=1 means x^j term present)
_POLYNOMIALS = {
    '6':    np.array([1,1,0,0,0,0,1], dtype=np.uint8),                                  # g_CRC6
    '11':   np.array([1,1,1,0,0,0,1,0,0,0,0,1], dtype=np.uint8),                       # g_CRC11
    '16':   np.array([1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1], dtype=np.uint8),            # g_CRC16
    '24A':  np.array([1,1,0,0,0,0,1,1,0,0,1,0,0,1,1,0,0,1,1,1,1,1,0,1,1], dtype=np.uint8),   # g_CRC24A
    '24B':  np.array([1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1], dtype=np.uint8),   # g_CRC24B
    '24C':  np.array([1,1,0,1,1,0,0,1,0,1,0,1,1,0,0,0,1,0,0,0,1,0,1,1,1], dtype=np.uint8),   # g_CRC24C
}

_POLY_LENGTHS = {'6': 6, '11': 11, '16': 16, '24A': 24, '24B': 24, '24C': 24}


def _crc_encode_bits(data: np.ndarray, poly: str, mask: int = 0) -> np.ndarray:
    """CRC encoding over GF(2): append L-bit CRC to data."""
    g = _POLYNOMIALS[poly]
    L = _POLY_LENGTHS[poly]
    data = np.asarray(data, dtype=np.uint8) % 2
    n = len(data)
    # padded dividend: data << L
    dividend = np.concatenate([data, np.zeros(L, dtype=np.uint8)])
    # Long division over GF(2)
    remainder = dividend.copy()
    for i in range(n):
        if remainder[i]:
            remainder[i:i + L + 1] ^= g
    crc_bits = remainder[-L:]
    if mask:
        mask_bits = np.array([(mask >> (L - 1 - j)) & 1 for j in range(L)], dtype=np.uint8)
        crc_bits ^= mask_bits
    return np.concatenate([data, crc_bits])


def _crc_decode_bits(blkcrc: np.ndarray, poly: str, mask: int = 0) -> tuple[np.ndarray, bool]:
    """CRC decoding: check and extract. Returns (data, error_flag)."""
    g = _POLYNOMIALS[poly]
    L = _POLY_LENGTHS[poly]
    blkcrc = np.asarray(blkcrc, dtype=np.uint8) % 2
    n = len(blkcrc) - L
    data = blkcrc[:n]
    # Re-encode
    encoded = _crc_encode_bits(data, poly, mask)
    crc_match = np.array_equal(encoded[-L:], blkcrc[-L:])
    return data, not crc_match


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NR CRC tool")
    parser.add_argument('--poly', required=True, choices=list(_POLYNOMIALS.keys()))
    parser.add_argument('--bits', help="comma-separated data bits")
    parser.add_argument('--mask', type=int, default=0, help="XOR mask value")
    parser.add_argument('--decode', action='store_true', help="check CRC on input bits")
    args = parser.parse_args()

    bits = np.array([int(b) for b in args.bits.split(',')], dtype=np.uint8)

    if args.decode:
        data, err = _crc_decode_bits(bits, args.poly, args.mask)
        print(json.dumps({"poly": args.poly, "data": data.tolist(), "crc_error": bool(err)}))
    else:
        out = _crc_encode_bits(bits, args.poly, args.mask)
        print(json.dumps({"poly": args.poly, "input_bits": bits.tolist(),
                          "output_bits": out.tolist(), "n_crc": _POLY_LENGTHS[args.poly]}))


if __name__ == '__main__':
    main()
