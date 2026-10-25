"""Standalone entropy and predictive source coding slices."""
from __future__ import annotations

import heapq
import itertools

import numpy as np

from _nr_remaining_common import bits, run_cli


def huffmandict(symbols, probabilities):
    if len(symbols) != len(probabilities) or not symbols:
        raise ValueError("symbols and probabilities must be equally sized and nonempty")
    if len(set(symbols)) != len(symbols):
        raise ValueError("symbols must be unique scalars")
    p = np.asarray(probabilities, float)
    if np.any(p <= 0) or not np.isclose(np.sum(p), 1):
        raise ValueError("probabilities must be positive and sum to one")
    serial = itertools.count()
    heap = [(float(weight), next(serial), i) for i, weight in enumerate(p)]
    heapq.heapify(heap)
    if len(heap) == 1:
        return {"dictionary": [{"symbol": symbols[0], "code": [0]}], "average_length": 1.0}
    while len(heap) > 1:
        wa, _, a = heapq.heappop(heap)
        wb, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (wa + wb, next(serial), (a, b)))
    codes = [None] * len(symbols)

    def visit(node, path):
        if isinstance(node, int):
            codes[node] = path
        else:
            visit(node[0], path + [0])
            visit(node[1], path + [1])

    visit(heap[0][2], [])
    dictionary = [{"symbol": symbol, "code": code} for symbol, code in zip(symbols, codes)]
    return {"dictionary": dictionary,
            "average_length": float(np.dot(p, [len(code) for code in codes]))}


def _dictionary(dictionary):
    entries = dictionary.get("dictionary") if isinstance(dictionary, dict) else dictionary
    if not isinstance(entries, list) or not entries:
        raise ValueError("dictionary must contain symbol/code entries")
    mapping = {}
    for entry in entries:
        code = tuple(int(x) for x in entry["code"])
        if not code or any(x not in (0, 1) for x in code) or code in mapping:
            raise ValueError("invalid duplicate or empty Huffman code")
        mapping[code] = entry["symbol"]
    if any(a != b and len(a) <= len(b) and a == b[:len(a)] for a in mapping for b in mapping):
        raise ValueError("Huffman dictionary is not prefix-free")
    return mapping


def huffmanenco(data, dictionary):
    reverse = {symbol: code for code, symbol in _dictionary(dictionary).items()}
    try:
        return {"bits": [bit for symbol in data for bit in reverse[symbol]]}
    except KeyError as exc:
        raise ValueError(f"symbol outside dictionary: {exc}") from exc


def huffmandeco(encoded, dictionary):
    lookup = _dictionary(dictionary)
    stream = bits(encoded, "encoded")
    output, current = [], ()
    for bit in stream:
        current += (int(bit),)
        if current in lookup:
            output.append(lookup[current])
            current = ()
    if current:
        raise ValueError("trailing incomplete Huffman code")
    return {"symbols": output}


def _counts(counts):
    c = np.asarray(counts)
    if c.ndim != 1 or not len(c) or np.any(c < 1) or np.any(c != np.floor(c)):
        raise ValueError("counts must be positive integer frequencies")
    c = c.astype(np.int64)
    if int(c.sum()) >= 1 << 16:
        raise ValueError("counts sum must be less than 65536")
    return np.r_[0, np.cumsum(c)].astype(int)


def arithenco(data, counts):
    """32-bit binary arithmetic coder for MATLAB-style 1-based symbol IDs."""
    cumulative = _counts(counts)
    total = int(cumulative[-1])
    low, high, pending = 0, 0xFFFFFFFF, 0
    output = []

    def emit(bit):
        nonlocal pending
        output.append(bit)
        output.extend([1 - bit] * pending)
        pending = 0

    for symbol in data:
        if type(symbol) is not int or not 1 <= symbol < len(cumulative):
            raise ValueError("data symbols must be 1..len(counts)")
        span = high - low + 1
        high = low + span * cumulative[symbol] // total - 1
        low = low + span * cumulative[symbol - 1] // total
        while True:
            if high < 0x80000000:
                emit(0)
            elif low >= 0x80000000:
                emit(1)
                low -= 0x80000000
                high -= 0x80000000
            elif low >= 0x40000000 and high < 0xC0000000:
                pending += 1
                low -= 0x40000000
                high -= 0x40000000
            else:
                break
            low = (low << 1) & 0xFFFFFFFF
            high = ((high << 1) | 1) & 0xFFFFFFFF
    pending += 1
    emit(0 if low < 0x40000000 else 1)
    return {"bits": output}


