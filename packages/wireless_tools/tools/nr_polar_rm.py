"""nr_polar_rm - 5G NR Polar 码速率匹配和恢复。

Implements TS 38.212 Section 5.4.1 Polar rate matching.
MATLAB equivalent: nrRateMatchPolar(...) and nrRateRecoverPolar(...)

处理链：
  编码: 子块交织 -> 比特选择(重复/打孔/缩短) -> [三角交织(上行)]
  解码: [三角解交织] -> 比特选择恢复 -> 子块解交织
"""
from __future__ import annotations

import argparse
import json
import sys
import os
import math

import numpy as np


# TS 38.212 Section 5.4.1.1: Sub-block interleaving pattern (0-based)
POLAR_SUBBLOCK_PERM = [
    0, 1, 2, 4, 3, 5, 6, 7, 8, 16, 9, 17, 10, 18, 11, 19,
    12, 20, 13, 21, 14, 22, 15, 23, 24, 25, 26, 28, 27, 29, 30, 31
]


def sub_block_interleave(bits: np.ndarray) -> np.ndarray:
    """Sub-block interleaving for Polar codes (TS 38.212 Section 5.4.1.1).

    Args:
        bits: Input bits, length must be power of 2

    Returns:
        Interleaved bits
    """
    N = len(bits)
    if N <= 1:
        return bits.copy()

    if N == 32:
        return bits[POLAR_SUBBLOCK_PERM]

    if N > 32 and N % 32 == 0:
        subblock_size = N // 32
        result = np.zeros_like(bits)
        for i, perm_idx in enumerate(POLAR_SUBBLOCK_PERM):
            start = i * subblock_size
            perm_start = perm_idx * subblock_size
            result[start:start + subblock_size] = bits[perm_start:perm_start + subblock_size]
        return result

    return bits.copy()


def sub_block_deinterleave(bits: np.ndarray) -> np.ndarray:
    """Sub-block deinterleaving (inverse of sub_block_interleave).

    Args:
        bits: Interleaved bits

    Returns:
        Deinterleaved bits
    """
    N = len(bits)
    if N <= 1:
        return bits.copy()

    if N == 32:
        inv_perm = np.argsort(POLAR_SUBBLOCK_PERM)
        return bits[inv_perm]

    if N > 32 and N % 32 == 0:
        subblock_size = N // 32
        result = np.zeros_like(bits)
        inv_perm = np.argsort(POLAR_SUBBLOCK_PERM)
        for i, inv_idx in enumerate(inv_perm):
            start = i * subblock_size
            inv_start = inv_idx * subblock_size
            result[inv_start:inv_start + subblock_size] = bits[start:start + subblock_size]
        return result

    return bits.copy()


def _get_triangle_size(E: int) -> int:
    """Get triangle size T for triangular interleaving."""
    return math.ceil((-1 + math.sqrt(1 + 8 * E)) / 2)


def triangular_interleave(bits: np.ndarray) -> np.ndarray:
    """Triangular interleaving for uplink (TS 38.212 Section 5.4.1.3).

    Write row-wise, read column-wise in a triangle pattern.

    Args:
        bits: Input bits, length E

    Returns:
        Interleaved bits
    """
    E = len(bits)
    T = _get_triangle_size(E)

    # Write row-wise into triangle buffer
    buffer = np.full((T, T), -1, dtype=bits.dtype)
    k = 0
    for i in range(T):
        for j in range(T - i):
            if k < E:
                buffer[i, j] = bits[k]
                k += 1

    # Read column-wise
    result = np.zeros(E, dtype=bits.dtype)
    k = 0
    for j in range(T):
        for i in range(T - j):
            if buffer[i, j] != -1:
                result[k] = buffer[i, j]
                k += 1

    return result


def triangular_deinterleave(bits: np.ndarray) -> np.ndarray:
    """Triangular deinterleaving (inverse of triangular_interleave).

    Args:
        bits: Interleaved bits, length E

    Returns:
        Deinterleaved bits
    """
    E = len(bits)
    T = _get_triangle_size(E)

    # Reconstruct the triangle buffer by reading column-wise
    buffer = np.full((T, T), -1, dtype=bits.dtype)

    k = 0
    for j in range(T):
        for i in range(T - j):
            if k < E and buffer[i, j] != -1:
                buffer[i, j] = bits[k]
                k += 1

    # Write row-wise to get original
    result = np.zeros(E, dtype=bits.dtype)
    k = 0
    for i in range(T):
        for j in range(T - i):
            if k < E and buffer[i, j] != -1:
                result[k] = buffer[i, j]
                k += 1

    return result


