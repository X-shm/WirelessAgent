"""wlan_constellation - IEEE 802.11 星座映射/解映射工具。

Implements IEEE 802.11 constellation mapping/demapping.
MATLAB equivalent: wlanConstellationMap / wlanConstellationDemap

支持调制 (numBPSCS = 每子载波每空间流编码比特数):
  1=BPSK, 2=QPSK, 4=16QAM, 6=64QAM, 8=256QAM, 10=1024QAM, 12=4096QAM

映射方向：比特 → 复符号（IEEE 802.11 Gray 映射）
解映射方向：复符号 → 硬判决比特 或 近似 LLR 软比特
可选相位旋转（map 逆时针 / demap 顺时针）。
"""
from __future__ import annotations

import argparse
import json
import sys
import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _complex_io import parse_complex

# IEEE 802.11 Gray 映射表（索引 = 比特模式整数值，值 = 星座符号位置 k）
_QPSK_MAP = [1, 0, 3, 2]

_16QAM_MAP = [2, 3, 1, 0, 6, 7, 5, 4, 14, 15, 13, 12, 10, 11, 9, 8]

_64QAM_MAP = [
    4, 5, 7, 6, 2, 3, 1, 0, 12, 13, 15, 14, 10, 11, 9, 8,
    28, 29, 31, 30, 26, 27, 25, 24, 20, 21, 23, 22, 18, 19, 17, 16,
    52, 53, 55, 54, 50, 51, 49, 48, 60, 61, 63, 62, 58, 59, 57, 56,
    44, 45, 47, 46, 42, 43, 41, 40, 36, 37, 39, 38, 34, 35, 33, 32,
]


def _256qam_map() -> list[int]:
    first_col = [8, 9, 11, 10, 14, 15, 13, 12, 4, 5, 7, 6, 2, 3, 1, 0]
    offsets = [0, 16, 48, 32, 96, 112, 80, 64, 192, 208, 240, 224, 160, 176, 144, 128]
    return [fc + off for off in offsets for fc in first_col]


def _1024qam_map() -> list[int]:
    first_col = [16, 17, 19, 18, 22, 23, 21, 20, 28, 29, 31, 30, 26, 27, 25, 24,
                 8, 9, 11, 10, 14, 15, 13, 12, 4, 5, 7, 6, 2, 3, 1, 0]
    offsets = [0, 32, 96, 64, 192, 224, 160, 128,
               384, 416, 480, 448, 320, 352, 288, 256,
               768, 800, 864, 832, 960, 992, 928, 896,
               640, 672, 736, 704, 576, 608, 544, 512]
    return [fc + off for off in offsets for fc in first_col]


def _4096qam_map() -> list[int]:
    first_col = [32, 33, 35, 34, 38, 39, 37, 36, 44, 45, 47, 46, 42, 43, 41, 40,
                 56, 57, 59, 58, 62, 63, 61, 60, 52, 53, 55, 54, 50, 51, 49, 48,
                 16, 17, 19, 18, 22, 23, 21, 20, 28, 29, 31, 30, 26, 27, 25, 24,
                 8, 9, 11, 10, 14, 15, 13, 12, 4, 5, 7, 6, 2, 3, 1, 0]
    offsets = [0, 64, 192, 128, 384, 448, 320, 256,
               768, 832, 960, 896, 640, 704, 576, 512,
               1536, 1600, 1728, 1664, 1920, 1984, 1856, 1792,
               1280, 1344, 1472, 1408, 1152, 1216, 1088, 1024,
               3072, 3136, 3264, 3200, 3456, 3520, 3392, 3328,
               3840, 3904, 4032, 3968, 3712, 3776, 3648, 3584,
               2560, 2624, 2752, 2688, 2944, 3008, 2880, 2816,
               2304, 2368, 2496, 2432, 2176, 2240, 2112, 2048]
    return [fc + off for off in offsets for fc in first_col]


_SYM_MAPS = {
    2: _QPSK_MAP,
    4: _16QAM_MAP,
    6: _64QAM_MAP,
    8: _256qam_map(),
    10: _1024qam_map(),
    12: _4096qam_map(),
}

VALID_BPSCS = [1, 2, 4, 6, 8, 10, 12]


def _check_bpscs(num_bpscs: int) -> None:
    if num_bpscs not in VALID_BPSCS:
        raise ValueError(f"numBPSCS must be one of {VALID_BPSCS}, got {num_bpscs}")


