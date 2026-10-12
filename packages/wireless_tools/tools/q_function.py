"""Gaussian Q-function and inverse Q-function."""
from __future__ import annotations
import argparse
import json
import math
import statistics
import sys


def qfunc(value: float) -> float:
    return 0.5 * math.erfc(float(value) / math.sqrt(2.0))


def qfuncinv(probability: float) -> float:
    probability = float(probability)
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probabilities must be between 0 and 1")
    if probability == 0.0:
        return math.inf
    if probability == 1.0:
        return -math.inf
    return -statistics.NormalDist().inv_cdf(probability)


def _values(text: str) -> list[float]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = [item for item in text.split(",") if item.strip()]
    if not isinstance(parsed, list):
        parsed = [parsed]
    return [float(item) for item in parsed]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["qfunc", "qfuncinv"], required=True)
    parser.add_argument("--values", required=True)
    args = parser.parse_args()
    try:
        values = _values(args.values)
        output = [qfunc(value) for value in values] if args.mode == "qfunc" else [qfuncinv(value) for value in values]
        print(json.dumps({"output": output}, allow_nan=True))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
