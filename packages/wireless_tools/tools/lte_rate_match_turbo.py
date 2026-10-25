"""TS 36.212 Turbo subblock interleaving and circular-buffer rate matching."""
from __future__ import annotations

import math
import numpy as np

_P = np.asarray([0, 16, 8, 24, 4, 20, 12, 28, 2, 18, 10, 26, 6, 22, 14, 30,
                 1, 17, 9, 25, 5, 21, 13, 29, 3, 19, 11, 27, 7, 23, 15, 31])


def _interleaver_positions(length: int, third: bool) -> np.ndarray:
    rows = math.ceil(length/32)
    total = rows*32
    if third:
        return (_P[np.arange(total)//rows] + 32*(np.arange(total) % rows) + 1) % total
    return np.arange(total).reshape(rows, 32)[:, _P].T.reshape(-1)


def circular_positions(block_size: int, output_length: int, rv: int,
                       filler_count: int = 0, ncb: int | None = None):
    if block_size < 40 or block_size > 6144 or output_length < 0 or rv not in (0, 1, 2, 3):
        raise ValueError("invalid Turbo block size, output length, or redundancy version")
    if not 0 <= filler_count <= block_size:
        raise ValueError("invalid filler count")
    data_length = block_size+4
    rows = math.ceil(data_length/32)
    total = 32*rows
    valid = np.ones((3, data_length), dtype=bool)
    valid[0, :filler_count] = False
    valid[1, :filler_count] = False
    padded = np.pad(valid, ((0, 0), (total-data_length, 0)),
                    constant_values=False)
    first = padded[0, _interleaver_positions(data_length, False)]
    second = padded[1, _interleaver_positions(data_length, False)]
    third = padded[2, _interleaver_positions(data_length, True)]
    mask = np.empty(3*total, dtype=bool)
    mask[:total] = first
    mask[total::2] = second
    mask[total+1::2] = third
    count = len(mask) if ncb is None else int(ncb)
    if not 1 <= count <= len(mask) or not np.any(mask[:count]):
        raise ValueError("invalid circular-buffer size")
    start = rows*(2*math.ceil(count/(8*rows))*rv+2)
    selected = []
    offset = 0
    while len(selected) < output_length:
        position = (start+offset) % count
        if mask[position]:
            selected.append(position)
        offset += 1
    return np.asarray(selected, dtype=int), total, mask


def rate_match(bits, length: int, rv: int = 0, ncb: int | None = None) -> np.ndarray:
    raw = np.asarray(bits, dtype=int).reshape(-1)
    if len(raw) % 3:
        raise ValueError("Turbo coded input must have three equal streams")
    block_size = len(raw)//3 - 4
    if np.any(raw > 1):
        raise ValueError("coded bits must be binary or negative filler")
    filler = 0
    systematic = raw[:block_size]
    while filler < block_size and systematic[filler] < 0:
        filler += 1
    data_length = block_size+4
    rows = math.ceil(data_length/32)
    total = rows*32
    streams = raw.reshape(3, data_length)
    padded = np.pad(streams, ((0, 0), (total-data_length, 0)), constant_values=-1)
    first = padded[0, _interleaver_positions(data_length, False)]
    second = padded[1, _interleaver_positions(data_length, False)]
    third = padded[2, _interleaver_positions(data_length, True)]
    circular = np.empty(3*total, dtype=int)
    circular[:total] = first
    circular[total::2] = second
    circular[total+1::2] = third
    positions, _, mask = circular_positions(block_size, int(length), int(rv), filler, ncb)
    if np.any((circular[positions] < 0) | (~mask[positions])):
        raise RuntimeError("Turbo rate matcher selected NULL bits")
    return circular[positions]


def rate_recover(soft_bits, block_size: int, rv: int = 0,
                 filler_count: int = 0, ncb: int | None = None) -> np.ndarray:
    soft = np.asarray(soft_bits, dtype=float).reshape(-1)
    if not np.all(np.isfinite(soft)):
        raise ValueError("soft bits must be finite")
    positions, total, _ = circular_positions(
        int(block_size), len(soft), int(rv), int(filler_count), ncb)
    circular = np.zeros(3*total, dtype=float)
    np.add.at(circular, positions, soft)
    data_length = int(block_size)+4
    padded = np.zeros((3, total), dtype=float)
    common = _interleaver_positions(data_length, False)
    special = _interleaver_positions(data_length, True)
    padded[0, common] = circular[:total]
    padded[1, common] = circular[total::2]
    padded[2, special] = circular[total+1::2]
    return padded[:, total-data_length:].reshape(-1)
