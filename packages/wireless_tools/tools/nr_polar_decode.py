"""Standalone successive-cancellation NR Polar decoder for list length one."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from nr_polar import _construct, _interleave_map


def _decode_node(llr: np.ndarray, frozen: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(llr) == 1:
        bit = np.int8(0 if frozen[0] else llr[0] < 0)
        return np.array([bit], dtype=np.int8), np.array([bit], dtype=np.int8)
    half = len(llr) // 2
    a, b = llr[:half], llr[half:]
    left_llr = (np.sign(a) * np.sign(b) * np.minimum(np.abs(a), np.abs(b))
                + np.log1p(np.exp(-np.abs(a + b)))
                - np.log1p(np.exp(-np.abs(a - b))))
    left_u, left_x = _decode_node(left_llr, frozen[:half])
    right_llr = b + (1 - 2 * left_x) * a
    right_u, right_x = _decode_node(right_llr, frozen[half:])
    return np.concatenate((left_u, right_u)), np.concatenate((left_x ^ right_x, right_x))


def polar_decode_sc(rec: np.ndarray, k: int, e: int, nmax: int = 9,
                    iil: bool = True) -> np.ndarray:
    """Decode rate-recovered mother-code LLRs; equivalent to L=1 SC path."""
    soft = np.asarray(rec, dtype=float).reshape(-1)
    if type(k) is not int or type(e) is not int or k <= 0 or e <= k:
        raise ValueError("K and E must be positive integers with E > K")
    if nmax not in (9, 10) or not isinstance(iil, bool):
        raise ValueError("nmax must be 9/10 and iil must be boolean")
    if not np.all(np.isfinite(soft)):
        raise ValueError("rec must contain finite LLR values")
    frozen, _, _, n = _construct(k, e, nmax)
    if len(soft) != n:
        raise ValueError(f"rec must contain {n} rate-recovered LLRs")
    estimate, _ = _decode_node(soft, frozen)
    interleaved = estimate[frozen == 0]
    if not iil:
        return interleaved
    message = np.empty_like(interleaved)
    message[_interleave_map(k)] = interleaved
    return message


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR Polar L=1 SC decoding")
    parser.add_argument("--rec", required=True, help="JSON rate-recovered mother-code LLR vector")
    parser.add_argument("--k", type=int, required=True, help="Information bits, including CRC")
    parser.add_argument("--e", type=int, required=True, help="Transmitted rate-matched length")
    parser.add_argument("--nmax", type=int, choices=(9, 10), default=9)
    parser.add_argument("--iil", type=lambda text: text.lower() in ("true", "1"), default=True)
    parser.add_argument("--list_length", type=int, default=1)
    args = parser.parse_args()
    try:
        if args.list_length != 1:
            raise ValueError("this decoder implements list_length=1 only")
        result = polar_decode_sc(np.asarray(json.loads(args.rec)), args.k, args.e,
                                 args.nmax, args.iil)
        print(json.dumps({"decoded_bits": result.tolist(), "K": args.k,
                          "E": args.e, "list_length": 1}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
