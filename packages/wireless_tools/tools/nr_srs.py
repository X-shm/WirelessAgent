"""nr_srs - 5G NR Sounding Reference Signal (SRS) 序列和索引生成。

Implements TS 38.211 Section 6.4.1.4 SRS processing.
MATLAB equivalent: nrSRS(...) and nrSRSIndices(...)

SRS 序列基于 Zadoff-Chu 序列，支持：
  - 循环移位 (cyclic shift)
  - 梳状传输 (comb pattern, K_TC = 2/4/8)
  - 多端口 TDM 复用
"""
from __future__ import annotations

import argparse
import json
import sys
import os
import math

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zadoff_chu_seq import zadoff_chu_seq


# TS 38.211 Table 6.4.1.4.3-1: SRS bandwidth configuration (simplified)
# Maps C_SRS to m_SRS (SRS sequence length in units of 4 RBs)
SRS_M_SRS = [4, 8, 12, 16, 16, 20, 24, 24, 28, 32, 36, 40, 48, 48, 52, 56,
              60, 64, 72, 76, 80, 88, 96, 104, 112, 120, 128, 136, 144, 152,
              160, 168, 176, 184, 192, 200, 208, 216, 224, 240, 256, 272, 288,
              304, 320, 336, 352, 368, 384, 400, 416, 432, 448, 464, 480, 496,
              512, 528, 544, 560, 576, 592, 608, 624]


def _get_srs_length(csrs: int) -> int:
    """Get SRS sequence length m_SRS from bandwidth config index."""
    if 0 <= csrs < len(SRS_M_SRS):
        return SRS_M_SRS[csrs]
    return 4 + csrs  # Fallback


def _get_ncs_max(ktc: int) -> int:
    """Get max number of cyclic shifts N_CS_max."""
    if ktc == 8:
        return 6
    elif ktc == 4:
        return 12
    elif ktc == 2:
        return 8
    return 12


def srs_sequence(seq_length: int, alpha: float, root: int = 0) -> np.ndarray:
    """Generate SRS sequence using Zadoff-Chu with cyclic shift.

    Args:
        seq_length: Length of SRS sequence
        alpha: Cyclic shift value (fractional, 0..1)
        root: Zadoff-Chu root index (0 = auto-select)

    Returns:
        Complex SRS sequence
    """
    if seq_length <= 0:
        raise ValueError(f"seq_length must be positive, got {seq_length}")

    # For even lengths, use nearest odd for ZC then truncate
    zc_length = seq_length if seq_length % 2 == 1 else seq_length + 1

    if root == 0:
        root = seq_length - 1 if seq_length > 1 else 1

    base_seq = zadoff_chu_seq(root, zc_length)[:seq_length]

    # Apply cyclic shift
    n = np.arange(seq_length, dtype=float)
    shift = np.exp(2j * np.pi * alpha * n / seq_length)
    return base_seq * shift


