"""wlan_golay - IEEE 802.11ad Golay 序列生成工具。

Implements Golay complementary sequences per IEEE Std 802.11ad-2012 Section 21.11.
MATLAB equivalent: wlanGolaySequence(len)

长度支持：32, 64, 128（802.11ad DMG 训练序列基础）。
输出 Ga、Gb 两列互补 Golay 序列（±1）。
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

# IEEE Std 802.11ad-2012 Section 21.11 硬编码序列
_GA_128 = np.array([
    1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, -1, 1, -1, 1, -1, 1, 1, -1,
    -1, -1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1, 1, 1, -1, 1, 1, -1, -1, 1, 1, 1, 1, -1, 1, -1, 1, -1, 1, 1, -1,
    1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, -1, 1, -1, 1, -1, 1, 1, -1,
    1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1,
])

_GB_128 = np.array([
    -1, -1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1, 1, 1, -1, -1, -1, 1, 1, -1, -1, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1,
    1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1,
    1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, 1, -1, 1, -1, 1, -1, 1, 1, -1,
    1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1, -1, 1, -1, 1, -1, -1, 1,
])

_GA_64 = np.array([
    -1, -1, 1, -1, 1, -1, -1, -1, 1, 1, -1, 1, 1, -1, -1, -1, -1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, 1, 1,
    -1, -1, 1, -1, 1, -1, -1, -1, 1, 1, -1, 1, 1, -1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, -1, 1, 1, -1, -1, -1,
])

_GB_64 = np.array([
    1, 1, -1, 1, -1, 1, 1, 1, -1, -1, 1, -1, -1, 1, 1, 1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, -1, 1, 1, -1, -1, -1,
    -1, -1, 1, -1, 1, -1, -1, -1, 1, 1, -1, 1, 1, -1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, -1, 1, 1, -1, -1, -1,
])

_GA_32 = np.array([1, 1, 1, 1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, -1, 1, -1])
_GB_32 = np.array([-1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1, 1, 1, -1, 1, 1, -1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, -1, 1, -1])

_SEQUENCES = {
    32: (_GA_32, _GB_32),
    64: (_GA_64, _GB_64),
    128: (_GA_128, _GB_128),
}


def golay_sequence(length: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate Golay complementary sequences per IEEE 802.11ad.

    Args:
        length: sequence length, must be 32, 64 or 128

    Returns:
        (Ga, Gb): two ±1 sequences of the given length
    """
    if length not in _SEQUENCES:
        raise ValueError(f"length must be 32, 64 or 128, got {length}")
    ga, gb = _SEQUENCES[length]
    if len(ga) != length or len(gb) != length:
        raise RuntimeError(f"hardcoded sequence length mismatch for len={length}")
    return ga.astype(float), gb.astype(float)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WLAN Golay — IEEE 802.11ad Golay 序列"
    )
    parser.add_argument("--length", type=int, required=True, choices=[32, 64, 128],
                        help="Golay 序列长度 (32/64/128)")
    args = parser.parse_args()

    try:
        ga, gb = golay_sequence(args.length)
        result = {
            "length": args.length,
            "Ga": ga.tolist(),
            "Gb": gb.tolist(),
        }
        print(json.dumps(result))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
