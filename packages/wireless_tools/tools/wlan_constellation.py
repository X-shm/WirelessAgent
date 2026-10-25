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

VALID_BPSCS = [1, 2, 4, 6, 8, 10, 12]


def _check_bpscs(num_bpscs: int) -> None:
    if num_bpscs not in VALID_BPSCS:
        raise ValueError(f"numBPSCS must be one of {VALID_BPSCS}, got {num_bpscs}")


def _qam_points_for_binary_indices(indices: np.ndarray, num_bpscs: int) -> np.ndarray:
    """IEEE WLAN mapping: each axis starts with a sign bit then Gray magnitude bits."""
    indices = np.asarray(indices, dtype=np.uint32).reshape(-1)
    if num_bpscs == 1:
        return np.where(indices == 0, -1.0, 1.0).astype(complex)
    axis_bits = num_bpscs // 2
    magnitude_bits = axis_bits - 1
    axis_values = []
    for shift in (axis_bits, 0):
        word = (indices >> shift) & ((1 << axis_bits) - 1)
        sign = np.where((word >> magnitude_bits) == 0, -1.0, 1.0)
        gray = word & ((1 << magnitude_bits) - 1)
        binary = gray.copy()
        offset = 1
        while offset < magnitude_bits:
            binary ^= binary >> offset
            offset *= 2
        magnitude = (1 << axis_bits) - 1 - 2 * binary.astype(int)
        axis_values.append(sign * magnitude)
    scale = 1.0 / np.sqrt(2.0 * (2 ** num_bpscs - 1) / 3.0)
    return (axis_values[0] + 1j * axis_values[1]) * scale


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

    if not np.all((bits == 0) | (bits == 1)):
        raise ValueError("bits must contain only 0 or 1")
    bits_mat = bits.reshape(-1, num_bpscs)
    powers = 2 ** np.arange(num_bpscs - 1, -1, -1)
    sym = _qam_points_for_binary_indices(bits_mat @ powers, num_bpscs)

    if phase is not None:
        sym = sym * np.exp(1j * phase)
    return sym


def _build_constellation(num_bpscs: int) -> np.ndarray:
    """Build constellation points indexed by the binary bit pattern."""
    m = 2 ** num_bpscs
    return _qam_points_for_binary_indices(np.arange(m), num_bpscs)


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
    constellation = _build_constellation(num_bpscs)

    diffs = symbols[:, None] - constellation[None, :]
    dist2 = np.abs(diffs) ** 2

    powers = 2 ** np.arange(num_bpscs - 1, -1, -1)
    point_bits = ((np.arange(m)[:, None] // powers) % 2)  # [M, numBPSCS]

    if demap_type == "hard":
        nearest = np.argmin(dist2, axis=1)
        bits = ((nearest[:, None] // powers) % 2).astype(np.int8)
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
