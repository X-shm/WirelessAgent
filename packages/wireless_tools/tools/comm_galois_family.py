"""Finite-field and binary-polynomial arithmetic without MATLAB."""
from __future__ import annotations

import itertools

import numpy as np

from _gf import DEFAULT_PRIMITIVES, GF2m, poly_mul
from _nr_remaining_common import run_cli


def _polyint(value):
    if isinstance(value, int):
        return value
    coefficients = list(map(int, value))
    if not coefficients or any(bit not in (0, 1) for bit in coefficients):
        raise ValueError("polynomial coefficients must be binary")
    out = 0
    for bit in coefficients:
        out = (out << 1) | bit
    return out


def _field(m: int, primitive=None):
    return GF2m(m, None if primitive is None else _polyint(primitive))


def gf(values, m: int = 1, primitive=None):
    if m == 1:
        size, poly = 2, 3
    else:
        field = _field(m, primitive)
        size, poly = field.size, field.primitive
    x = np.asarray(values)
    if not x.size or np.any(x != np.floor(x)) or np.any(x < 0) or np.any(x >= size):
        raise ValueError("GF elements must be integers in 0..2^m-1")
    return {"values": x.astype(int), "m": m, "primitive": poly}


def gfdiv(numerator, denominator, m: int = 1, primitive=None):
    a, b = np.broadcast_arrays(np.asarray(numerator, int), np.asarray(denominator, int))
    if np.any(b == 0):
        raise ValueError("GF division by zero")
    if m == 1:
        return {"values": a & 1}
    field = _field(m, primitive)
    if np.any(a < 0) or np.any(a >= field.size) or np.any(b < 0) or np.any(b >= field.size):
        raise ValueError("GF elements outside field")
    return {"values": np.vectorize(field.div, otypes=[int])(a, b)}


def gfsub(a, b, p: int = 2):
    if p < 2:
        raise ValueError("p must be a prime greater than one")
    x, y = np.broadcast_arrays(np.asarray(a, int), np.asarray(b, int))
    return {"values": (x - y) % p}


def _rref(matrix, p: int):
    a = np.asarray(matrix, int).copy() % p
    if a.ndim != 2 or not 2 <= p <= 257:
        raise ValueError("matrix must be 2-D and p a small prime")
    if any(p % divisor == 0 for divisor in range(2, int(p**.5) + 1)):
        raise ValueError("p must be prime")
    pivots, row = [], 0
    for col in range(a.shape[1]):
        pivot = next((r for r in range(row, a.shape[0]) if a[r, col]), None)
        if pivot is None:
            continue
        a[[row, pivot]] = a[[pivot, row]]
        a[row] = (a[row] * pow(int(a[row, col]), -1, p)) % p
        for r in range(a.shape[0]):
            if r != row and a[r, col]:
                a[r] = (a[r] - a[r, col] * a[row]) % p
        pivots.append(col)
        row += 1
        if row == a.shape[0]:
            break
    return a, pivots


def gfrank(matrix, p: int = 2):
    return {"rank": len(_rref(matrix, p)[1])}


def gflineq(matrix, vector, p: int = 2):
    a = np.asarray(matrix, int)
    b = np.asarray(vector, int).reshape(-1)
    if a.ndim != 2 or len(b) != a.shape[0]:
        raise ValueError("matrix rows must equal vector length")
    reduced, pivots = _rref(np.c_[a, b], p)
    if a.shape[1] in pivots:
        return {"solution": None, "valid": False}
    solution = np.zeros(a.shape[1], dtype=int)
    for row, col in enumerate(pivots):
        solution[col] = reduced[row, -1]
    return {"solution": solution, "valid": True}


def gfrepcov(exponents):
    powers = list(map(int, exponents))
    if not powers or min(powers) < 0 or len(set(powers)) != len(powers):
        raise ValueError("exponents must be unique nonnegative integers")
    out = [0] * (max(powers) + 1)
    for power in powers:
        out[power] = 1
    return {"coefficients_ascending": out}


def gfpretty(coefficients, variable: str = "x"):
    c = list(map(int, coefficients))
    if not c or any(x not in (0, 1) for x in c):
        raise ValueError("coefficients must be a binary ascending vector")
    terms = ["1" if k == 0 else variable if k == 1 else f"{variable}^{k}"
             for k, bit in enumerate(c) if bit]
    return {"polynomial": " + ".join(reversed(terms)) if terms else "0"}


