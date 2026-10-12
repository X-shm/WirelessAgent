"""nr_prbs - 5G NR Pseudorandom Binary Sequence generator.

Implements TS 38.211 Section 5.2.1 Gold sequence PRBS generator.
MATLAB equivalent: nrPRBS(cinit, n)
"""
from __future__ import annotations
import argparse
import json
import sys
import numpy as np

# ── LFSR taps for x^31 + x^3 + 1 ──
# The PRBS generator uses two length-31 m-sequences (Gold code):
#   c1: x^31 + x^3 + 1, initialised to all-ones
#   c2: same polynomial, initialised based on cinit
# Output: c(n) = c1((n+Nc) mod L) XOR c2((n+Nc) mod L),  L = 2^31 - 1
# Nc = 1600 (offset per spec)

_POLY_TAPS = [0, 3]  # x^31 + x^3 + 1 → taps at positions 0 and 3
_LFSR_LEN = 31
_PERIOD = (1 << 31) - 1  # 2^31 - 1 = 2147483647
_Nc = 1600


def _lfsr_step_x1(state: np.ndarray) -> tuple[np.ndarray, int]:
    """Single step of x^31 + x^3 + 1 LFSR for x1. Returns (new_state, output_bit)."""
    feedback = int(state[0]) ^ int(state[3])
    out = int(state[0])
    state = np.roll(state, -1)
    state[-1] = feedback
    return state, out


def _lfsr_step_x2(state: np.ndarray) -> tuple[np.ndarray, int]:
    """Single step of x^31 + x^3 + x^2 + x + 1 LFSR for x2. Returns (new_state, output_bit)."""
    feedback = int(state[0]) ^ int(state[1]) ^ int(state[2]) ^ int(state[3])
    out = int(state[0])
    state = np.roll(state, -1)
    state[-1] = feedback
    return state, out


def _gen_mseq(cinit: int, total_len: int) -> np.ndarray:
    """Generate Gold code from two m-sequences per TS 38.211 5.2.1.

    Args:
        cinit: 31-bit initialisation value
        total_len: total number of output bits needed

    Returns:
        Gold code sequence of length total_len
    """
    # x1: polynomial x^31+x^3+1, initial state x1(0)=1, x1(1..30)=0
    x1_state = np.zeros(_LFSR_LEN, dtype=np.int8)
    x1_state[0] = 1

    # x2: polynomial x^31+x^3+x^2+x+1, initial state from cinit bits
    x2_state = np.zeros(_LFSR_LEN, dtype=np.int8)
    for j in range(_LFSR_LEN):
        x2_state[j] = (cinit >> j) & 1

    gen_len = _Nc + total_len
    x1_seq = np.zeros(gen_len, dtype=np.int8)
    x2_seq = np.zeros(gen_len, dtype=np.int8)

    for i in range(gen_len):
        x1_state, x1_seq[i] = _lfsr_step_x1(x1_state)
        x2_state, x2_seq[i] = _lfsr_step_x2(x2_state)

    gold = x1_seq[_Nc:] ^ x2_seq[_Nc:]
    return gold[:total_len]


def prbs(cinit: int, n, mapping: str = "binary") -> np.ndarray:
    """Generate 5G NR PRBS sequence per TS 38.211 Section 5.2.1.

    Args:
        cinit: 31-bit initialisation value (0..2^31-1)
        n: sequence length, or [offset, length] pair (0-based offset)
        mapping: 'binary' (0/1) or 'signed' (1/-1)

    Returns:
        PRBS sequence (int8 array for binary, float64 for signed)
    """
    cinit = int(cinit)
    if cinit < 0 or cinit > _PERIOD:
        raise ValueError(f"cinit must be 0..{_PERIOD}, got {cinit}")

    if isinstance(n, (list, tuple, np.ndarray)):
        n_arr = np.asarray(n).flatten().astype(int)
        if len(n_arr) == 2:
            offset = n_arr[0]
            length = n_arr[1]
        else:
            offset = 0
            length = int(n_arr[0])
    else:
        offset = 0
        length = int(n)

    if length < 0:
        raise ValueError(f"length must be non-negative, got {length}")
    if offset < 0:
        raise ValueError(f"offset must be non-negative, got {offset}")

    # Generate enough bits to cover offset + length
    total = offset + length
    seq = _gen_mseq(cinit, total)

    # Extract the requested subsequence
    result = seq[offset:offset + length]

    if mapping == "signed":
        # signed: 0 → +1, 1 → -1
        return np.where(result == 0, 1.0, -1.0).astype(np.float64)
    return result.astype(np.int8)


def main():
    parser = argparse.ArgumentParser(description="5G NR PRBS generator (TS 38.211 Sec 5.2.1)")
    parser.add_argument("--cinit", type=int, required=True, help="31-bit initialization value")
    parser.add_argument("--n", type=int, default=100, help="Sequence length")
    parser.add_argument("--offset", type=int, default=0, help="Sequence offset (0-based)")
    parser.add_argument("--mapping", choices=["binary", "signed"], default="binary",
                        help="Output mapping type")
    args = parser.parse_args()

    try:
        if args.offset > 0:
            seq = prbs(args.cinit, [args.offset, args.n], args.mapping)
        else:
            seq = prbs(args.cinit, args.n, args.mapping)

        if args.mapping == "signed":
            result = {
                "cinit": args.cinit,
                "n": args.n,
                "offset": args.offset,
                "mapping": args.mapping,
                "seq_signed": seq.tolist(),
            }
        else:
            result = {
                "cinit": args.cinit,
                "n": args.n,
                "offset": args.offset,
                "mapping": args.mapping,
                "seq": seq.astype(int).tolist(),
            }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
