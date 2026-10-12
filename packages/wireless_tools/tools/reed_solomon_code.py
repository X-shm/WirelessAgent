"""Systematic narrow-sense Reed-Solomon encoder/decoder over GF(2^m)."""
from __future__ import annotations
import argparse
import json
import sys

from _gf import GF2m, berlekamp_massey, find_error_positions, poly_eval, poly_mul, solve_linear


def generator_polynomial(nsym: int, gf: GF2m, first_root: int = 1) -> list[int]:
    generator = [1]
    for exponent in range(first_root, first_root + nsym):
        generator = poly_mul(generator, [1, gf.alpha(exponent)], gf)
    return generator


def _validate(n: int, k: int, gf: GF2m) -> int:
    if not (3 <= n <= gf.order):
        raise ValueError("n must satisfy 3 <= n <= 2^m-1")
    nsym = n - k
    if k < 1 or nsym < 2 or nsym % 2:
        raise ValueError("n-k must be a positive even number")
    return nsym


def encode(message: list[int], n: int, k: int, gf: GF2m, parity_position: str = "end") -> tuple[list[int], list[int]]:
    nsym = _validate(n, k, gf)
    if len(message) != k or any(value < 0 or value >= gf.size for value in message):
        raise ValueError("message must contain k symbols in the selected field")
    generator = generator_polynomial(nsym, gf)
    work = list(message) + [0] * nsym
    for i in range(k):
        coefficient = work[i]
        if coefficient:
            for j in range(1, len(generator)):
                work[i + j] ^= gf.mul(generator[j], coefficient)
    parity = work[-nsym:]
    codeword = list(message) + parity
    if parity_position == "beginning":
        codeword = parity + list(message)
    return codeword, generator


def syndromes(codeword: list[int], nsym: int, gf: GF2m) -> list[int]:
    return [poly_eval(codeword, gf.alpha(1 + i), gf) for i in range(nsym)]


def decode(codeword: list[int], n: int, k: int, gf: GF2m, parity_position: str = "end") -> tuple[list[int], list[int], int]:
    nsym = _validate(n, k, gf)
    if len(codeword) != n or any(value < 0 or value >= gf.size for value in codeword):
        raise ValueError("codeword must contain n symbols in the selected field")
    received = list(codeword)
    if parity_position == "beginning":
        received = received[nsym:] + received[:nsym]
    syn = syndromes(received, nsym, gf)
    if not any(syn):
        corrected = received
        errors = 0
    else:
        locator = berlekamp_massey(syn, gf)
        errors = len(locator) - 1
        if errors == 0 or errors > nsym // 2:
            raise ValueError("too many errors to correct")
        positions = find_error_positions(locator, n, gf)
        locations = [n - 1 - position for position in positions]
        matrix = [[gf.alpha((1 + row) * location) for location in locations] for row in range(errors)]
        magnitudes = solve_linear(matrix, syn[:errors], gf)
        corrected = received.copy()
        for position, magnitude in zip(positions, magnitudes):
            corrected[position] ^= magnitude
        if any(syndromes(corrected, nsym, gf)):
            raise ValueError("too many errors to correct")
    message = corrected[:k]
    returned = corrected if parity_position == "end" else corrected[k:] + corrected[:k]
    return message, returned, errors


def _symbols(text: str) -> list[int]:
    value = json.loads(text)
    if not isinstance(value, list):
        raise ValueError("symbols must be a JSON array")
    return [int(item) for item in value]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["encode", "decode", "generator"], required=True)
    parser.add_argument("--symbols", default="[]")
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--m", type=int, required=True)
    parser.add_argument("--primitive", type=lambda value: int(value, 0))
    parser.add_argument("--parity_position", choices=["end", "beginning"], default="end")
    args = parser.parse_args()
    try:
        gf = GF2m(args.m, args.primitive)
        if args.mode == "generator":
            nsym = _validate(args.n, args.k, gf)
            result = {"generator": generator_polynomial(nsym, gf), "correctable_errors": nsym // 2}
        elif args.mode == "encode":
            codeword, generator = encode(_symbols(args.symbols), args.n, args.k, gf, args.parity_position)
            result = {"codeword": codeword, "generator": generator, "correctable_errors": (args.n - args.k) // 2}
        else:
            message, corrected, errors = decode(_symbols(args.symbols), args.n, args.k, gf, args.parity_position)
            result = {"message": message, "corrected_codeword": corrected, "corrected_errors": errors}
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, ZeroDivisionError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
