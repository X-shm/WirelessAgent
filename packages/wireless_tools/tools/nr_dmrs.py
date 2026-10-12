"""nr_dmrs - 5G NR PDSCH DM-RS sequence generator (simplified).

Implements TS 38.211 Section 7.4.1.1.1 DM-RS sequence generation.
MATLAB equivalent: nrPDSCHDMRS (simplified, config type 1, single layer)

The cinit formula:
  cinit = (2^17 * (Nsymb*slot + sym + 1) * (2*nid + 1) + 2*nid + nscid) mod 2^31
"""
from __future__ import annotations
import argparse
import json
import sys
import numpy as np

# Import our PRBS generator
from nr_prbs import prbs


def dmrs_sequence(ncellid: int, nscid: int, nslot: int, nsym: int,
                  nprb: int, config_type: int = 1,
                  nsymbols: int = 1) -> np.ndarray:
    """Generate PDSCH DM-RS QPSK symbols for given parameters.

    Args:
        ncellid: physical cell ID (0..1007), used as nid if NIDNSCID not set
        nscid: scrambling initialization (0 or 1)
        nslot: slot number
        nsym: OFDM symbol number within slot (0-based)
        nprb: number of allocated PRBs
        config_type: 1 or 2 (DM-RS configuration type)
        nsymbols: number of DM-RS OFDM symbols

    Returns:
        Complex QPSK DM-RS symbols, shape (nprb * ndmrs_per_rb * nsymbols,)
    """
    if config_type not in (1, 2):
        raise ValueError("config_type must be 1 or 2")
    if nscid not in (0, 1):
        raise ValueError("nscid must be 0 or 1")
    if nprb <= 0 or nsymbols <= 0:
        raise ValueError("nprb and nsymbols must be positive")

    # DM-RS REs per RB: type 1 = 6, type 2 = 4
    if config_type == 1:
        ndmrs_re = 6
    else:
        ndmrs_re = 4

    symbols: list[np.ndarray] = []
    for symbol_offset in range(nsymbols):
        # The initialization uses the actual OFDM-symbol number.  A contiguous
        # multi-symbol request therefore produces one independent PRBS segment
        # per DM-RS symbol rather than repeating the first segment.
        ofdm_symbol = nsym + symbol_offset
        cinit = int(
            (
                2**17 * (14 * nslot + ofdm_symbol + 1) * (2 * ncellid + 1)
                + 2 * ncellid
                + nscid
            )
            % (2**31)
        )
        bits = prbs(cinit, 2 * ndmrs_re * nprb).reshape(-1, 2).astype(float)
        real = (1 - 2 * bits[:, 0]) / np.sqrt(2)
        imag = (1 - 2 * bits[:, 1]) / np.sqrt(2)
        symbols.append((real + 1j * imag).astype(np.complex128))

    return np.concatenate(symbols)


def dmrs_subcarrier_locations(config_type: int = 1, port: int = 0) -> np.ndarray:
    """Get DM-RS subcarrier locations within a PRB (0-based, within 12 REs).

    Args:
        config_type: 1 or 2
        port: antenna port (0..11 for type 1, 0..23 for type 2)

    Returns:
        Array of subcarrier indices within a PRB
    """
    if config_type == 1:
        # Type 1: delta shift depends on CDM group
        # Port 0,4,8 → CDM group 0 → delta=0 → k=0,2,4,6,8,10
        # Port 1,5,9 → CDM group 1 → delta=1 → k=1,3,5,7,9,11
        cdm_group = (port // 4) % 2
        delta = cdm_group
        return np.arange(0, 12, 2) + delta
    else:
        # Type 2: 4 REs per RB per CDM group (TS 38.211 Table
        # 7.4.1.1.2-1).  k' takes 0 and 1, in both 6-subcarrier bundles.
        cdm_group = (port // 2) % 3
        deltas = [0, 2, 4]
        return np.array([0, 1, 6, 7], dtype=int) + deltas[cdm_group]


def main():
    parser = argparse.ArgumentParser(description="5G NR PDSCH DM-RS generator (TS 38.211 Sec 7.4.1.1.1)")
    parser.add_argument("--ncellid", type=int, required=True, help="Physical cell ID")
    parser.add_argument("--nscid", type=int, default=0, choices=[0, 1], help="Scrambling init")
    parser.add_argument("--nslot", type=int, default=0, help="Slot number")
    parser.add_argument("--nsym", type=int, default=0, help="OFDM symbol in slot (0-based)")
    parser.add_argument("--nprb", type=int, required=True, help="Number of PRBs")
    parser.add_argument("--config-type", type=int, default=1, choices=[1, 2])
    parser.add_argument("--nsymbols", type=int, default=1, help="Number of DM-RS symbols")
    args = parser.parse_args()

    try:
        sym = dmrs_sequence(args.ncellid, args.nscid, args.nslot, args.nsym,
                            args.nprb, args.config_type, args.nsymbols)
        loc = dmrs_subcarrier_locations(args.config_type, 0)
        result = {
            "ncellid": args.ncellid,
            "nscid": args.nscid,
            "nslot": args.nslot,
            "nsym": args.nsym,
            "nprb": args.nprb,
            "config_type": args.config_type,
            "cinit": int((2**17 * (14 * args.nslot + args.nsym + 1) * (2 * args.ncellid + 1) + 2 * args.ncellid + args.nscid) % (2**31)),
            "ndmrs_re_per_rb": 6 if args.config_type == 1 else 4,
            "nsymbols": args.nsymbols,
            "subcarrier_locations": loc.tolist(),
            "sym_real": sym.real.tolist(),
            "sym_imag": sym.imag.tolist(),
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