def arithdeco(encoded, counts, length: int):
    cumulative = _counts(counts)
    if length < 0:
        raise ValueError("length must be nonnegative")
    stream = [int(x) for x in encoded]
    if any(x not in (0, 1) for x in stream):
        raise ValueError("encoded must be binary")
    cursor = 0

    def next_bit():
        nonlocal cursor
        value = stream[cursor] if cursor < len(stream) else 0
        cursor += 1
        return value

    value = 0
    for _ in range(32):
        value = (value << 1) | next_bit()
    low, high, total = 0, 0xFFFFFFFF, int(cumulative[-1])
    decoded = []
    for _ in range(length):
        span = high - low + 1
        scaled = ((value - low + 1) * total - 1) // span
        symbol = int(np.searchsorted(cumulative, scaled, side="right"))
        if not 1 <= symbol < len(cumulative):
            raise ValueError("invalid arithmetic stream")
        decoded.append(symbol)
        high = low + span * cumulative[symbol] // total - 1
        low = low + span * cumulative[symbol - 1] // total
        while True:
            if high < 0x80000000:
                pass
            elif low >= 0x80000000:
                value -= 0x80000000
                low -= 0x80000000
                high -= 0x80000000
            elif low >= 0x40000000 and high < 0xC0000000:
                value -= 0x40000000
                low -= 0x40000000
                high -= 0x40000000
            else:
                break
            low = (low << 1) & 0xFFFFFFFF
            high = ((high << 1) | 1) & 0xFFFFFFFF
            value = ((value << 1) | next_bit()) & 0xFFFFFFFF
    return {"symbols": decoded}


def lloyds(samples, levels: int, iterations: int = 100, tolerance: float = 1e-10):
    x = np.asarray(samples, float).reshape(-1)
    if not len(x) or np.any(~np.isfinite(x)) or not 1 <= levels <= len(x):
        raise ValueError("finite samples and 1 <= levels <= sample count required")
    if iterations < 1 or tolerance <= 0:
        raise ValueError("iterations and tolerance must be positive")
    codebook = np.quantile(x, (np.arange(levels) + .5) / levels)
    for _ in range(iterations):
        partition = (codebook[:-1] + codebook[1:]) / 2
        indices = np.searchsorted(partition, x, side="left")
        updated = np.array([np.mean(x[indices == k]) if np.any(indices == k) else codebook[k]
                            for k in range(levels)])
        if np.max(abs(updated - codebook)) <= tolerance:
            codebook = updated
            break
        codebook = updated
    partition = (codebook[:-1] + codebook[1:]) / 2
    indices = np.searchsorted(partition, x, side="left")
    return {"partition": partition, "codebook": codebook,
            "distortion": float(np.mean((x - codebook[indices])**2))}


def dpcmopt(samples, order: int, levels: int):
    x = np.asarray(samples, float).reshape(-1)
    if order < 0 or len(x) <= order or np.any(~np.isfinite(x)):
        raise ValueError("finite samples and 0 <= order < sample count required")
    if order:
        design = np.array([x[t - order:t][::-1] for t in range(order, len(x))])
        predictor = np.linalg.lstsq(design, x[order:], rcond=None)[0]
        residual = x[order:] - design @ predictor
    else:
        predictor, residual = np.array([]), x
    q = lloyds(residual, levels)
    return {"predictor": predictor, **q}


def _dpcm(indices_or_samples, codebook, predictor, encode):
    values = np.asarray(indices_or_samples).reshape(-1)
    c = np.asarray(codebook, float).reshape(-1)
    p = np.asarray(predictor, float).reshape(-1)
    if not len(c) or np.any(~np.isfinite(c)) or np.any(~np.isfinite(p)):
        raise ValueError("finite nonempty codebook and finite predictor required")
    if encode and np.any(~np.isfinite(values.astype(float))):
        raise ValueError("samples must be finite")
    if not encode and (np.any(values != np.floor(values)) or np.any(values < 0) or np.any(values >= len(c))):
        raise ValueError("indices outside codebook")
    partition = (c[:-1] + c[1:]) / 2
    reconstructed, indices = [], []
    for value in values:
        prediction = sum(p[k] * reconstructed[-k - 1] for k in range(min(len(p), len(reconstructed))))
        index = int(np.searchsorted(partition, float(value) - prediction, side="left")) if encode else int(value)
        indices.append(index)
        reconstructed.append(float(c[index] + prediction))
    return {"indices": indices, "samples": reconstructed}


def dpcmenco(samples, codebook, predictor=()):
    return _dpcm(samples, codebook, predictor, True)


def dpcmdeco(indices, codebook, predictor=()):
    return _dpcm(indices, codebook, predictor, False)


if __name__ == "__main__":
    run_cli("Standalone entropy and predictive source coding slices", {
        "huffmandict": huffmandict, "huffmanenco": huffmanenco,
        "huffmandeco": huffmandeco, "arithenco": arithenco,
        "arithdeco": arithdeco, "lloyds": lloyds,
        "dpcmopt": dpcmopt, "dpcmenco": dpcmenco, "dpcmdeco": dpcmdeco,
    })
