"""nr_pusch_ref - 5G NR PUSCH 参考信号和索引工具。

包含：
  - PUSCH DM-RS 序列生成 (nrPUSCHDMRS)
  - PUSCH DM-RS 资源元素索引 (nrPUSCHDMRSIndices)
  - PUSCH 资源元素索引 (nrPUSCHIndices)

对应 MATLAB 5G Toolbox nrPUSCHDMRS、nrPUSCHDMRSIndices、nrPUSCHIndices。
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


def pusch_dmrs(ncellid: int, nslot: int, symbol_start: int,
               num_symbols: int, num_ports: int = 1,
               ktc: int = 2) -> np.ndarray:
    """Generate PUSCH DM-RS sequence (simplified, TS 38.211 Section 6.4.1.1.1).

    Args:
        ncellid: Physical cell identity (0..1007)
        nslot: Slot number
        symbol_start: First DM-RS symbol in slot
        num_symbols: Number of DM-RS symbols
        num_ports: Number of antenna ports
        ktc: Transmission comb (2 or 4)

    Returns:
        Complex DM-RS symbols [n_re, num_ports]
    """
    if ncellid < 0 or ncellid > 1007:
        raise ValueError(f"ncellid must be 0..1007, got {ncellid}")

    # Simplified: use Gold PRBS with cinit based on ncellid and slot
    cinit = (ncellid + nslot * 1009) % (2**31)

    # DM-RS length per symbol: depends on allocated bandwidth
    # Simplified: assume 1 RB = 12 subcarriers, comb every K_TC
    n_sc_per_sym = 12  # per RB
    n_re_per_sym = n_sc_per_sym // ktc

    all_sym = []
    for p in range(num_ports):
        # Each port gets a different cyclic shift
        port_cinit = (cinit + p * 2**17) % (2**31)
        seq = prbs(port_cinit, n_re_per_sym * num_symbols, mapping="binary")
        sym = modulate(seq, "QPSK")
        all_sym.append(sym)

    min_len = min(len(s) for s in all_sym)
    result = np.zeros((min_len, num_ports), dtype=complex)
    for p in range(num_ports):
        result[:, p] = all_sym[p][:min_len]

    return result


def pusch_dmrs_indices(n_rb: int, symbol_start: int, num_symbols: int,
                       ktc: int = 2, num_ports: int = 1) -> np.ndarray:
    """Calculate PUSCH DM-RS resource element indices.

    Args:
        n_rb: Number of allocated RBs
        symbol_start: First DM-RS symbol in slot
        num_symbols: Number of DM-RS symbols
        ktc: Transmission comb (2 or 4)
        num_ports: Number of antenna ports

    Returns:
        Linear indices (0-based) into resource grid
    """
    n_sc = n_rb * 12
    n_sym = 14

    indices = []
    for p in range(num_ports):
        port_offset = p * (ktc // max(1, num_ports))
        for sym_offset in range(num_symbols):
            sym = symbol_start + sym_offset
            if sym >= n_sym:
                break
            for k in range(n_sc // ktc):
                sc = port_offset + k * ktc
                if sc >= n_sc:
                    break
                idx = sc + sym * n_sc
                indices.append(idx)

    return np.array(indices, dtype=int)


def pusch_indices(n_rb: int, symbol_start: int, num_symbols: int,
                  nslot: int = 0) -> tuple[np.ndarray, dict]:
    """Calculate PUSCH resource element indices.

    Args:
        n_rb: Number of allocated RBs
        symbol_start: First PUSCH symbol in slot
        num_symbols: Number of PUSCH symbols
        nslot: Slot number

    Returns:
        indices: Linear indices (0-based)
        info: Dict with allocation info
    """
    n_sc = n_rb * 12
    n_sym = 14

    indices = []
    for sym_offset in range(num_symbols):
        sym = symbol_start + sym_offset
        if sym >= n_sym:
            break
        for sc in range(n_sc):
            idx = sc + sym * n_sc
            indices.append(idx)

    info = {"n_rb": n_rb, "symbol_start": symbol_start,
            "num_symbols": num_symbols, "nslot": nslot}

    return np.array(indices, dtype=int), info


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NR PUSCH Reference — PUSCH DM-RS 序列和索引"
    )

    parser.add_argument("--mode", choices=["dmrs", "dmrs_indices", "pusch_indices"],
                        required=True, help="操作模式")

    parser.add_argument("--ncellid", type=int, default=0,
                        help="物理小区 ID (0..1007)")
    parser.add_argument("--nslot", type=int, default=0,
                        help="时隙号")
    parser.add_argument("--symbol_start", type=int, default=0,
                        help="起始符号位置")
    parser.add_argument("--num_symbols", type=int, default=1,
                        help="符号数量")
    parser.add_argument("--n_rb", type=int, default=1,
                        help="分配的 RB 数量")
    parser.add_argument("--num_ports", type=int, default=1,
                        help="天线端口数")
    parser.add_argument("--ktc", type=int, default=2,
                        help="传输梳齿数 (2 或 4)")

    args = parser.parse_args()

    try:
        if args.mode == "dmrs":
            sym = pusch_dmrs(args.ncellid, args.nslot, args.symbol_start,
                            args.num_symbols, args.num_ports, args.ktc)
            result = {
                "symbols_real": sym.real.tolist(),
                "symbols_imag": sym.imag.tolist(),
                "n_re": sym.shape[0],
                "n_ports": sym.shape[1],
            }
        elif args.mode == "dmrs_indices":
            ind = pusch_dmrs_indices(args.n_rb, args.symbol_start,
                                   args.num_symbols, args.ktc, args.num_ports)
            result = {"indices": ind.tolist(), "n_indices": len(ind)}
        else:
            ind, info = pusch_indices(args.n_rb, args.symbol_start,
                                     args.num_symbols, args.nslot)
            result = {"indices": ind.tolist(), "n_indices": len(ind), "info": info}

        print(json.dumps(result))

    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