def srs_indices(csrs: int, ktc: int, symbol_start: int,
                num_symbols: int, n_rb: int, port: int = 0) -> np.ndarray:
    """Calculate SRS resource element indices for one port.

    Args:
        csrs: SRS bandwidth config index C_SRS (0..63)
        ktc: Transmission comb number (2, 4, 8)
        symbol_start: First SRS symbol in slot (0..13)
        num_symbols: Number of SRS OFDM symbols
        n_rb: Number of RBs in carrier grid
        port: Antenna port number (0-based)

    Returns:
        Linear indices (0-based) into resource grid
    """
    n_sc = n_rb * 12
    n_sym = 14

    m_srs = _get_srs_length(csrs)
    # SRS subcarriers: m_srs * 12 / ktc
    srs_sc = m_srs * 12 // ktc

    indices = []
    for sym_offset in range(num_symbols):
        sym = symbol_start + sym_offset
        if sym >= n_sym:
            break

        # Comb offset for this port
        comb_offset = port * (ktc // max(1, 1))

        for k in range(srs_sc):
            sc = comb_offset + k * ktc
            if sc >= n_sc:
                break
            idx = sc + sym * n_sc
            indices.append(idx)

    return np.array(indices, dtype=int)


def nr_srs(csrs: int, ktc: int, symbol_start: int,
           num_symbols: int, n_rb: int, num_ports: int = 1,
           cyclic_shift: int = 0, n_srs_id: int = 0) -> tuple[np.ndarray, dict]:
    """Generate SRS symbols and info.

    Args:
        csrs: SRS bandwidth config index C_SRS (0..63)
        ktc: Transmission comb number (2, 4, 8)
        symbol_start: First SRS symbol in slot (0..13)
        num_symbols: Number of SRS OFDM symbols (1, 2, 4)
        n_rb: Number of RBs in carrier grid
        num_ports: Number of SRS antenna ports (1, 2, 4)
        cyclic_shift: Cyclic shift number (0..N_CS_max-1)
        n_srs_id: SRS scrambling identity (0..65535)

    Returns:
        sym: SRS symbols [n_re, num_ports]
        info: Dict with sequence parameters
    """
    n_cs_max = _get_ncs_max(ktc)
    if cyclic_shift < 0 or cyclic_shift >= n_cs_max:
        raise ValueError(f"cyclic_shift must be 0..{n_cs_max-1}, got {cyclic_shift}")

    m_srs = _get_srs_length(csrs)
    zc_length = m_srs * 12 // ktc

    all_sym = []
    for p in range(num_ports):
        alpha = (cyclic_shift + p * (n_cs_max // max(1, num_ports))) % n_cs_max
        alpha_frac = alpha / n_cs_max

        seq = srs_sequence(zc_length, alpha_frac, root=zc_length - 1 if zc_length > 1 else 1)

        port_sym = []
        for sym_offset in range(num_symbols):
            port_sym.extend(seq)

        all_sym.append(np.array(port_sym))

    min_len = min(len(s) for s in all_sym)
    sym = np.zeros((min_len, num_ports), dtype=complex)
    for p in range(num_ports):
        sym[:, p] = all_sym[p][:min_len]

    info = {
        "m_srs": m_srs,
        "zc_length": zc_length,
        "n_cs_max": n_cs_max,
        "alpha_per_port": [(cyclic_shift + p * (n_cs_max // max(1, num_ports))) % n_cs_max for p in range(num_ports)],
    }

    return sym, info


def nr_srs_indices(csrs: int, ktc: int, symbol_start: int,
                   num_symbols: int, n_rb: int, num_ports: int = 1) -> tuple[np.ndarray, dict]:
    """Calculate SRS resource element indices.

    Args:
        csrs: SRS bandwidth config index C_SRS (0..63)
        ktc: Transmission comb number (2, 4, 8)
        symbol_start: First SRS symbol in slot (0..13)
        num_symbols: Number of SRS OFDM symbols
        n_rb: Number of RBs in carrier grid
        num_ports: Number of SRS antenna ports

    Returns:
        indices: Linear indices [n_re, num_ports] (0-based)
        info: Dict with index parameters
    """
    indices = []
    for p in range(num_ports):
        port_ind = srs_indices(csrs, ktc, symbol_start, num_symbols, n_rb, port=p)
        indices.append(port_ind)

    min_len = min(len(ind) for ind in indices)
    ind_matrix = np.zeros((min_len, num_ports), dtype=int)
    for p in range(num_ports):
        ind_matrix[:, p] = indices[p][:min_len]

    info = {
        "m_srs": _get_srs_length(csrs),
        "ktc": ktc,
        "symbol_start": symbol_start,
        "num_symbols": num_symbols,
        "n_rb": n_rb,
    }

    return ind_matrix, info


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NR SRS — 5G NR Sounding Reference Signal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  # 生成 SRS 序列
  python tools/nr_srs.py --mode sequence --csrs 5 --ktc 2 \\
      --symbol_start 8 --num_symbols 4 --n_rb 52 --num_ports 2

  # 生成 SRS 索引
  python tools/nr_srs.py --mode indices --csrs 5 --ktc 2 \\
      --symbol_start 8 --num_symbols 4 --n_rb 52 --num_ports 2
""",
    )

    parser.add_argument("--mode", choices=["sequence", "indices"], required=True,
                        help="操作模式：sequence（生成序列）或 indices（计算索引）")

    # 公共参数
    parser.add_argument("--csrs", type=int, default=5,
                        help="SRS 带宽配置索引 C_SRS (0..63)，默认 5")
    parser.add_argument("--ktc", type=int, default=2,
                        help="传输梳齿数 K_TC (2, 4, 8)，默认 2")
    parser.add_argument("--symbol_start", type=int, default=8,
                        help="SRS 起始符号位置 (0..13)，默认 8")
    parser.add_argument("--num_symbols", type=int, default=4,
                        help="SRS OFDM 符号数 (1, 2, 4)，默认 4")
    parser.add_argument("--n_rb", type=int, default=52,
                        help="载波 RB 数，默认 52")
    parser.add_argument("--num_ports", type=int, default=1,
                        help="SRS 天线端口数 (1, 2, 4)，默认 1")

    # 序列参数
    parser.add_argument("--cyclic_shift", type=int, default=0,
                        help="[序列] 循环移位号 (0..N_CS_max-1)，默认 0")
    parser.add_argument("--n_srs_id", type=int, default=0,
                        help="[序列] SRS 加扰身份 (0..65535)，默认 0")

    args = parser.parse_args()

    try:
        if args.mode == "sequence":
            sym, info = nr_srs(
                args.csrs, args.ktc, args.symbol_start,
                args.num_symbols, args.n_rb, args.num_ports,
                args.cyclic_shift, args.n_srs_id
            )
            result = {
                "symbols_real": sym.real.tolist(),
                "symbols_imag": sym.imag.tolist(),
                "n_re": sym.shape[0],
                "n_ports": sym.shape[1],
                "info": info,
            }
        else:  # indices
            ind, info = nr_srs_indices(
                args.csrs, args.ktc, args.symbol_start,
                args.num_symbols, args.n_rb, args.num_ports
            )
            result = {
                "indices": ind.tolist(),
                "n_re": ind.shape[0],
                "n_ports": ind.shape[1],
                "info": info,
            }

        print(json.dumps(result))

    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