def constellation_map(bits: np.ndarray, num_bpscs: int,
                      phase: float | None = None) -> np.ndarray:
    """Map bits to WLAN constellation symbols.

    Args:
        bits: binary bits (0/1), length must be a multiple of num_bpscs
        num_bpscs: coded bits per subcarrier per spatial stream
        phase: optional counter-clockwise rotation in radians

    Returns:
        Complex symbols, length = len(bits) / num_bpscs
    """
    _check_bpscs(num_bpscs)
    bits = np.asarray(bits, dtype=np.int8).reshape(-1)
    if len(bits) % num_bpscs != 0:
        raise ValueError(f"bits length {len(bits)} not a multiple of numBPSCS {num_bpscs}")

    if num_bpscs == 1:
        # IEEE 802.11: bit 0 -> -1, bit 1 -> +1
        sym = np.where(bits == 0, -1.0, 1.0).astype(complex)
    else:
        m = 2 ** num_bpscs
        sq_m = int(np.sqrt(m))
        sym_tab = np.array(_SYM_MAPS[num_bpscs])

        bits_mat = bits.reshape(-1, num_bpscs)
        powers = 2 ** np.arange(num_bpscs - 1, -1, -1)
        indices = bits_mat @ powers

        k = sym_tab[indices]
        i_pos = 2 * (k % sq_m) - sq_m + 1
        q_pos = 2 * (k // sq_m) - sq_m + 1
        scale = 1.0 / np.sqrt(2.0 * (m - 1) / 3.0)
        sym = (i_pos + 1j * q_pos).astype(complex) * scale

    if phase is not None:
        sym = sym * np.exp(1j * phase)
    return sym


def _build_constellation(num_bpscs: int) -> np.ndarray:
    """Build constellation point array indexed by symbol position k."""
    m = 2 ** num_bpscs
    sq_m = int(np.sqrt(m))
    scale = 1.0 / np.sqrt(2.0 * (m - 1) / 3.0)
    k = np.arange(m)
    i_pos = 2 * (k % sq_m) - sq_m + 1
    q_pos = 2 * (k // sq_m) - sq_m + 1
    return (i_pos + 1j * q_pos).astype(complex) * scale


def constellation_demap(symbols: np.ndarray, noise_var: float, num_bpscs: int,
                        demap_type: str = "soft",
                        phase: float | None = None) -> np.ndarray:
    """Demap received symbols to bits (hard) or approximate LLRs (soft).

    Args:
        symbols: received complex symbols
        noise_var: noise variance (soft demapping)
        num_bpscs: coded bits per subcarrier per spatial stream
        demap_type: 'hard' or 'soft'
        phase: optional clockwise derotation in radians

    Returns:
        bits (hard) or LLRs (soft), length = len(symbols) * num_bpscs
    """
    _check_bpscs(num_bpscs)
    if demap_type not in ("hard", "soft"):
        raise ValueError(f"demap_type must be 'hard' or 'soft', got {demap_type}")

    symbols = np.asarray(symbols, dtype=complex).reshape(-1)
    if phase is not None:
        symbols = symbols * np.exp(-1j * phase)

    if num_bpscs == 1:
        if demap_type == "hard":
            return (symbols.real >= 0).astype(np.int8)
        return 2.0 * symbols.real / max(noise_var, 1e-30)

    m = 2 ** num_bpscs
    sym_tab = np.array(_SYM_MAPS[num_bpscs])
    constellation = _build_constellation(num_bpscs)

    diffs = symbols[:, None] - constellation[None, :]
    dist2 = np.abs(diffs) ** 2

    # inverse table: symbol position k -> bit pattern integer
    inv = np.zeros(m, dtype=np.int64)
    for bits_int, k in enumerate(sym_tab):
        inv[k] = bits_int
    powers = 2 ** np.arange(num_bpscs - 1, -1, -1)
    point_bits = ((inv[:, None] // powers) % 2)  # [M, numBPSCS]

    if demap_type == "hard":
        nearest = np.argmin(dist2, axis=1)
        bits_ints = inv[nearest]
        bits = ((bits_ints[:, None] // powers) % 2).astype(np.int8)
        return bits.reshape(-1)

    # soft: max-log-MAP approximate LLR
    scale = 1.0 / max(noise_var, 1e-30)
    llrs = np.zeros((len(symbols), num_bpscs))
    for b in range(num_bpscs):
        mask0 = point_bits[:, b] == 0
        min0 = dist2[:, mask0].min(axis=1)
        min1 = dist2[:, ~mask0].min(axis=1)
        llrs[:, b] = (min1 - min0) * scale
    return llrs.reshape(-1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WLAN Constellation — IEEE 802.11 星座映射/解映射"
    )
    parser.add_argument("--mode", choices=["map", "demap"], required=True,
                        help="map: 比特→符号; demap: 符号→比特/LLR")
    parser.add_argument("--num_bpscs", type=int, required=True,
                        help="每子载波每空间流编码比特数 (1/2/4/6/8/10/12)")
    parser.add_argument("--bits", help="[map] 逗号分隔的比特串，如 1,0,1,1")
    parser.add_argument("--symbols", help='[demap] 复符号 JSON')
    parser.add_argument("--noise_var", type=float, default=1.0,
                        help="[demap soft] 噪声方差")
    parser.add_argument("--demap_type", choices=["hard", "soft"], default="soft",
                        help="[demap] 判决类型")
    parser.add_argument("--phase", type=float, default=None,
                        help="相位旋转（弧度）：map 逆时针 / demap 顺时针")
    args = parser.parse_args()

    try:
        if args.mode == "map":
            if args.bits is None:
                raise ValueError("map 模式需要 --bits")
            bits = np.array([int(b) for b in args.bits.split(",")], dtype=np.int8)
            sym = constellation_map(bits, args.num_bpscs, args.phase)
            result = {
                "symbols_real": sym.real.tolist(),
                "symbols_imag": sym.imag.tolist(),
                "n_symbols": len(sym),
                "num_bpscs": args.num_bpscs,
            }
        else:
            if args.symbols is None:
                raise ValueError("demap 模式需要 --symbols")
            syms = parse_complex(args.symbols)
            out = constellation_demap(syms, args.noise_var, args.num_bpscs,
                                      args.demap_type, args.phase)
            key = "bits" if args.demap_type == "hard" else "llr"
            result = {
                key: out.tolist(),
                "n_out": len(out),
                "num_bpscs": args.num_bpscs,
                "demap_type": args.demap_type,
            }
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
