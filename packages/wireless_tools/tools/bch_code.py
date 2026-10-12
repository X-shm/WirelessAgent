"""Primitive narrow-sense binary BCH encoder/decoder."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from _gf import GF2m, berlekamp_massey, find_error_positions, poly_eval, poly_mul


def generator_for_t(n: int, t: int, gf: GF2m) -> list[int]:
    exponents: set[int] = set()
    for root in range(1, 2 * t + 1):
        value = root % n
        while value not in exponents:
            exponents.add(value)
            value = (2 * value) % n
    generator = [1]
    for exponent in sorted(exponents):
        generator = poly_mul(generator, [1, gf.alpha(exponent)], gf)
    if any(value not in (0, 1) for value in generator):
        raise ValueError("generator polynomial did not reduce to GF(2)")
    return generator


def parameters(n: int, k: int, primitive: int | None = None) -> tuple[GF2m, list[int], int]:
    m = int(round(math.log2(n + 1)))
    if m < 2 or (1 << m) - 1 != n:
        raise ValueError("n must equal 2^m-1 with 2 <= m <= 8")
    gf = GF2m(m, primitive)
    if not (1 <= k < n):
        raise ValueError("k must satisfy 1 <= k < n")
    for t in range(1, (n - k) // 2 + 2):
        generator = generator_for_t(n, t, gf)
        if len(generator) - 1 == n - k:
            return gf, generator, t
        if len(generator) - 1 > n - k:
            break
    raise ValueError("(n,k) is not a supported primitive narrow-sense BCH pair")


def encode(message, n: int, k: int, primitive: int | None = None, parity_position: str = "end"):
    bits = np.asarray(message, dtype=int).reshape(-1)
    if len(bits) != k or np.any((bits != 0) & (bits != 1)):
        raise ValueError("message must contain exactly k binary values")
    _, generator, t = parameters(n, k, primitive)
    parity_length = n - k
    work = bits.tolist() + [0] * parity_length
    for i in range(k):
        if work[i]:
            for j in range(1, len(generator)):
                work[i + j] ^= generator[j]
    parity = work[-parity_length:]
    codeword = bits.tolist() + parity
    if parity_position == "beginning":
        codeword = parity + bits.tolist()
    return np.asarray(codeword, dtype=int), generator, t


def _syndromes(codeword: list[int], t: int, gf: GF2m) -> list[int]:
    return [poly_eval(codeword, gf.alpha(i), gf) for i in range(1, 2 * t + 1)]


def decode(codeword, n: int, k: int, primitive: int | None = None, parity_position: str = "end"):
    bits = np.asarray(codeword, dtype=int).reshape(-1)
    if len(bits) != n or np.any((bits != 0) & (bits != 1)):
        raise ValueError("codeword must contain exactly n binary values")
    gf, _, t = parameters(n, k, primitive)
    parity_length = n - k
    received = bits.tolist()
    if parity_position == "beginning":
        received = received[parity_length:] + received[:parity_length]
    syn = _syndromes(received, t, gf)
    corrected = received.copy()
    errors = 0
    if any(syn):
        locator = berlekamp_massey(syn, gf)
        errors = len(locator) - 1
        if errors == 0 or errors > t:
            raise ValueError("too many errors to correct")
        positions = find_error_positions(locator, n, gf)
        for position in positions:
            corrected[position] ^= 1
        if any(_syndromes(corrected, t, gf)):
            raise ValueError("too many errors to correct")
    returned = corrected if parity_position == "end" else corrected[k:] + corrected[:k]
    return np.asarray(corrected[:k]), np.asarray(returned), errors, t


def _bits(text: str) -> list[int]:
    return [int(value) for value in text.split(",") if value.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["encode", "decode", "generator"], required=True)
    parser.add_argument("--bits", default="")
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--primitive", type=lambda value: int(value, 0))
    parser.add_argument("--parity_position", choices=["end", "beginning"], default="end")
    args = parser.parse_args()
    try:
        if args.mode == "generator":
            gf, generator, t = parameters(args.n, args.k, args.primitive)
            result = {"generator": generator, "m": gf.m, "correctable_errors": t}
        elif args.mode == "encode":
            codeword, generator, t = encode(_bits(args.bits), args.n, args.k, args.primitive, args.parity_position)
            result = {"codeword": codeword.tolist(), "generator": generator, "correctable_errors": t}
        else:
            message, corrected, errors, t = decode(_bits(args.bits), args.n, args.k, args.primitive, args.parity_position)
            result = {"message": message.tolist(), "corrected_codeword": corrected.tolist(), "corrected_errors": errors, "correctable_errors": t}
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, ZeroDivisionError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
