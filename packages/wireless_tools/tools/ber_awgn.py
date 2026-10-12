"""Analytical uncoded BER/SER for common modulations in AWGN."""
from __future__ import annotations
import argparse
import json
import math
import sys

from q_function import qfunc


def ber_awgn(ebno_db, modulation: str, order: int = 2, differential: bool = False, coherence: str = "coherent"):
    values = [float(value) for value in ebno_db]
    modulation = modulation.lower()
    if order < 2 or order & (order - 1):
        raise ValueError("order must be a power of two >= 2")
    k = math.log2(order)
    if modulation == "qam" and int(math.isqrt(order)) ** 2 != order:
        raise ValueError("QAM order must be square")
    ber, ser = [], []
    for db in values:
        gamma = 10.0 ** (db / 10.0)
        if modulation in ("bpsk", "qpsk"):
            actual_order = 2 if modulation == "bpsk" else 4
            if order not in (actual_order, 2) and modulation == "qpsk":
                raise ValueError("qpsk order must be 4")
            if differential:
                if actual_order == 2:
                    error = 0.5 * math.exp(-gamma)
                    bit_error, symbol_error = error, error
                else:
                    q = qfunc(math.sqrt(2.0 * gamma))
                    bit_error = 2.0 * (q - q * q)
                    symbol_error = 4.0 * (q - 2*q*q + 2*q**3 - q**4)
            else:
                q = qfunc(math.sqrt(2.0 * gamma))
                bit_error = q
                symbol_error = q if actual_order == 2 else 2.0*q - q*q
        elif modulation == "psk":
            if order == 2:
                bit_error = symbol_error = qfunc(math.sqrt(2.0 * gamma))
            elif order == 4:
                q = qfunc(math.sqrt(2.0 * gamma))
                bit_error, symbol_error = q, 2.0*q - q*q
            else:
                argument = math.sqrt(2.0 * k * gamma) * math.sin(math.pi / order)
                symbol_error = min(1.0, 2.0 * qfunc(argument))
                bit_error = symbol_error / k
        elif modulation == "pam":
            argument = math.sqrt(6.0 * k * gamma / (order * order - 1.0))
            symbol_error = 2.0 * (order - 1.0) / order * qfunc(argument)
            bit_error = symbol_error / k
        elif modulation == "qam":
            root = math.sqrt(order)
            q = qfunc(math.sqrt(3.0 * k * gamma / (order - 1.0)))
            symbol_error = 1.0 - (1.0 - 2.0 * (1.0 - 1.0/root) * q) ** 2
            bit_error = 4.0 / k * (1.0 - 1.0/root) * q
        elif modulation == "dpsk":
            if order != 2:
                raise ValueError("independent DPSK coverage currently supports order 2")
            bit_error = symbol_error = 0.5 * math.exp(-gamma)
        elif modulation == "fsk":
            if order != 2:
                raise ValueError("independent FSK coverage currently supports binary orthogonal FSK")
            if coherence == "coherent":
                bit_error = symbol_error = qfunc(math.sqrt(gamma))
            elif coherence == "noncoherent":
                bit_error = symbol_error = 0.5 * math.exp(-gamma / 2.0)
            else:
                raise ValueError("coherence must be coherent or noncoherent")
        else:
            raise ValueError("unsupported modulation")
        ber.append(float(bit_error))
        ser.append(float(symbol_error))
    return ber, ser


def _values(text: str) -> list[float]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        value = [item for item in text.split(",") if item.strip()]
    if not isinstance(value, list):
        value = [value]
    return [float(item) for item in value]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ebno_db", required=True)
    parser.add_argument("--modulation", choices=["bpsk", "qpsk", "psk", "pam", "qam", "dpsk", "fsk"], required=True)
    parser.add_argument("--order", type=int, default=2)
    parser.add_argument("--differential", action="store_true")
    parser.add_argument("--coherence", choices=["coherent", "noncoherent"], default="coherent")
    args = parser.parse_args()
    try:
        ber, ser = ber_awgn(_values(args.ebno_db), args.modulation, args.order, args.differential, args.coherence)
        print(json.dumps({"ber": ber, "ser": ser}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