def _cosets(m: int, p: int):
    if m < 1 or p < 2:
        raise ValueError("m positive and p >= 2 required")
    modulus = p**m - 1
    unseen = set(range(modulus))
    groups = []
    while unseen:
        start = min(unseen)
        group, value = [], start
        while value not in group:
            group.append(value)
            unseen.remove(value)
            value = value * p % modulus
        groups.append(group)
    return {"cosets": groups, "modulus": modulus}


def cosets(m: int):
    return _cosets(m, 2)


def gfcosets(m: int, p: int = 2):
    return _cosets(m, p)


def gfprimck(polynomial):
    poly = _polyint(polynomial)
    m = poly.bit_length() - 1
    try:
        _field(m, poly)
        valid = True
    except ValueError:
        valid = False
    return {"primitive": valid, "degree": m}


def isprimitive(polynomial):
    return gfprimck(polynomial)


def gfprimdf(m: int):
    if m not in DEFAULT_PRIMITIVES:
        raise ValueError("default primitive polynomial available for m=2..8")
    return {"polynomial": DEFAULT_PRIMITIVES[m]}


def gfprimfd(m: int, all_polynomials: bool = False):
    if not 2 <= m <= 8:
        raise ValueError("m must be 2..8")
    found = []
    for polynomial in range((1 << m) | 1, 1 << (m + 1), 2):
        if gfprimck(polynomial)["primitive"]:
            found.append(polynomial)
            if not all_polynomials:
                break
    return {"polynomials": found}


def primpoly(m: int, all_polynomials: bool = False):
    return gfprimfd(m, all_polynomials)


def gftable(m: int, primitive=None):
    field = _field(m, primitive)
    return {"exp": field.exp[:field.order], "log": field.log,
            "primitive": field.primitive}


def gftuple(values, m: int, primitive=None):
    field = _field(m, primitive)
    x = np.asarray(values, int).reshape(-1)
    if np.any(x < 0) or np.any(x >= field.size):
        raise ValueError("values outside selected field")
    powers = ((x[:, None] >> np.arange(m)) & 1).astype(int)
    return {"polynomial_coefficients_ascending": powers,
            "exponents": [field.log[int(value)] for value in x]}


def gfroots(coefficients, p: int = 2):
    c = np.asarray(coefficients, int).reshape(-1)
    if not len(c) or p < 2:
        raise ValueError("nonempty polynomial and p >= 2 required")
    roots = [x for x in range(p) if int(np.polyval(c, x)) % p == 0]
    return {"roots": roots}


def gfweight(generator):
    g = np.asarray(generator, int)
    if g.ndim != 2 or not 1 <= g.shape[0] <= 16 or np.any((g != 0) & (g != 1)):
        raise ValueError("binary generator matrix with 1..16 rows required")
    weights = [int(np.sum(np.bitwise_xor.reduce(g[list(index)], axis=0)))
               for size in range(1, g.shape[0] + 1)
               for index in itertools.combinations(range(g.shape[0]), size)]
    return {"minimum_distance": min(weights)}


def gfminpol(exponents, m: int, primitive=None):
    field = _field(m, primitive)
    groups = _cosets(m, 2)["cosets"]
    result = []
    for exponent in np.asarray(exponents, int).reshape(-1):
        target = int(exponent) % field.order
        group = next(group for group in groups if target in group)
        polynomial = [1]
        for power in group:
            polynomial = poly_mul(polynomial, [1, field.alpha(power)], field)
        if any(value not in (0, 1) for value in polynomial):
            raise ValueError("minimal polynomial did not reduce to GF(2)")
        result.append(polynomial)
    return {"polynomials_descending": result}


if __name__ == "__main__":
    run_cli("Standalone finite-field and binary-polynomial slices", {
        "gf": gf, "gfdiv": gfdiv, "gfsub": gfsub, "gflineq": gflineq,
        "gfrank": gfrank, "gfrepcov": gfrepcov, "gfpretty": gfpretty,
        "cosets": cosets, "gfcosets": gfcosets, "gfprimck": gfprimck,
        "isprimitive": isprimitive, "gfprimdf": gfprimdf,
        "gfprimfd": gfprimfd, "primpoly": primpoly, "gftable": gftable,
        "gftuple": gftuple, "gfroots": gfroots, "gfweight": gfweight,
        "gfminpol": gfminpol,
    })
