"""Release 8/9 LTE FDD PDSCH RE indices with control/CRS/sync/PBCH avoidance."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _lte_resource_helpers import modulation_order, slot_prbs
from lte_cell_rs import cell_rs


_SCHEMES = {"port0", "txdiversity", "cdd", "spatialmux", "multiuser"}


def _coded_bits(gd, modulations, n_layers):
    mods = [item.strip() for item in modulations.split(",") if item.strip()]
    if len(mods) not in (1, 2):
        raise ValueError("modulation must contain one or two comma-separated formats")
    if len(mods) == 1:
        return [gd*modulation_order(mods[0])*n_layers]
    if n_layers < 2:
        raise ValueError("two codewords require at least two layers")
    layer_counts = [n_layers//2, n_layers-n_layers//2]
    return [gd*modulation_order(mods[i])*layer_counts[i] for i in range(2)]


def pdsch_indices(ndlrb, ncellid, prb_set, nsubframe=0, cfi=1, cyclic_prefix="Normal", cell_ref_p=1, tx_scheme="Port0", modulation="QPSK", n_layers=1):
    ndlrb, ncellid, nsubframe = int(ndlrb), int(ncellid), int(nsubframe)
    cfi, cell_ref_p, n_layers = int(cfi), int(cell_ref_p), int(n_layers)
    cp, scheme = cyclic_prefix.lower(), tx_scheme.lower()
    if not 6 <= ndlrb <= 110 or not 0 <= ncellid <= 503 or not 0 <= nsubframe <= 9:
        raise ValueError("ndlrb 6..110, ncellid 0..503 and nsubframe 0..9 required")
    if cp not in ("normal", "extended") or cfi not in (1, 2, 3) or cell_ref_p not in (1, 2, 4):
        raise ValueError("invalid cyclic prefix, CFI or cell_ref_p")
    if scheme not in _SCHEMES or not 1 <= n_layers <= 8:
        raise ValueError("only Release 8/9 CRS-based schemes and 1..8 layers are supported")
    prbs = slot_prbs(prb_set, ndlrb)
    symbols_per_slot = 7 if cp == "normal" else 6
    control_symbols = cfi + (1 if ndlrb <= 10 else 0)
    reserved = set()
    for data in cell_rs(ndlrb, ncellid, nsubframe, cyclic_prefix, range(cell_ref_p)).values():
        reserved.update((int(row[0]), int(row[1])) for row in data["indices"])
    if nsubframe in (0, 5):
        sync_start = 6*ndlrb-31
        sync_carriers = range(sync_start, sync_start+62)
        reserved.update((carrier, symbols_per_slot-2) for carrier in sync_carriers)
        reserved.update((carrier, symbols_per_slot-1) for carrier in sync_carriers)
    if nsubframe == 0:
        pbch_start = 6*ndlrb-36
        for symbol in range(symbols_per_slot, symbols_per_slot+4):
            reserved.update((carrier, symbol) for carrier in range(pbch_start, pbch_start+72))
    common = []
    slot_counts = []
    for slot_index, allocation in enumerate(prbs):
        carriers = np.concatenate([np.arange(12*prb, 12*prb+12) for prb in allocation])
        before = len(common)
        for local_symbol in range(symbols_per_slot):
            symbol = slot_index*symbols_per_slot+local_symbol
            if symbol < control_symbols:
                continue
            common.extend((int(carrier), symbol) for carrier in carriers if (int(carrier), symbol) not in reserved)
        slot_counts.append(len(common)-before)
    indices = np.asarray([[carrier, symbol, 0] for carrier, symbol in common], dtype=int)
    gd = len(indices)
    info = {"G": _coded_bits(gd, modulation, n_layers), "Gd": gd, "slot_re_counts": slot_counts, "port_count": cell_ref_p, "index_base": 0}
    return indices, info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ndlrb", type=int, required=True)
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--prb_set", required=True)
    parser.add_argument("--nsubframe", type=int, default=0)
    parser.add_argument("--cfi", type=int, choices=[1, 2, 3], default=1)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--cell_ref_p", type=int, choices=[1, 2, 4], default=1)
    parser.add_argument("--tx_scheme", default="Port0")
    parser.add_argument("--modulation", default="QPSK")
    parser.add_argument("--n_layers", type=int, default=1)
    args = parser.parse_args()
    try:
        indices, info = pdsch_indices(args.ndlrb, args.ncellid, args.prb_set, args.nsubframe, args.cfi, args.cyclic_prefix, args.cell_ref_p, args.tx_scheme, args.modulation, args.n_layers)
        print(json.dumps({"indices": indices.tolist(), "info": info}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
