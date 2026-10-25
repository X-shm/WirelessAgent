"""Standalone PUSCH bit scrambling and soft-bit descrambling."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
from nr_channel_prbs import channel_prbs


def scramble(bits: np.ndarray, nid: int, rnti: int, q: int = 0) -> np.ndarray:
    data = np.asarray(bits)
    if data.ndim != 1 or not np.all(np.isin(data, (0, 1))):
        raise ValueError("bits must be a one-dimensional binary array")
    _, sequence = channel_prbs("pusch", nid, len(data), rnti=rnti, q=q)
    return np.bitwise_xor(data.astype(np.int8), np.asarray(sequence, dtype=np.int8))


def descramble(soft_bits: np.ndarray, nid: int, rnti: int, q: int = 0) -> np.ndarray:
    data = np.asarray(soft_bits, dtype=float)
    if data.ndim != 1 or not np.all(np.isfinite(data)):
        raise ValueError("soft_bits must be a one-dimensional finite numeric array")
    _, sequence = channel_prbs("pusch", nid, len(data), rnti=rnti, q=q)
    return data * (1 - 2 * np.asarray(sequence, dtype=int))


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR PUSCH scramble/descramble")
    parser.add_argument("--operation", choices=("scramble", "descramble"), required=True)
    parser.add_argument("--data", required=True, help="JSON vector of bits or soft values")
    parser.add_argument("--nid", type=int, required=True)
    parser.add_argument("--rnti", type=int, required=True)
    parser.add_argument("--q", type=int, default=0)
    args = parser.parse_args()
    try:
        data = np.asarray(json.loads(args.data))
        output = scramble(data, args.nid, args.rnti, args.q) if args.operation == "scramble" else descramble(data, args.nid, args.rnti, args.q)
        print(json.dumps({"operation": args.operation, "data": output.tolist()}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
