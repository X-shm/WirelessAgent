"""nr_pbch_ref - 5G NR PBCH 参考信号和索引工具。

包含：
  - PBCH DM-RS 序列生成 (nrPBCHDMRS)
  - PBCH DM-RS 资源元素索引 (nrPBCHDMRSIndices)
  - PBCH 资源元素索引 (nrPBCHIndices)

对应 MATLAB 5G Toolbox nrPBCHDMRS、nrPBCHDMRSIndices、nrPBCHIndices。
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


def pbch_dmrs(ncellid: int, ibar_ssb: int) -> np.ndarray:
    """Generate PBCH DM-RS sequence (TS 38.211 Section 7.4.1.4.1).

    Args:
        ncellid: Physical cell identity (0..1007)
        ibar_ssb: Time-dependent part of DM-RS scrambling (0..7)

    Returns:
        Complex QPSK symbols, length 144
    """
    if ncellid < 0 or ncellid > 1007:
        raise ValueError(f"ncellid must be 0..1007, got {ncellid}")
    if ibar_ssb < 0 or ibar_ssb > 7:
        raise ValueError(f"ibar_ssb must be 0..7, got {ibar_ssb}")

    cinit = (2**11 * (ibar_ssb + 1) * (ncellid // 4 + 1) +
             2**6 * (ibar_ssb + 1) + ncellid % 4)

    prbs_seq = prbs(cinit, 2 * 144, mapping="binary")
    return modulate(prbs_seq, "QPSK")


def pbch_dmrs_indices(ncellid: int) -> np.ndarray:
    """Calculate PBCH DM-RS resource element indices (TS 38.211 Section 7.4.3.1).

    Args:
        ncellid: Physical cell identity (0..1007)

    Returns:
        Linear indices (0-based) into [240, 4] resource grid
    """
    if ncellid < 0 or ncellid > 1007:
        raise ValueError(f"ncellid must be 0..1007, got {ncellid}")

    K = 240
    v = ncellid % 4

    ind = (np.concatenate([
        np.arange(v + 1*K, v + 1*K + 237, 4),     # l=1
        np.arange(v + 2*K, v + 2*K + 45, 4),      # l=2 (first part)
        np.arange(v + 2*K + 192, v + 2*K + 237, 4),  # l=2 (second part)
        np.arange(v + 3*K, v + 3*K + 237, 4),     # l=3
    ])).astype(int)

    return ind


def pbch_indices(ncellid: int) -> tuple[np.ndarray, dict]:
    """Calculate PBCH resource element indices (TS 38.211 Section 7.4.3.1).

    Args:
        ncellid: Physical cell identity (0..1007)

    Returns:
        indices: Linear indices (0-based) into [240, 4] resource grid
        info: Dict with G (data bits) and Gd (data symbols)
    """
    if ncellid < 0 or ncellid > 1007:
        raise ValueError(f"ncellid must be 0..1007, got {ncellid}")

    K = 240
    v = ncellid % 4

    # DMRS indices for v=0
    dmrs_ind0 = np.concatenate([
        np.arange(1*K, 1*K + 237, 4),
        np.arange(2*K, 2*K + 45, 4),
        np.arange(2*K + 192, 2*K + 237, 4),
        np.arange(3*K, 3*K + 237, 4),
    ])

    # Non-DMRS positions within groups of 4
    not_dmrs = np.array([
        [1, 2, 3],  # v=0
        [0, 2, 3],  # v=1
        [0, 1, 3],  # v=2
        [0, 1, 2],  # v=3
    ]).T

    ind = (dmrs_ind0 + not_dmrs[:, v]).astype(int)

    info = {"G": len(ind) * 2, "Gd": len(ind)}

    return ind, info


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NR PBCH Reference — PBCH DM-RS 序列和索引"
    )

    parser.add_argument("--mode", choices=["dmrs", "dmrs_indices", "pbch_indices"],
                        required=True, help="操作模式")

    parser.add_argument("--ncellid", type=int, required=True,
                        help="物理小区 ID (0..1007)")
    parser.add_argument("--ibar_ssb", type=int, default=0,
                        help="[dmrs] SS/PBCH 块索引相关值 (0..7)")

    args = parser.parse_args()

    try:
        if args.mode == "dmrs":
            sym = pbch_dmrs(args.ncellid, args.ibar_ssb)
            result = {
                "symbols_real": sym.real.tolist(),
                "symbols_imag": sym.imag.tolist(),
                "n_symbols": len(sym),
            }
        elif args.mode == "dmrs_indices":
            ind = pbch_dmrs_indices(args.ncellid)
            result = {
                "indices": ind.tolist(),
                "n_indices": len(ind),
            }
        else:
            ind, info = pbch_indices(args.ncellid)
            result = {
                "indices": ind.tolist(),
                "n_indices": len(ind),
                "info": info,
            }

        print(json.dumps(result))

    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
