"""
LTE CRC Tool — LTE CRC 编码/校验工具 (3GPP TS 36.212 §5.1.1).

Replicates MATLAB lteCRCEncode / lteCRCDecode from the LTE Toolbox.
Supported polynomials: '24A', '24B', '16', '8'.
Filler bits (-1) are treated as logical 0 for CRC computation and preserved in output.
Optional MASK xors the CRC parity bits MSB-first.
"""
from __future__ import annotations

import json
import sys
import numpy as np

# Polynomials in L-bit representation (x^L term omitted), per TS 36.212 §5.1.1.
_POLYS = {
    '24A': 0x864CFB,
    '24B': 0x800063,
    '16': 0x1021,
    '8': 0x9B,
}
_LEN = {'24A': 24, '24B': 24, '16': 16, '8': 8}
_TYPES = tuple(_POLYS.keys())


def _check_poly(poly: str) -> None:
    if poly not in _POLYS:
        raise ValueError(f"Unsupported CRC poly '{poly}'. Supported: {list(_TYPES)}")


def crc_length(poly: str) -> int:
    _check_poly(poly)
    return _LEN[poly]


def _crc_remainder(work: np.ndarray, poly: str) -> int:
    """LTE CRC: a(x)*x^L mod g(x). Shift all bits in, then L more zero bits."""
    L = _LEN[poly]
    reg = 0
    for b in list(work) + [0] * L:
        top = (reg >> (L - 1)) & 1
        reg = ((reg << 1) & ((1 << L) - 1)) | int(b)
        if top:
            reg ^= _POLYS[poly]
    return reg


def crc_encode(bits, poly: str, mask: int = 0):
    """Append CRC parity bits to input. Filler (-1) preserved. Returns output vector."""
    _check_poly(poly)
    bits = np.asarray(bits, dtype=np.int64).reshape(-1)
    L = _LEN[poly]
    work = np.where(bits < 0, 0, bits)  # filler treated as 0 for CRC
    reg = _crc_remainder(work, poly)
    parity = np.zeros(L, dtype=np.int64)
    for i in range(L):
        p = (reg >> (L - 1 - i)) & 1
        if mask:
            p ^= (mask >> (L - 1 - i)) & 1
        parity[i] = p
    return np.concatenate([bits, parity])


def crc_verify(bits, poly: str, mask: int = 0):
    """Given input already carrying CRC, return (valid, data_without_crc)."""
    _check_poly(poly)
    bits = np.asarray(bits, dtype=np.int64).reshape(-1)
    L = _LEN[poly]
    if bits.size < L:
        raise ValueError(f"input length {bits.size} too short for {L}-bit CRC")
    data = bits[:-L]
    parity = bits[-L:]
    work = np.where(data < 0, 0, data)
    reg = _crc_remainder(work, poly)
    ok = True
    for i in range(L):
        p = (reg >> (L - 1 - i)) & 1
        if mask:
            p ^= (mask >> (L - 1 - i)) & 1
        if p != int(parity[i]):
            ok = False
            break
    return ok, data


def _parse_bits(text: str) -> np.ndarray:
    return np.array([int(b) for b in text.split(',')], dtype=np.int64)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="LTE CRC tool")
    parser.add_argument('--poly', required=True, help="CRC polynomial: 24A / 24B / 16 / 8")
    parser.add_argument('--bits', help="comma-separated bits, -1 allowed for filler")
    parser.add_argument('--bits_hex', '--bits-hex', dest='bits_hex', help="hex string of bits (msb first)")
    parser.add_argument('--mask', type=lambda x: int(x, 0), default=0, help="mask integer (e.g. RNTI), default 0")
    parser.add_argument('--verify', action='store_true', help="verify input already carrying CRC")
    args = parser.parse_args()

    if args.bits_hex:
        raw = args.bits_hex
        bits = np.array([int(b) for b in bin(int(raw, 16))[2:].zfill(len(raw) * 4)], dtype=np.int64)
    else:
        bits = _parse_bits(args.bits)

    if args.verify:
        valid, data = crc_verify(bits, args.poly, args.mask)
        print(json.dumps({"poly": args.poly, "valid": bool(valid), "data": data.tolist()}, ensure_ascii=False))
    else:
        out = crc_encode(bits, args.poly, args.mask)
        L = crc_length(args.poly)
        print(json.dumps({
            "poly": args.poly,
            "parity": out[-L:].tolist(),
            "crc": out.tolist(),
        }, ensure_ascii=False))


if __name__ == '__main__':
    main()
