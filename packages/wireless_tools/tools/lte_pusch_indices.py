"""LTE PUSCH data RE indices for explicit slot-wise PRB allocation."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _lte_resource_helpers import modulation_order, slot_prbs


def pusch_indices(nulrb, prb_set, cyclic_prefix="Normal", shortened=False, n_tx_ants=1, modulation="QPSK", n_layers=1):
    nulrb, n_tx_ants, n_layers = int(nulrb), int(n_tx_ants), int(n_layers)
    cp = cyclic_prefix.lower()
    if not 1 <= nulrb <= 110 or cp not in ("normal", "extended"):
        raise ValueError("nulrb must be 1..110 and cyclic_prefix Normal/Extended")
    if n_tx_ants not in (1, 2, 4) or not 1 <= n_layers <= 4:
        raise ValueError("n_tx_ants must be 1, 2 or 4 and n_layers 1..4")
    prbs = slot_prbs(prb_set, nulrb)
    symbols_per_slot = 7 if cp == "normal" else 6
    dmrs_symbol = 3 if cp == "normal" else 2
    common = []
    slot_counts = []
    for slot_index, allocation in enumerate(prbs):
        carriers = np.concatenate([np.arange(12*prb, 12*prb+12) for prb in allocation])
        before = len(common)
        for local_symbol in range(symbols_per_slot):
            global_symbol = slot_index*symbols_per_slot + local_symbol
            if local_symbol == dmrs_symbol or (bool(shortened) and global_symbol == 2*symbols_per_slot-1):
                continue
            common.extend((int(carrier), global_symbol) for carrier in carriers)
        slot_counts.append(len(common)-before)
    per_port = {}
    for port in range(n_tx_ants):
        per_port[str(port)] = np.asarray([[carrier, symbol, port] for carrier, symbol in common], dtype=int)
    gd = len(common)
    g = gd*modulation_order(modulation)*n_layers
    return per_port, {"G": [g], "Gd": gd, "slot_re_counts": slot_counts, "index_base": 0}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nulrb", type=int, required=True)
    parser.add_argument("--prb_set", required=True)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--shortened", action="store_true")
    parser.add_argument("--n_tx_ants", type=int, default=1)
    parser.add_argument("--modulation", default="QPSK")
    parser.add_argument("--n_layers", type=int, default=1)
    args = parser.parse_args()
    try:
        ports, info = pusch_indices(args.nulrb, args.prb_set, args.cyclic_prefix, args.shortened, args.n_tx_ants, args.modulation, args.n_layers)
        print(json.dumps({"ports": {port: indices.tolist() for port, indices in ports.items()}, "info": info}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
