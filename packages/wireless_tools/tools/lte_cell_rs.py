"""LTE cell-specific reference signals and RE indices (TS 36.211 6.10.1)."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from lte_prbs import lte_prbs


def _validate(nrb, ncellid, nsubframe, cyclic_prefix, ports):
    nrb, ncellid, nsubframe = int(nrb), int(ncellid), int(nsubframe)
    cp = cyclic_prefix.lower()
    ports = [int(port) for port in ports]
    if not 1 <= nrb <= 110 or not 0 <= ncellid <= 503 or not 0 <= nsubframe <= 9:
        raise ValueError("nrb 1..110, ncellid 0..503 and nsubframe 0..9 required")
    if cp not in ("normal", "extended") or any(port not in (0, 1, 2, 3) for port in ports):
        raise ValueError("cyclic_prefix must be Normal/Extended and ports in 0..3")
    return nrb, ncellid, nsubframe, cp, ports


def _symbol_sequence(nrb: int, ncellid: int, slot: int, symbol_in_slot: int, cp: str):
    ncp = 1 if cp == "normal" else 0
    cinit = (1 << 10) * (7 * (slot + 1) + symbol_in_slot + 1) * (2 * ncellid + 1) + 2 * ncellid + ncp
    bits = lte_prbs(cinit, 440)
    full = ((1 - 2*bits[0::2]) + 1j*(1 - 2*bits[1::2])) / math.sqrt(2.0)
    start = 110 - nrb
    return full[start:start + 2*nrb]


def cell_rs(nrb, ncellid, nsubframe=0, cyclic_prefix="Normal", ports=(0,)):
    nrb, ncellid, nsubframe, cp, ports = _validate(nrb, ncellid, nsubframe, cyclic_prefix, ports)
    symbols_per_slot = 7 if cp == "normal" else 6
    output = {}
    for port in ports:
        indices = []
        values = []
        for slot_in_subframe in (0, 1):
            slot = 2*nsubframe + slot_in_subframe
            rs_symbols = (0, symbols_per_slot-3) if port in (0, 1) else (1,)
            for symbol_in_slot in rs_symbols:
                if port == 0:
                    v = 0 if symbol_in_slot == 0 else 3
                elif port == 1:
                    v = 3 if symbol_in_slot == 0 else 0
                elif port == 2:
                    v = 3 * (slot % 2)
                else:
                    v = (3 + 3 * (slot % 2)) % 6
                shift = ncellid % 6
                carriers = 6*np.arange(2*nrb) + ((v + shift) % 6)
                global_symbol = slot_in_subframe*symbols_per_slot + symbol_in_slot
                sequence = _symbol_sequence(nrb, ncellid, slot, symbol_in_slot, cp)
                indices.extend([[int(carrier), int(global_symbol), port] for carrier in carriers])
                values.extend(sequence.tolist())
        output[port] = {"indices": np.asarray(indices, dtype=int), "symbols": np.asarray(values, dtype=complex)}
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nrb", type=int, required=True)
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--nsubframe", type=int, default=0)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--ports", default="0")
    args = parser.parse_args()
    try:
        ports = [int(value) for value in args.ports.split(",") if value.strip()]
        result = {}
        for port, data in cell_rs(args.nrb, args.ncellid, args.nsubframe, args.cyclic_prefix, ports).items():
            result[str(port)] = {"indices": data["indices"].tolist(), "symbols_real": data["symbols"].real.tolist(), "symbols_imag": data["symbols"].imag.tolist()}
        print(json.dumps({"ports": result, "index_base": 0}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
