"""Square Gray/binary QAM modulation and hard-decision demodulation."""
from __future__ import annotations
import argparse, json, math, sys
import numpy as np


def _gray_decode(value):
    result = 0
    while value:
        result ^= value
        value >>= 1
    return result


def _labels(values, width):
    return np.array([[(int(v) >> shift) & 1 for shift in range(width - 1, -1, -1)] for v in values], dtype=int)


def constellation(order, symbol_order="gray", unit_average_power=False):
    order = int(order)
    side = int(math.isqrt(order))
    if side * side != order or side < 2 or side & (side - 1):
        raise ValueError("order must be a square power of two (4,16,64,...)")
    width = int(math.log2(side))
    points = np.empty(order, dtype=np.complex128)
    for label in range(order):
        i_label, q_label = label >> width, label & (side - 1)
        i_index = _gray_decode(i_label) if symbol_order == "gray" else i_label
        q_index = _gray_decode(q_label) if symbol_order == "gray" else q_label
        points[label] = (2 * i_index - side + 1) + 1j * (side - 1 - 2 * q_index)
    if unit_average_power:
        points /= math.sqrt(2 * (order - 1) / 3)
    return points


def qam_modulate(values, order, input_type="bits", symbol_order="gray", unit_average_power=False):
    table = constellation(order, symbol_order, unit_average_power)
    width = int(math.log2(order))
    if input_type == "bits":
        bits = np.asarray(values, dtype=int).reshape(-1)
        if np.any((bits != 0) & (bits != 1)) or len(bits) % width:
            raise ValueError(f"bits must be binary and length divisible by {width}")
        labels = np.array([sum(int(bit) << (width - 1 - j) for j, bit in enumerate(row))
                           for row in bits.reshape(-1, width)], dtype=int)
    else:
        labels = np.asarray(values, dtype=int).reshape(-1)
    if np.any(labels < 0) or np.any(labels >= order):
        raise ValueError("symbol labels out of range")
    return table[labels], labels


def qam_demodulate(symbols, order, output_type="bits", symbol_order="gray", unit_average_power=False):
    table = constellation(order, symbol_order, unit_average_power)
    symbols = np.asarray(symbols, dtype=np.complex128).reshape(-1)
    labels = np.argmin(np.abs(symbols[:, None] - table[None, :]) ** 2, axis=1)
    return _labels(labels, int(math.log2(order))).reshape(-1) if output_type == "bits" else labels


def _complex(text):
    raw = json.loads(text)
    return np.asarray(raw["real"]) + 1j * np.asarray(raw["imag"])


def main():
    p = argparse.ArgumentParser(description="Square QAM modulation/demodulation")
    p.add_argument("--mode", required=True, choices=("modulate", "demodulate"))
    p.add_argument("--order", required=True, type=int)
    p.add_argument("--values", required=True, help="comma bits/symbols or real/imag JSON")
    p.add_argument("--input_type", choices=("bits", "symbols"), default="bits")
    p.add_argument("--output_type", choices=("bits", "symbols"), default="bits")
    p.add_argument("--symbol_order", choices=("gray", "binary"), default="gray")
    p.add_argument("--unit_average_power", action="store_true")
    a = p.parse_args()
    try:
        if a.mode == "modulate":
            values = [int(v) for v in a.values.split(",")]
            out, labels = qam_modulate(values, a.order, a.input_type, a.symbol_order, a.unit_average_power)
            result = {"labels": labels.tolist(), "symbols_real": out.real.tolist(), "symbols_imag": out.imag.tolist()}
        else:
            out = qam_demodulate(_complex(a.values), a.order, a.output_type, a.symbol_order, a.unit_average_power)
            result = {"output_type": a.output_type, "values": out.tolist()}
        print(json.dumps(result))
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False)); sys.exit(1)


if __name__ == "__main__": main()
