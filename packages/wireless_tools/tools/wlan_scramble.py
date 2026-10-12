"""WLAN Scramble Tool — IEEE 802.11 Scrambler / Descrambler.

Replicates MATLAB wlanScramble.
7-bit LFSR with polynomial x^7 + x^4 + 1.
Scrambling and descrambling use the same operation (self-synchronous).
Seed range: 1-127 (integer, or 7-bit binary representation).
Verified against MATLAB golden samples.
"""
from __future__ import annotations

import json
import sys
import numpy as np


def scramble(bits: np.ndarray, seed: int) -> np.ndarray:
    """Scramble (or descramble) bits using 802.11 7-bit LFSR.

    Same function works for both scrambling and descrambling
    (self-synchronous property of LFSR-based scramblers).

    MATLAB-compatible implementation:
    - Generator polynomial: x^7 + x^4 + 1 (IEEE 802.11 Section 18.3.5.5)
    - State ordering: state[0]=x7 (LSB of seed), state[6]=x1 (MSB of seed)
    - Feedback = x7 XOR x4 = state[0] ^ state[3]
    - Left shift each cycle, new bit goes into x1 position

    Args:
        bits: Input bit array (0/1 values)
        seed: LFSR initial state, integer 1-127

    Returns:
        Scrambled bit array, same length as input
    """
    bits = np.asarray(bits, dtype=np.uint8) % 2
    n = len(bits)

    # Initialize 7-bit LFSR state from seed
    # MATLAB uses int2bit(seed, 7) which returns LSB first.
    # State mapping: state[0]=x7, state[1]=x6, state[2]=x5,
    #                state[3]=x4, state[4]=x3, state[5]=x2, state[6]=x1
    # After testing against MATLAB golden samples, the correct mapping is:
    #   seed MSB (bit 6) → state[0] → x7
    #   seed LSB (bit 0) → state[6] → x1
    # i.e., the seed integer maps to state MSB-first
    state = np.zeros(7, dtype=np.uint8)
    for i in range(7):
        state[i] = (seed >> (6 - i)) & 1

    # Generate scrambling sequence (period 127)
    seq = np.zeros(n, dtype=np.uint8)
    for i in range(n):
        # Feedback = x7 XOR x4 = state[0] ^ state[3]
        seq[i] = state[0] ^ state[3]
        # Left shift: positions 1..7 → 0..6 (MATLAB 1-indexed)
        # In 0-indexed Python: state[0:6] = state[1:7]
        state[0:6] = state[1:7]
        # New bit goes into position 6 (x1, last stage)
        state[6] = seq[i]

    # Output = input XOR scrambling sequence
    return bits ^ seq


def main():
    import argparse
    parser = argparse.ArgumentParser("WLAN Scramble tool")
    parser.add_argument('--bits', required=True, help="comma-separated data bits")
    parser.add_argument('--seed', type=int, required=True,
                        help="scrambler initial state, integer 1-127")
    parser.add_argument('--descramble', action='store_true',
                        help="descramble mode (same operation as scramble)")
    args = parser.parse_args()
    bits = np.array([int(b) for b in args.bits.split(',')], dtype=np.uint8)

    result = scramble(bits, args.seed)
    mode = 'descramble' if args.descramble else 'scramble'
    print(json.dumps({
        "mode": mode,
        "seed": args.seed,
        "input_bits": bits.tolist(),
        "output_bits": result.tolist()
    }))


if __name__ == '__main__':
    main()
