"""wlan_symbol_timing - IEEE 802.11 符号定时估计工具。

Implements fine symbol timing estimation using L-LTF cross-correlation.
MATLAB equivalent: wlanSymbolTimingEstimate(x, chanbw, threshold)

算法：
  1. 生成本地 L-LTF 时域波形（频域 52 tones，CP=32，2 个 OFDM 符号，共 160 采样）
  2. 与接收波形做互相关，跨接收天线累加功率 Metric(n) = Σ|corr(n)|²
  3. 取峰值位置 nInitial
  4. CSD 细化：在 [nInitial, nInitial+ΔCSD] 内取最后一个 ≥ threshold·Mmax 的位置
     ΔCSD = round(200ns · fs)（802.11n/ac 最大循环移位延迟）
  5. startOffset = nMax - L（相对输入起点的 L-STF 起始，0-based）

L-LTF 频率序列（IEEE 802.11-2012 Eq. 20-11）：52 个活动子载波，DC 为空。
"""
from __future__ import annotations

import argparse
import json
import sys
import os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _complex_io import parse_complex

# 信道带宽 → MHz
_CBW_MHZ = {
    "CBW5": 5, "CBW10": 10, "CBW20": 20, "CBW40": 40,
    "CBW80": 80, "CBW160": 160, "CBW320": 320,
}

# L-LTF 频率序列（IEEE 802.11-2012 Eq. 20-11）
_LLTF_LOWER = np.array(
    [1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, -1,
     -1, 1, 1, -1, 1, -1, 1, 1, 1, 1], dtype=float)
_LLTF_UPPER = np.array(
    [1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1,
     -1, -1, 1, -1, 1, -1, 1, 1, 1, 1], dtype=float)


def _subchannel_count(mhz: float) -> int:
    return int(mhz / 20) if mhz > 20 else 1


def _vht_carrier_rotations(n_subchannels: int) -> np.ndarray:
    """Apply 802.11-2016 VHT carrier rotation per 20MHz subchannel.

    gamma = [1 1i] for 40MHz, [1 -1 -1 -1] for 80MHz, etc.
    Returns a length-n_subchannels array of phase factors.
    """
    if n_subchannels == 1:
        return np.array([1])
    gammas = {
        2: [1, 1j],
        4: [1, -1, -1, -1],
        8: [1, -1, -1, -1, 1, -1, -1, -1],
        16: [1, -1, -1, -1, 1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1],
    }
    return np.array(gammas[n_subchannels])


def _lltf_spectrum(n_subchannels: int) -> np.ndarray:
    """Build the 64-point L-LTF frequency-domain symbol per 20MHz subchannel."""
    sym = np.concatenate([
        np.zeros(6), _LLTF_LOWER, np.zeros(1), _LLTF_UPPER, np.zeros(5)])
    return np.tile(sym, n_subchannels)


def lltf_waveform(chanbw: str = "CBW20") -> np.ndarray:
    """Generate the L-LTF time-domain waveform (2 OFDM symbols).

    L-LTF = [CP(32) + 64] + [64] = 160 samples per 20 MHz subchannel.

    Args:
        chanbw: channel bandwidth string

    Returns:
        Complex L-LTF waveform
    """
    if chanbw not in _CBW_MHZ:
        raise ValueError(f"chanbw must be one of {list(_CBW_MHZ)}, got {chanbw}")
    n_subch = _subchannel_count(_CBW_MHZ[chanbw])
    fft_len = 64 * n_subch

    spectrum = _lltf_spectrum(n_subch)
    # Apply carrier rotation per 20MHz subchannel (IEEE 802.11-2016)
    gamma = _vht_carrier_rotations(n_subch)
    spectrum = spectrum.reshape(n_subch, 64) * gamma[:, np.newaxis]
    spectrum = spectrum.flatten()
    n_tones = 52 * n_subch
    spectrum = spectrum / np.sqrt(n_tones)

    # Match MATLAB: ifftshift to center DC, then ifft + N/sqrt(num_tones) scaling
    td = np.fft.ifft(np.fft.ifftshift(spectrum)) * fft_len
    cp_len = fft_len // 2
    sym1 = np.concatenate([td[-cp_len:], td])
    return np.concatenate([sym1, td])


def symbol_timing_estimate(waveform: np.ndarray, chanbw: str = "CBW20",
                           threshold: float = 1.0) -> tuple[int | None, np.ndarray]:
    """Estimate L-STF start offset by cross-correlating with L-LTF.

    Args:
        waveform: received waveform [Ns] or [Ns, Nr]
        chanbw: channel bandwidth string
        threshold: decision threshold (0..1), default 1

    Returns:
        (start_offset, metric):
        start_offset — samples from input start to estimated L-STF start
                       (None if input shorter than L-LTF)
        metric — decision metric vector
    """
    if chanbw not in _CBW_MHZ:
        raise ValueError(f"chanbw must be one of {list(_CBW_MHZ)}, got {chanbw}")
    if not 0 <= threshold <= 1:
        raise ValueError(f"threshold must be in [0,1], got {threshold}")

    x = np.asarray(waveform, dtype=complex)
    if x.ndim == 1:
        x = x[:, None]
    if x.ndim != 2:
        raise ValueError(f"waveform must be 1-D or 2-D, got {x.ndim}-D")

    fs = _CBW_MHZ[chanbw] * 1e6
    lltf = lltf_waveform(chanbw)
    L = len(lltf)

    if len(x) < L:
        return None, np.array([])

    metric = np.zeros(len(x) - L + 1)
    ref = np.conj(lltf[::-1])  # flipped conjugate for correlation
    for r in range(x.shape[1]):
        corr = np.convolve(x[:, r], ref, mode="valid")
        metric += np.abs(corr) ** 2

    n_initial = int(np.argmax(metric))
    m_max = metric[n_initial]

    # CSD refinement
    delta_csd = int(round(200e-9 * fs))
    end = min(len(metric) - 1, n_initial + delta_csd)
    window = metric[n_initial: end + 1]
    above = np.where(window >= threshold * m_max)[0]
    idx_rel = int(above[-1]) if len(above) else 0
    n_max = n_initial + idx_rel

    start_offset = n_max - L
    return start_offset, metric


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WLAN Symbol Timing — 802.11 L-LTF 符号定时估计"
    )
    parser.add_argument("--subcmd", choices=["estimate", "lltf"], default="estimate",
                        help="estimate: 定时估计; lltf: 生成本地 L-LTF 波形")
    parser.add_argument("--waveform",
                        help='[estimate] 接收波形 JSON：{"real":[...],"imag":[...]}')
    parser.add_argument("--chanbw", default="CBW20", choices=list(_CBW_MHZ),
                        help="信道带宽（默认 CBW20）")
    parser.add_argument("--threshold", type=float, default=1.0,
                        help="[estimate] 检测门限 (0..1)，默认 1.0")
    args = parser.parse_args()

    try:
        if args.subcmd == "lltf":
            wf = lltf_waveform(args.chanbw)
            result = {
                "lltf_real": wf.real.tolist(),
                "lltf_imag": wf.imag.tolist(),
                "length": len(wf),
                "channel_bandwidth": args.chanbw,
            }
        else:
            if args.waveform is None:
                raise ValueError("estimate 模式需要 --waveform")
            x = parse_complex(args.waveform)
            start, metric = symbol_timing_estimate(x, args.chanbw, args.threshold)
            result = {
                "start_offset": start,
                "n_metric": len(metric),
                "metric": metric.tolist(),
                "channel_bandwidth": args.chanbw,
                "threshold": args.threshold,
            }
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()