def rate_match_polar(bits: np.ndarray, K: int, E: int,
                     ibil: bool = False) -> np.ndarray:
    """Polar rate matching (TS 38.212 Section 5.4.1).

    Args:
        bits: Polar encoded bits, length N (power of 2)
        K: Information block length
        E: Rate-matched output length
        ibil: Enable coded-bit interleaving (uplink), default False

    Returns:
        Rate-matched bits, length E
    """
    bits = np.asarray(bits).reshape(-1)
    N = len(bits)

    if N <= 0 or (N & (N - 1)) != 0:
        raise ValueError(f"Input length must be power of 2, got {N}")

    # Step 1: Sub-block interleaving
    y = sub_block_interleave(bits)

    # Step 2: Bit selection
    if E >= N:
        # Repetition
        out = np.zeros(E, dtype=bits.dtype)
        for k in range(E):
            out[k] = y[k % N]
    else:
        if K / E <= 7 / 16:
            # Puncturing: take last E bits
            out = y[N - E:N]
        else:
            # Shortening: take first E bits
            out = y[:E]

    # Step 3: Interleaving (uplink only)
    if ibil:
        out = triangular_interleave(out)

    return out


def rate_recover_polar(bits: np.ndarray, K: int, N: int,
                       ibil: bool = False) -> np.ndarray:
    """Polar rate recovery (inverse of rate_match_polar).

    Args:
        bits: Received bits (LLR values), length E
        K: Information block length
        N: Polar encoded block length (power of 2)
        ibil: Enable coded-bit deinterleaving, default False

    Returns:
        Rate-recovered LLR values, length N
    """
    bits = np.asarray(bits, dtype=float).reshape(-1)
    E = len(bits)

    if N <= 0 or (N & (N - 1)) != 0:
        raise ValueError(f"N must be power of 2, got {N}")

    # Step 1: Deinterleaving (uplink only)
    if ibil:
        bits = triangular_deinterleave(bits)

    # Step 2: Bit selection recovery
    if E >= N:
        # Soft combine repetitions
        out = np.zeros(N, dtype=float)
        for k in range(E):
            out[k % N] += bits[k]
    else:
        if K / E <= 7 / 16:
            # Puncturing: put bits at end, 0s for punctured
            out = np.zeros(N, dtype=float)
            out[N - E:N] = bits
        else:
            # Shortening: put bits at start, large value for shortened
            out = np.full(N, 1e20, dtype=float)
            out[:E] = bits

    # Step 3: Sub-block deinterleave
    out = sub_block_deinterleave(out)

    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NR Polar Rate Matching — 5G NR Polar 码速率匹配和恢复",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  # 速率匹配
  python tools/nr_polar_rm.py --mode match --bits 0,1,1,0,1,0,0,1,1,0,0,1,1,0,0,1 \\
      --K 8 --E 12

  # 速率恢复
  python tools/nr_polar_rm.py --mode recover --bits 0.5,-0.3,0.8,-0.2,0.1,0.9 \\
      --K 8 --N 16

  # 上行（带三角交织）
  python tools/nr_polar_rm.py --mode match --bits 0,1,1,0,1,0,0,1 --K 4 --E 6 --ibil
""",
    )

    parser.add_argument("--mode", choices=["match", "recover"], required=True,
                        help="操作模式：match（速率匹配）或 recover（速率恢复）")

    parser.add_argument("--bits", required=True,
                        help="输入比特（match: 0/1 逗号分隔；recover: LLR 浮点数逗号分隔）")

    parser.add_argument("--K", type=int, required=True,
                        help="信息块长度 K")

    parser.add_argument("--E", type=int, default=None,
                        help="[match] 速率匹配输出长度 E")
    parser.add_argument("--N", type=int, default=None,
                        help="[recover] Polar 编码块长度 N（2 的幂）")

    parser.add_argument("--ibil", action="store_true",
                        help="启用编码比特交织（上行）")

    args = parser.parse_args()

    try:
        input_bits = np.array([float(x) for x in args.bits.split(",")])

        if args.mode == "match":
            if args.E is None:
                raise ValueError("match 模式需要 --E")
            bits = input_bits.astype(int)
            result_bits = rate_match_polar(bits, args.K, args.E, args.ibil)
            result = {
                "output_bits": result_bits.tolist(),
                "E": len(result_bits),
            }
        else:
            if args.N is None:
                raise ValueError("recover 模式需要 --N")
            result_bits = rate_recover_polar(input_bits, args.K, args.N, args.ibil)
            result = {
                "soft_bits": result_bits.tolist(),
                "N": len(result_bits),
            }

        print(json.dumps(result))

    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
