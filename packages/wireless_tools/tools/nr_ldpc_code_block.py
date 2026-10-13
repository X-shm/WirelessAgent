"""NR LDPC Code Block Segmentation Tool
5G NR LDPC code block segmentation/desegmentation (3GPP TS 38.212 section 5.2.2).
Replicates MATLAB nrCodeBlockSegmentLDPC / nrCodeBlockDesegmentLDPC.
Supports BG1 (Kcb=8448) and BG2 (Kcb=3840). Uses CRC-24B.
"""
from __future__ import annotations

import json
import sys
import numpy as np

# CRC-24B polynomial: x^24 + x^23 + x^6 + x^5 + x + 1
_CRC24B_POLY = np.array(
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1],
    dtype=np.uint8,
)
_CRC24B_LEN = 24

# Lifting size set from TS 38.212 Table 5.3.2-1
_ZLIST = np.array(
    list(range(2, 17))
    + list(range(18, 33, 2))
    + list(range(36, 65, 4))
    + list(range(72, 129, 8))
    + list(range(144, 257, 16))
    + list(range(288, 385, 32)),
    dtype=int,
)


def _get_cbs_info(blk_len: int, bgn: int) -> dict:
    """Get code block segmentation info."""
    Kcb = 8448 if bgn == 1 else 3840
    if blk_len <= Kcb:
        L = 0
        C = 1
        Bd = blk_len
    else:
        L = 24
        C = int(np.ceil(blk_len / (Kcb - L)))
        Bd = blk_len + C * L
    cbz = int(np.ceil(blk_len / C))
    Kd = int(np.ceil(Bd / C))
    if bgn == 1:
        Kb = 22
    else:
        if blk_len > 640:
            Kb = 10
        elif blk_len > 560:
            Kb = 9
        elif blk_len > 192:
            Kb = 8
        else:
            Kb = 6
    Zc = int(np.min(_ZLIST[Kb * _ZLIST >= Kd]))
    K = Kb * Zc
    F = K - Kd
    return {"C": C, "CBZ": cbz, "Lcb": L, "F": F, "K": K, "Zc": Zc, "Kb": Kb}


def _crc24b_encode(data: np.ndarray) -> np.ndarray:
    """CRC-24B encoding over GF(2)."""
    data = np.asarray(data, dtype=np.uint8) % 2
    n = len(data)
    dividend = np.concatenate([data, np.zeros(_CRC24B_LEN, dtype=np.uint8)])
    remainder = dividend.copy()
    for i in range(n):
        if remainder[i]:
            remainder[i : i + _CRC24B_LEN + 1] ^= _CRC24B_POLY
    crc_bits = remainder[-_CRC24B_LEN:]
    return np.concatenate([data, crc_bits])


def _crc24b_decode(blkcrc: np.ndarray) -> tuple:
    """CRC-24B decoding. Returns (data, error_flag)."""
    blkcrc = np.asarray(blkcrc, dtype=np.uint8) % 2
    n = len(blkcrc) - _CRC24B_LEN
    data = blkcrc[:n]
    encoded = _crc24b_encode(data)
    crc_match = np.array_equal(encoded[-_CRC24B_LEN:], blkcrc[-_CRC24B_LEN:])
    return data, not crc_match


def code_block_segment(bits, bgn):
    """LDPC code block segmentation and CRC attachment."""
    bits = np.asarray(bits, dtype=np.float64).reshape(-1)
    blk_len = len(bits)
    if blk_len == 0:
        return {"cbs": np.zeros((0, 1), dtype=np.float64), "C": 1, "K": 0,
                "info": {"C": 1, "CBZ": 0, "Lcb": 0, "F": 0, "K": 0, "Zc": 0, "Kb": 0}}
    info = _get_cbs_info(blk_len, bgn)
    C, CBZ, F, K = info["C"], info["CBZ"], info["F"], info["K"]
    if C == 1:
        cbCRC = bits.copy().reshape(-1, 1)
    else:
        padded = np.zeros(CBZ * C, dtype=np.float64)
        padded[:blk_len] = bits
        cb = padded.reshape(CBZ, C)
        cbCRC = np.zeros((CBZ + 24, C), dtype=np.float64)
        for i in range(C):
            cbCRC[:, i] = _crc24b_encode(cb[:, i])
    if F > 0:
        filler = -np.ones((F, C), dtype=np.float64)
        cbs = np.concatenate([cbCRC, filler], axis=0)
    else:
        cbs = cbCRC.copy()
    return {"cbs": cbs, "C": C, "K": K, "info": info}


def code_block_desegment(cbs, bgn, blk_len):
    """LDPC code block desegmentation and CRC decoding."""
    cbs = np.asarray(cbs, dtype=np.float64)
    if cbs.size == 0 or blk_len == 0:
        return {"blk": np.zeros(0, dtype=np.float64), "err": np.zeros(0, dtype=np.uint32)}
    info = _get_cbs_info(blk_len, bgn)
    C, F, K = info["C"], info["F"], info["K"]
    if cbs.ndim == 1:
        cbs = cbs.reshape(-1, 1)
    K_actual, C_actual = cbs.shape
    if C_actual != C:
        raise ValueError(f"Expected {C} code blocks, got {C_actual}")
    if K_actual != K:
        raise ValueError(f"Expected code block length {K}, got {K_actual}")
    cbi = cbs[: K - F, :]
    if C == 1:
        blk = cbi.reshape(-1)
        err = np.zeros(0, dtype=np.uint32)
    else:
        data_len = K - F - 24
        cb_data = np.zeros((data_len, C), dtype=np.float64)
        err = np.zeros(C, dtype=np.uint32)
        for i in range(C):
            data, error = _crc24b_decode(cbi[:, i])
            cb_data[:, i] = data
            err[i] = int(error)
        blk = cb_data.reshape(-1)
    blk = blk[:blk_len]
    return {"blk": blk, "err": err}


def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="NR LDPC Code Block Segmentation Tool")
    parser.add_argument("--mode", choices=["encode", "decode"], required=True)
    parser.add_argument("--bgn", type=int, choices=[1, 2], required=True)
    parser.add_argument("--bits", type=str)
    parser.add_argument("--cbs", type=str)
    parser.add_argument("--blk-len", type=int)
    args = parser.parse_args()

    if args.mode == "encode":
        if not args.bits:
            parser.error("--bits is required for encode mode")
        bits = np.array([int(b) for b in args.bits.split(",")], dtype=np.float64)
        result = code_block_segment(bits, args.bgn)
        cbs = result["cbs"]
        print(json.dumps({
            "mode": "encode", "bgn": args.bgn,
            "blk_len": len(bits),
            "C": result["C"], "K": result["K"],
            "cbs": cbs.tolist(),
            "info": result["info"],
        }, ensure_ascii=False))
    else:
        if not args.cbs or args.blk_len is None:
            parser.error("--cbs and --blk-len are required for decode mode")
        cbs = np.array(json.loads(args.cbs), dtype=np.float64)
        result = code_block_desegment(cbs, args.bgn, args.blk_len)
        print(json.dumps({
            "mode": "decode", "bgn": args.bgn,
            "blk_len": args.blk_len,
            "blk": result["blk"].tolist(),
            "crc_errors": result["err"].tolist(),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
