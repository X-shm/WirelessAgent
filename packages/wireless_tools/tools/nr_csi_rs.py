"""nr_csi_rs - 5G NR CSI-RS sequence generator (simplified).

Implements TS 38.211 Section 7.4.1.5 CSI-RS sequence generation.
MATLAB equivalent: nrCSIRS (simplified)

The cinit formula:
  cinit = (2^10 * (Nsymb*slot + l + 1) * (2*nID + 1) + nID) mod 2^31
"""
from __future__ import annotations
import argparse
import json
import sys
import numpy as np

from nr_prbs import prbs


def csi_rs_rb_indices(nprb: int, density: int = 1) -> np.ndarray:
    """Return the contiguous RBs occupied by this single-port subset.

    The interface has no RB offset, so the allocation is anchored at RB 0.
    Density code 0 represents standard density 0.5 and selects even RBs.
    """
    if nprb <= 0:
        raise ValueError("nprb must be positive")
    if density not in (0, 1, 3):
        raise ValueError("density must be 0 (0.5), 1, or 3")
    step = 2 if density == 0 else 1
    return np.arange(0, nprb, step, dtype=int)


def csi_rs_sequence(nid: int, nslot: int, nsym: int,
                    nprb: int, density: int = 1) -> np.ndarray:
    """Generate CSI-RS QPSK symbols for given parameters.

    Args:
        nid: CSI-RS scrambling identity (0..1023)
        nslot: slot number
        nsym: OFDM symbol number (the l value for cinit)
        nprb: number of RBs for CSI-RS
        density: 1, 3, or 0 (0.5 → use 0, handled by caller)

    Returns:
        Complex QPSK CSI-RS symbols
    """
    # cinit per TS 38.211 7.4.1.5.1
    cinit = int((2**10 * (14 * nslot + nsym + 1) * (2 * nid + 1) + nid) % (2**31))

    rb_indices = csi_rs_rb_indices(nprb, density)
    # This single-port subset models one RE/RB at rho=1, three RE/RB at
    # rho=3, and one RE in every second RB at rho=0.5.
    n_re = len(rb_indices) * (3 if density == 3 else 1)
    total_bits = 2 * n_re

    seq = prbs(cinit, total_bits)

    # QPSK modulation
    bits = seq.reshape(-1, 2).astype(float)
    real = (1 - 2 * bits[:, 0]) / np.sqrt(2)
    imag = (1 - 2 * bits[:, 1]) / np.sqrt(2)
    return (real + 1j * imag).astype(np.complex128)


def main():
    parser = argparse.ArgumentParser(description="5G NR CSI-RS generator (TS 38.211 Sec 7.4.1.5)")
    parser.add_argument("--nid", type=int, required=True, help="CSI-RS scrambling identity (0..1023)")
    parser.add_argument("--nslot", type=int, default=0, help="Slot number")
    parser.add_argument("--nsym", type=int, default=0, help="OFDM symbol (l value)")
    parser.add_argument("--nprb", type=int, required=True, help="Number of RBs")
    parser.add_argument("--density", type=int, default=1, choices=[0, 1, 3],
                        help="Density (0=0.5, 1=1, 3=3)")
    args = parser.parse_args()

    try:
        sym = csi_rs_sequence(args.nid, args.nslot, args.nsym, args.nprb, args.density)
        result = {
            "nid": args.nid,
            "nslot": args.nslot,
            "nsym": args.nsym,
            "nprb": args.nprb,
            "density": args.density,
            "rb_indices": csi_rs_rb_indices(args.nprb, args.density).tolist(),
            "n_re": len(sym),
            "cinit": int((2**10 * (14 * args.nslot + args.nsym + 1) * (2 * args.nid + 1) + args.nid) % (2**31)),
            "sym_real": sym.real.tolist(),
            "sym_imag": sym.imag.tolist(),
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
