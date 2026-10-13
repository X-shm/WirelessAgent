"""wlan_ofdm_info - IEEE 802.11 Non-HT OFDM 参数信息工具。

Implements OFDM parameter info for non-HT fields.
MATLAB equivalent: wlanNonHTOFDMInfo(fieldname, chanbw)

字段：
  - L-LTF：传统长训练字段（CP = [32, 0]）
  - L-SIG：传统信号字段（CP = 16）
  - NonHT-Data：非 HT 数据（CP = 16）

信道带宽：CBW5, CBW10, CBW20, CBW40, CBW80, CBW160

输出 info 结构：
  FFTLength, SampleRate, CPLength, NumTones, NumSubchannels,
  ActiveFrequencyIndices, ActiveFFTIndices, DataIndices, PilotIndices
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

# 信道带宽 → (MHz, 20MHz 子信道数)
_CBW_TABLE = {
    "CBW5": (5, 1),
    "CBW10": (10, 1),
    "CBW20": (20, 1),
    "CBW40": (40, 2),
    "CBW80": (80, 4),
    "CBW160": (160, 8),
}

_FIELDS = ["NonHT-Data", "L-SIG", "L-LTF"]


def _non_ht_tone_indices(num_subchannels: int) -> tuple[np.ndarray, np.ndarray]:
    """Get active tone frequency indices and pilot indices (relative to DC)."""
    pilot_idx20 = np.array([-21, -7, 7, 21])
    freq_ind20 = np.concatenate([np.arange(-26, 0), np.arange(1, 27)])
    if num_subchannels == 1:
        return freq_ind20, pilot_idx20
    max_offset = 64 * (num_subchannels - 1)
    offsets = np.arange(0, 64 * num_subchannels, 64) - max_offset / 2
    freq_ind = (freq_ind20[None, :] + offsets[:, None]).reshape(-1)
    pilot_idx = (pilot_idx20[None, :] + offsets[:, None]).reshape(-1)
    return freq_ind, pilot_idx


def non_ht_ofdm_info(fieldname: str, chanbw: str = "CBW20",
                     osf: float = 1.0) -> dict:
    """Get OFDM info for a non-HT field.

    Args:
        fieldname: 'NonHT-Data', 'L-SIG' or 'L-LTF'
        chanbw: channel bandwidth string
        osf: oversampling factor (>= 1)

    Returns:
        dict with FFTLength, SampleRate, CPLength, NumTones, NumSubchannels,
        ActiveFrequencyIndices, ActiveFFTIndices, DataIndices, PilotIndices
    """
    if fieldname not in _FIELDS:
        raise ValueError(f"fieldname must be one of {_FIELDS}, got {fieldname}")
    if chanbw not in _CBW_TABLE:
        raise ValueError(f"chanbw must be one of {list(_CBW_TABLE)}, got {chanbw}")
    if osf < 1:
        raise ValueError(f"oversampling factor must be >= 1, got {osf}")

    mhz, num_subchannels = _CBW_TABLE[chanbw]
    fft_length = 64 * num_subchannels

    if fieldname in ("NonHT-Data", "L-SIG"):
        cp_length = 16 * num_subchannels
    else:  # L-LTF
        cp_length = [32 * num_subchannels, 0]

    freq_ind, pilot_idx = _non_ht_tone_indices(num_subchannels)
    num_st = len(freq_ind)
    is_pilot = np.isin(freq_ind, pilot_idx)
    seq = np.arange(1, num_st + 1)
    pilot_indices = seq[is_pilot].tolist()
    data_indices = seq[~is_pilot].tolist()

    return {
        "FFTLength": int(fft_length * osf),
        "SampleRate": mhz * 1e6 * osf,
        "CPLength": (int(cp_length * osf) if fieldname != "L-LTF"
                     else [int(32 * num_subchannels * osf), 0]),
        "NumTones": num_st,
        "NumSubchannels": num_subchannels,
        "ActiveFrequencyIndices": freq_ind.tolist(),
        "ActiveFFTIndices": (freq_ind + fft_length * osf / 2 + 1).tolist(),
        "DataIndices": data_indices,
        "PilotIndices": pilot_indices,
        "FieldName": fieldname,
        "ChannelBandwidth": chanbw,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WLAN Non-HT OFDM Info — 802.11 OFDM 参数信息"
    )
    parser.add_argument("--field", required=True, choices=_FIELDS,
                        help="OFDM 字段名")
    parser.add_argument("--chanbw", default="CBW20", choices=list(_CBW_TABLE),
                        help="信道带宽（默认 CBW20）")
    parser.add_argument("--osf", type=float, default=1.0,
                        help="过采样因子 (>=1)，默认 1")
    args = parser.parse_args()

    try:
        info = non_ht_ofdm_info(args.field, args.chanbw, args.osf)
        print(json.dumps(info))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
