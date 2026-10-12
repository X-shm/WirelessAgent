"""Coded BPSK BER bounds for convolutional, block and Hamming codes."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np


def _q(value):
    return 0.5*math.erfc(value/math.sqrt(2.0))


def ber_coding(ebno_db, coding, decision="hard", code_rate=None, d_free=None, weights=None, n=None, k=None, d_min=None):
    scalar = np.isscalar(ebno_db)
    ebnos = np.asarray(ebno_db, dtype=float).reshape(-1)
    mode, decision = coding.lower(), decision.lower()
    output = []
    for db in ebnos:
        gamma = 10**(float(db)/10.0)
        if mode == "conv":
            if code_rate is None or d_free is None or not weights:
                raise ValueError("conv mode requires code_rate, d_free and weights")
            rate, first = float(code_rate), int(d_free)
            if not 0 < rate <= 1 or first < 1:
                raise ValueError("invalid convolutional code rate or free distance")
            bound = 0.0
            if decision == "soft":
                for offset, weight in enumerate(weights):
                    distance = first+offset
                    bound += float(weight)*_q(math.sqrt(2*gamma*rate*distance))
            elif decision == "hard":
                p = _q(math.sqrt(2*gamma*rate))
                for offset, weight in enumerate(weights):
                    distance, pairwise = first+offset, 0.0
                    for errors in range(distance//2+1, distance+1):
                        pairwise += math.comb(distance, errors)*p**errors*(1-p)**(distance-errors)
                    if distance % 2 == 0:
                        pairwise += 0.5*math.comb(distance, distance//2)*(p*(1-p))**(distance//2)
                    bound += float(weight)*pairwise
            else:
                raise ValueError("decision must be hard or soft")
        elif mode in ("block", "hamming"):
            if n is None:
                raise ValueError("block/Hamming mode requires n")
            n = int(n)
            if mode == "hamming":
                m = round(math.log2(n+1))
                if 2**m-1 != n or m < 2 or decision != "hard":
                    raise ValueError("Hamming hard mode requires n=2^m-1")
                k_value, d_value = n-m, 3
            else:
                if k is None or d_min is None:
                    raise ValueError("block mode requires k and d_min")
                k_value, d_value = int(k), int(d_min)
                if not 0 < k_value <= n or not 1 <= d_value <= n-k_value+1:
                    raise ValueError("invalid block-code dimensions or minimum distance")
            rate = k_value/n
            p = _q(math.sqrt(2*gamma*rate))
            if mode == "hamming":
                bound = p-p*(1-p)**(n-1)
            elif decision == "hard":
                t = (d_value-1)//2
                bound = sum((errors+t)*math.comb(n, errors)*p**errors*(1-p)**(n-errors) for errors in range(t+1, n+1))/n
            elif decision == "soft":
                bound = 0.5*(2**k_value-1)*_q(math.sqrt(2*gamma*rate*d_value))
            else:
                raise ValueError("decision must be hard or soft")
        else:
            raise ValueError("coding must be conv, block or hamming")
        output.append(float(min(max(bound, 0.0), 1.0)))
    return output[0] if scalar else output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ebno_db", required=True)
    parser.add_argument("--coding", choices=["conv", "block", "hamming"], required=True)
    parser.add_argument("--decision", choices=["hard", "soft"], default="hard")
    parser.add_argument("--code_rate", type=float)
    parser.add_argument("--d_free", type=int)
    parser.add_argument("--weights")
    parser.add_argument("--n", type=int)
    parser.add_argument("--k", type=int)
    parser.add_argument("--d_min", type=int)
    args = parser.parse_args()
    try:
        ebno = json.loads(args.ebno_db)
        weights = None if args.weights is None else json.loads(args.weights)
        result = ber_coding(ebno, args.coding, args.decision, args.code_rate, args.d_free, weights, args.n, args.k, args.d_min)
        print(json.dumps({"ebno_db": ebno, "ber_bound": result, "coding": args.coding, "decision": args.decision}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
