"""Coherent BPSK/QPSK BER over Rayleigh or Rician fading with MRC diversity."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np


def ber_fading(ebno_db, modulation="BPSK", diversity_order=1, fading="Rayleigh", k_factor=0.0):
    values = np.asarray(ebno_db, dtype=float).reshape(-1)
    diversity_order, k_factor = int(diversity_order), float(k_factor)
    if modulation.upper() not in ("BPSK", "QPSK") or diversity_order < 1:
        raise ValueError("supported modulation is coherent BPSK/QPSK and diversity_order >= 1")
    if fading.lower() not in ("rayleigh", "rician") or k_factor < 0:
        raise ValueError("fading must be Rayleigh/Rician and k_factor nonnegative")
    gamma = 10**(values/10.0)
    theta = np.linspace(1e-7, math.pi/2, 20001)
    sin2 = np.sin(theta)**2
    output = []
    for average_snr in gamma:
        s = -1.0/sin2
        if fading.lower() == "rayleigh":
            mgf = (1-average_snr*s)**(-diversity_order)
        else:
            denominator = 1+k_factor-average_snr*s
            branch = (1+k_factor)/denominator*np.exp(k_factor*average_snr*s/denominator)
            mgf = branch**diversity_order
        output.append(float(np.trapezoid(mgf, theta)/math.pi))
    return output[0] if np.isscalar(ebno_db) else output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ebno_db", required=True)
    parser.add_argument("--modulation", choices=["BPSK", "QPSK"], default="BPSK")
    parser.add_argument("--diversity_order", type=int, default=1)
    parser.add_argument("--fading", choices=["Rayleigh", "Rician"], default="Rayleigh")
    parser.add_argument("--k_factor", type=float, default=0.0)
    args = parser.parse_args()
    try:
        raw = json.loads(args.ebno_db)
        result = ber_fading(raw, args.modulation, args.diversity_order, args.fading, args.k_factor)
        print(json.dumps({"ebno_db": raw, "ber": result, "modulation": args.modulation, "fading": args.fading}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
