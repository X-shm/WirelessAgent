"""Small GF(2^m) helper used by the independent BCH/RS codecs."""
from __future__ import annotations


DEFAULT_PRIMITIVES = {
    2: 0x7,
    3: 0xB,
    4: 0x13,
    5: 0x25,
    6: 0x43,
    7: 0x89,
    8: 0x11D,
}


class GF2m:
    def __init__(self, m: int, primitive: int | None = None):
        if m not in DEFAULT_PRIMITIVES:
            raise ValueError("m must be between 2 and 8")
        self.m = int(m)
        self.size = 1 << self.m
        self.order = self.size - 1
        self.primitive = int(primitive or DEFAULT_PRIMITIVES[self.m])
        if self.primitive.bit_length() != self.m + 1:
            raise ValueError("primitive polynomial must have degree m")
        self.exp = [0] * (2 * self.order)
        self.log = [-1] * self.size
        x = 1
        seen = set()
        for i in range(self.order):
            if x in seen or x == 0:
                raise ValueError("polynomial is not primitive for the selected field")
            seen.add(x)
            self.exp[i] = x
            self.log[x] = i
            x <<= 1
            if x & self.size:
                x ^= self.primitive
            x &= self.order
        if x != 1 or len(seen) != self.order:
            raise ValueError("polynomial is not primitive for the selected field")
        for i in range(self.order, 2 * self.order):
            self.exp[i] = self.exp[i - self.order]

    def mul(self, x: int, y: int) -> int:
        if not x or not y:
            return 0
        return self.exp[(self.log[x] + self.log[y]) % self.order]

    def div(self, x: int, y: int) -> int:
        if y == 0:
            raise ZeroDivisionError("division by zero in GF")
        if x == 0:
            return 0
        return self.exp[(self.log[x] - self.log[y]) % self.order]

    def inv(self, x: int) -> int:
        if x == 0:
            raise ZeroDivisionError("zero has no multiplicative inverse")
        return self.exp[-self.log[x] % self.order]

    def pow(self, x: int, power: int) -> int:
        if power == 0:
            return 1
        if x == 0:
            return 0
        return self.exp[(self.log[x] * power) % self.order]

    def alpha(self, power: int) -> int:
        return self.exp[power % self.order]


def poly_add(a: list[int], b: list[int]) -> list[int]:
    length = max(len(a), len(b))
    out = [0] * length
    for i, value in enumerate(a):
        out[length - len(a) + i] ^= value
    for i, value in enumerate(b):
        out[length - len(b) + i] ^= value
    while len(out) > 1 and out[0] == 0:
        out.pop(0)
    return out


def poly_mul(a: list[int], b: list[int], gf: GF2m) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] ^= gf.mul(x, y)
    return out


def poly_eval(poly: list[int], x: int, gf: GF2m) -> int:
    value = poly[0]
    for coefficient in poly[1:]:
        value = gf.mul(value, x) ^ coefficient
    return value


def berlekamp_massey(syndromes: list[int], gf: GF2m) -> list[int]:
    """Return ascending error-locator coefficients [1, c1, ...]."""
    count = len(syndromes)
    locator = [1] + [0] * count
    previous = [1] + [0] * count
    degree = 0
    shift = 1
    last_delta = 1
    for n in range(count):
        delta = syndromes[n]
        for i in range(1, degree + 1):
            delta ^= gf.mul(locator[i], syndromes[n - i])
        if delta == 0:
            shift += 1
            continue
        saved = locator.copy()
        scale = gf.div(delta, last_delta)
        for i in range(count + 1 - shift):
            if previous[i]:
                locator[i + shift] ^= gf.mul(scale, previous[i])
        if 2 * degree <= n:
            degree = n + 1 - degree
            previous = saved
            last_delta = delta
            shift = 1
        else:
            shift += 1
    return locator[:degree + 1]


def eval_ascending(poly: list[int], x: int, gf: GF2m) -> int:
    value = 0
    power = 1
    for coefficient in poly:
        value ^= gf.mul(coefficient, power)
        power = gf.mul(power, x)
    return value


def find_error_positions(locator: list[int], word_length: int, gf: GF2m) -> list[int]:
    positions = []
    for position in range(word_length):
        exponent = word_length - 1 - position
        root = gf.alpha(-exponent)
        if eval_ascending(locator, root, gf) == 0:
            positions.append(position)
    if len(positions) != len(locator) - 1:
        raise ValueError("error locator roots do not fit the received word")
    return positions


def solve_linear(matrix: list[list[int]], vector: list[int], gf: GF2m) -> list[int]:
    n = len(vector)
    aug = [list(matrix[i]) + [vector[i]] for i in range(n)]
    for col in range(n):
        pivot = next((row for row in range(col, n) if aug[row][col]), None)
        if pivot is None:
            raise ValueError("singular error-magnitude system")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        inverse = gf.inv(aug[col][col])
        aug[col] = [gf.mul(value, inverse) for value in aug[col]]
        for row in range(n):
            if row == col or aug[row][col] == 0:
                continue
            factor = aug[row][col]
            aug[row] = [a ^ gf.mul(factor, b) for a, b in zip(aug[row], aug[col])]
    return [aug[i][-1] for i in range(n)]
