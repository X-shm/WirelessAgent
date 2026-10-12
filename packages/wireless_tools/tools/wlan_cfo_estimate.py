"""wlan_cfo_estimate - IEEE 802.11 载波频偏估计工具。

Implements coarse (L-STF) and fine (L-LTF) carrier frequency offset estimation.
MATLAB equivalent: wlanCoarseCFOEstimate / wlanFineCFOEstimate

核心算法（Van Zelst & Schenk 2004）：
  对周期为 D 的重复序列：
    foffset_norm = angle(Σ conj(x_early) · x_delayed) / (2π)
    foffset_Hz   = foffset_norm · fs / D

粗估计（L-STF，0.8us 短训练序列）：M = fftLen/4, GI = fftLen/4, S = 9M
细估计（L-LTF，3.2us 长训练序列）：M = fftLen,   GI = fftLen/2, S = 2M
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


def cfo_estimate(x: np.ndarray, d: int) -> float:
    """Estimate normalized frequency offset from a repeated pattern.

    Args:
        x: complex signal [Ns, Nr] with a repeated pattern of period D
        d: repetition period in samples

    Returns:
        Normalized frequency offset (cycles per sample)
    """
    x = np.asarray(x, dtype=complex)
    if x.ndim == 1:
        x = x[:, None]
    num_samples = x.shape[0]
    if num_samples < 2 * d:
        raise ValueError(
            f"not enough samples: need >= {2 * d}, got {num_samples}")

    unused = num_samples % d
    cx = x[: num_samples - (d + unused)]
    sx = x[d: num_samples - unused]
    res = np.sum(np.conj(cx) * sx, axis=0)
    return float(np.angle(np.sum(res)) / (2 * np.pi))


def _resolve_geometry(chanbw: str, osf: float) -> tuple[float, float]:
    """Return (fft_len, sample_rate) for the given bandwidth."""
    if chanbw not in _CBW_MHZ:
        raise ValueError(f"chanbw must be one of {list(_CBW_MHZ)}, got {chanbw}")
    if osf < 1:
        raise ValueError(f"oversampling factor must be >= 1, got {osf}")
    mhz = _CBW_MHZ[chanbw]
    num20 = mhz / 20 if mhz > 20 else 1
    return 64 * num20 * osf, mhz * 1e6 * osf


def coarse_cfo_estimate(waveform: np.ndarray, chanbw: str = "CBW20",
                        corr_offset: float = 0.75, osf: float = 1.0) -> float:
    """Coarse CFO estimate from L-STF (frequency offset in Hz)."""
    if not 0 <= corr_offset <= 1:
        raise ValueError(f"corrOffset must be in [0,1], got {corr_offset}")

    fft_len, fs = _resolve_geometry(chanbw, osf)
    mhz = _CBW_MHZ[chanbw]
    num20 = mhz / 20 if mhz > 20 else 1
    n_stf = int(160 * num20 * osf)

    x = np.asarray(waveform, dtype=complex)
    if x.ndim == 1:
        x = x[:, None]
    lstf = x[: min(n_stf, len(x)), :]

    m = fft_len / 4
    gi = fft_len / 4
    s = m * 9
    n = len(lstf)
    offset = int(round(corr_offset * gi))
    if offset >= n:
        raise ValueError(f"corrOffset too large: offset {offset} >= samples {n}")
    take = int(min(s, n - offset))
    use = lstf[offset: offset + take, :]

    return cfo_estimate(use, int(m)) * fs / m


def fine_cfo_estimate(waveform: np.ndarray, chanbw: str = "CBW20",
                      corr_offset: float = 0.75, osf: float = 1.0) -> float:
    """Fine CFO estimate from L-LTF (frequency offset in Hz)."""
    if not 0 <= corr_offset <= 1:
        raise ValueError(f"corrOffset must be in [0,1], got {corr_offset}")

    fft_len, fs = _resolve_geometry(chanbw, osf)
    mhz = _CBW_MHZ[chanbw]
    num20 = mhz / 20 if mhz > 20 else 1
    n_ltf = int(160 * num20 * osf)

    x = np.asarray(waveform, dtype=complex)
    if x.ndim == 1:
        x = x[:, None]
    lltf = x[: min(n_ltf, len(x)), :]

    m = fft_len
    gi = fft_len / 2
    s = m * 2
    n = len(lltf)
    offset = int(round(corr_offset * gi))
    if offset >= n:
        raise ValueError(f"corrOffset too large: offset {offset} >= samples {n}")
    take = int(min(s, n - offset))
    use = lltf[offset: offset + take, :]

    return cfo_estimate(use, int(m)) * fs / m


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WLAN CFO Estimate — 802.11 粗/细载波频偏估计"
    )
    parser.add_argument("--mode", choices=["coarse", "fine"], required=True,
                        help="coarse: L-STF 粗估计; fine: L-LTF 细估计")
    parser.add_argument("--waveform", required=True,
                        help='接收波形 JSON：{"real":[...],"imag":[...]}')
    parser.add_argument("--chanbw", default="CBW20", choices=list(_CBW_MHZ),
                        help="信道带宽（默认 CBW20）")
    parser.add_argument("--corr_offset", type=float, default=0.75,
                        help="相关起始（GI 的比例，0..1），默认 0.75")
    parser.add_argument("--osf", type=float, default=1.0,
                        help="过采样因子 (>=1)，默认 1")
    args = parser.parse_args()

    try:
        x = parse_complex(args.waveform)
        if args.mode == "coarse":
            fo = coarse_cfo_estimate(x, args.chanbw, args.corr_offset, args.osf)
        else:
            fo = fine_cfo_estimate(x, args.chanbw, args.corr_offset, args.osf)
        result = {
            "frequency_offset_hz": fo,
            "mode": args.mode,
            "channel_bandwidth": args.chanbw,
            "corr_offset": args.corr_offset,
            "oversampling_factor": args.osf,
        }
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
