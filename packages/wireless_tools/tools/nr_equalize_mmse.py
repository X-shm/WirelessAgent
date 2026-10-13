"""
NR MMSE Equalizer — 5G NR 接收机 MMSE 均衡器。

对应 MATLAB 5G Toolbox 中的 nrEqualizeMMSE(rxSym, hest, nVar)。

对每个资源元素（RE）独立执行 MMSE 均衡：
    W = (H^H H + nVar * I)^(-1) H^H        # P x R 权值矩阵
    out[k, :] = W @ y                       # P 个均衡后符号
    csi[k, p] = 1 / P_mmse[p, p].real       # 第 p 层等效 SINR
其中 P_mmse = nVar * (H^H H + nVar * I)^(-1) 是 MMSE 估计误差协方差。

输入:
    rx_sym: [NRE, R]  接收符号（R = 接收天线数）
    hest:   [NRE, R, P]  信道估计（P = 层数 / 发射端层数）
    nvar:   标量，噪声方差

输出:
    eq_symbols: [NRE, P]  均衡后符号
    csi:        [NRE, P]  软信道状态信息（等效 SINR，越大越好）
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np


def _parse_complex_2d(text: str) -> np.ndarray:
    """从 JSON 解析 2D 复数数组，格式: {"real": [[...], ...], "imag": [[...], ...]}"""
    obj = json.loads(text)
    real = np.asarray(obj["real"], dtype=np.float64)
    imag = np.asarray(obj.get("imag", np.zeros_like(real)), dtype=np.float64)
    if real.shape != imag.shape:
        raise ValueError("real and imag arrays must have the same shape")
    if real.ndim != 2:
        raise ValueError(f"expected 2D array, got shape {real.shape}")
    return real + 1j * imag


def _parse_complex_3d(text: str) -> np.ndarray:
    """从 JSON 解析 3D 复数数组，格式: {"real": [[[...], ...], ...], "imag": ...}"""
    obj = json.loads(text)
    real = np.asarray(obj["real"], dtype=np.float64)
    imag = np.asarray(obj.get("imag", np.zeros_like(real)), dtype=np.float64)
    if real.shape != imag.shape:
        raise ValueError("real and imag arrays must have the same shape")
    if real.ndim != 3:
        raise ValueError(f"expected 3D array, got shape {real.shape}")
    return real + 1j * imag


def mmse_equalize(rx_sym: np.ndarray, hest: np.ndarray, nvar: float) -> tuple[np.ndarray, np.ndarray]:
    """MMSE 均衡核心函数。

    Args:
        rx_sym: 接收符号，形状 [NRE, R]
        hest: 信道估计，形状 [NRE, R, P]
        nvar: 噪声方差（标量）

    Returns:
        eq_symbols: 均衡后符号，形状 [NRE, P]
        csi: 软信道状态信息（等效 SINR），形状 [NRE, P]
    """
    rx_sym = np.asarray(rx_sym, dtype=np.complex128)
    hest = np.asarray(hest, dtype=np.complex128)
    nvar = float(nvar)

    if rx_sym.ndim != 2:
        raise ValueError(f"rx_sym must be 2D (NRE x R), got shape {rx_sym.shape}")
    if hest.ndim != 3:
        raise ValueError(f"hest must be 3D (NRE x R x P), got shape {hest.shape}")

    n_re, n_rx, n_layers = hest.shape
    if rx_sym.shape[0] != n_re:
        raise ValueError(
            f"rx_sym and hest must have same NRE dimension: "
            f"rx_sym {rx_sym.shape[0]} vs hest {n_re}"
        )
    if rx_sym.shape[1] != n_rx:
        raise ValueError(
            f"rx_sym and hest must have same R dimension: "
            f"rx_sym {rx_sym.shape[1]} vs hest {n_rx}"
        )
    if nvar < 0:
        raise ValueError("nvar must be non-negative")
    if nvar == 0:
        nvar = np.finfo(float).tiny

    eq_symbols = np.zeros((n_re, n_layers), dtype=np.complex128)
    csi = np.zeros((n_re, n_layers), dtype=np.float64)
    identity = np.eye(n_layers, dtype=np.complex128)

    for k in range(n_re):
        H = hest[k, :, :]          # R x P
        y = rx_sym[k, :]           # R,

        # A = H^H H + nVar * I  (P x P)
        A = H.conj().T @ H + nvar * identity

        # W = A^(-1) @ H^H  (P x R)
        # 使用 solve 比 inv 更数值稳定
        W = np.linalg.solve(A, H.conj().T)

        # 均衡输出
        eq_symbols[k, :] = W @ y

        # 误差协方差: P_mmse = nVar * A^(-1)
        # csi[k, p] = nVar / P_mmse[p, p].real
        # 与 MATLAB nrEqualizeMMSE 一致: CSI = diag(H^H H + nVar*I)
        a_inv = np.linalg.solve(A, identity)
        p_mmse_diag = nvar * np.real(np.diag(a_inv))
        csi[k, :] = nvar / np.maximum(p_mmse_diag, np.finfo(float).tiny)

    return eq_symbols, csi


def main() -> None:
    parser = argparse.ArgumentParser(
        description="5G NR MMSE 均衡器 — 对应 MATLAB nrEqualizeMMSE"
    )
    parser.add_argument(
        "--rx_sym", required=True,
        help='接收符号 JSON: {"real": [[...],...], "imag": [[...],...]}  (NRE x R)'
    )
    parser.add_argument(
        "--hest", required=True,
        help='信道估计 JSON: {"real": [[[...],...],...], "imag": [[[...],...],...]}  (NRE x R x P)'
    )
    parser.add_argument(
        "--nvar", type=float, required=True,
        help="噪声方差（标量）"
    )
    args = parser.parse_args()

    try:
        rx_sym = _parse_complex_2d(args.rx_sym)
        hest = _parse_complex_3d(args.hest)
        eq_symbols, csi = mmse_equalize(rx_sym, hest, args.nvar)

        n_re, n_layers = eq_symbols.shape
        result = {
            "eq_symbols_real": eq_symbols.real.tolist(),
            "eq_symbols_imag": eq_symbols.imag.tolist(),
            "csi": csi.tolist(),
            "n_re": n_re,
            "n_layers": n_layers,
        }
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, np.linalg.LinAlgError, json.JSONDecodeError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
