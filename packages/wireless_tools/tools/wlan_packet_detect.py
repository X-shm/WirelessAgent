"""wlan_packet_detect - IEEE 802.11 OFDM 包检测工具。

Implements OFDM packet detection using L-STF autocorrelation.
MATLAB equivalent: wlanPacketDetect(x, chanbw, offset, threshold)

算法（Schmidl & Cox / Heiskala 自相关法）：
  1. 滑动自相关 C(n) = Σ conj(x(k))·x(k+L)，L = 短训练符号长度
  2. 滑动功率 P(n) = Σ (|x(k)|² + |x(k+L)|²)/2
  3. 判决统计量 Mn(n) = |C(n)|² / P(n)²
  4. Mn 超过门限并持续 ≥ 1.5L 个采样 → 检测到包前导
  5. 返回包起始偏移（相对输入起点）

输入波形：Ns×Nr（Ns 采样数，Nr 接收天线），L-STF 短训练符号
在 20MHz 下 L=16 采样（0.8us @ 20MHz），10 个符号共 160 采样。
"""
from __future__ import annotations

import argparse
import json
import sys
import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _complex_io import parse_complex

# 信道带宽 → 20MHz 子信道数
_CBW_NSC = {
    "CBW5": 1, "CBW10": 1, "CBW20": 1,
    "CBW40": 2, "CBW80": 4, "CBW160": 8, "CBW320": 16,
}


def packet_detect(waveform: np.ndarray, chanbw: str = "CBW20",
                  offset: int = 0, threshold: float = 0.5) -> tuple[int | None, np.ndarray]:
    """Detect OFDM packet preamble start using L-STF autocorrelation.

    Args:
        waveform: received waveform [Ns] or [Ns, Nr]
        chanbw: channel bandwidth string
        offset: start processing offset (samples)
        threshold: decision threshold (0, 1]

    Returns:
        (start_offset, decision_stats):
        start_offset — samples from input start to detected preamble
                       (None if no packet); relative to `offset` if given
        decision_stats — Mn decision statistic curve
    """
    if chanbw not in _CBW_NSC:
        raise ValueError(f"chanbw must be one of {list(_CBW_NSC)}, got {chanbw}")
    if not 0 < threshold <= 1:
        raise ValueError(f"threshold must be in (0, 1], got {threshold}")

    x = np.asarray(waveform, dtype=complex)
    if x.ndim == 1:
        x = x[:, None]
    if x.ndim != 2:
        raise ValueError(f"waveform must be 1-D or 2-D, got {x.ndim}-D")
    if offset < 0 or offset >= len(x):
        raise ValueError(f"offset must be in [0, {len(x)-1}], got {offset}")

    nsc = _CBW_NSC[chanbw]
    # Short training symbol: 0.8 us at 20 MHz per subchannel
    symbol_length = int(round(0.8e-6 * nsc * 20e6))
    lstf_len = symbol_length * 10

    x = x[offset:]
    n_samples = len(x)
    if n_samples < 2 * symbol_length:
        return None, np.array([])

    # Sliding autocorrelation with delay L across antennas
    rx = x[:-symbol_length]                       # undelayed
    rxd = x[symbol_length:]                       # delayed by L
    corr = np.sum(rx.conj() * rxd, axis=1)        # [N-L]
    power = np.sum((np.abs(rx) ** 2 + np.abs(rxd) ** 2) / 2.0, axis=1)

    # Sliding window sums over L samples (moving average)
    window = np.ones(symbol_length)
    kernel = window / symbol_length
    c_s = np.convolve(corr, kernel, mode="valid")     # [N-2L+1]
    p_s = np.convolve(power, kernel, mode="valid") + np.finfo(float).eps

    mn = np.abs(c_s) ** 2 / p_s ** 2

    # Detection: Mn above threshold sustained for >= 1.5*L samples
    run_required = int(np.ceil(1.5 * symbol_length))
    above = mn > threshold

    start_offset = None
    run = 0
    for i, ok in enumerate(above):
        if ok:
            run += 1
            if run >= run_required:
                start_offset = i - run + 1
                break
        else:
            run = 0

    return start_offset, mn


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WLAN Packet Detect — 802.11 OFDM 包检测（L-STF 自相关）"
    )
    parser.add_argument("--waveform", required=True,
                        help='接收波形 JSON：{"real":[...],"imag":[...]} 或复数数组')
    parser.add_argument("--chanbw", default="CBW20",
                        choices=list(_CBW_NSC), help="信道带宽（默认 CBW20）")
    parser.add_argument("--offset", type=int, default=0,
                        help="起始处理偏移（采样数），默认 0")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="检测门限 (0,1]，默认 0.5")
    parser.add_argument("--max_stats", type=int, default=0,
                        help="输出判决统计曲线的最大长度（0=全部）")
    args = parser.parse_args()

    try:
        x = parse_complex(args.waveform)
        start, mn = packet_detect(x, args.chanbw, args.offset, args.threshold)
        stats = mn.tolist()
        if args.max_stats and args.max_stats > 0:
            stats = stats[: args.max_stats]
        result = {
            "start_offset": start,
            "detected": start is not None,
            "n_stats": len(mn),
            "decision_stats": stats,
            "symbol_length": int(round(0.8e-6 * _CBW_NSC[args.chanbw] * 20e6)),
        }
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
