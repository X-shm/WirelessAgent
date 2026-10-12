"""Single-antenna LTE uplink SRS sequence and RE indices for explicit bandwidth allocation."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from lte_pusch_dmrs import _base_sequence


def srs(nulrb, prb_set, nsubframe=0, cyclic_prefix="Normal", tx_comb=0, cyclic_shift=0, seq_group=0, sequence_index=0):
    nulrb, nsubframe = int(nulrb), int(nsubframe)
    cp = cyclic_prefix.lower()
    value = json.loads(prb_set) if isinstance(prb_set, str) else prb_set
    prbs = [int(prb) for prb in value] if isinstance(value, list) else []
    if not 6 <= nulrb <= 110 or not 0 <= nsubframe <= 9:
        raise ValueError("nulrb 6..110 and nsubframe 0..9 required")
    if cp not in ("normal", "extended") or tx_comb not in (0, 1) or not 0 <= cyclic_shift <= 7:
        raise ValueError("invalid cyclic prefix, transmission comb or cyclic shift")
    if not 0 <= seq_group <= 29 or sequence_index not in (0, 1):
        raise ValueError("seq_group must be 0..29 and sequence_index 0 or 1")
    if len(prbs) < 6 or len(set(prbs)) != len(prbs) or prbs != list(range(min(prbs), max(prbs)+1)) or any(prb < 0 or prb >= nulrb for prb in prbs):
        raise ValueError("independent SRS coverage requires at least 6 contiguous valid PRBs")
    carriers = np.arange(12*prbs[0]+tx_comb, 12*(prbs[-1]+1), 2, dtype=int)
    base, nzc, root = _base_sequence(len(carriers), seq_group, sequence_index)
    alpha = 2*math.pi*cyclic_shift/8.0
    sequence = base*np.exp(1j*alpha*np.arange(len(base)))
    symbol = 13 if cp == "normal" else 11
    indices = np.column_stack((carriers, np.full(len(carriers), symbol), np.zeros(len(carriers), int)))
    info = {"Alpha": alpha, "SeqGroup": seq_group, "SeqIdx": sequence_index, "RootSeq": root, "NZC": nzc, "PRBSet": prbs, "FreqStart": int(carriers[0]), "KTxComb": tx_comb, "Port": 0}
    return sequence, indices, info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nulrb", type=int, required=True)
    parser.add_argument("--prb_set", required=True)
    parser.add_argument("--nsubframe", type=int, default=0)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--tx_comb", type=int, choices=[0, 1], default=0)
    parser.add_argument("--cyclic_shift", type=int, default=0)
    parser.add_argument("--seq_group", type=int, default=0)
    parser.add_argument("--sequence_index", type=int, choices=[0, 1], default=0)
    args = parser.parse_args()
    try:
        sequence, indices, info = srs(args.nulrb, args.prb_set, args.nsubframe, args.cyclic_prefix, args.tx_comb, args.cyclic_shift, args.seq_group, args.sequence_index)
        print(json.dumps({"symbols_real": sequence.real.tolist(), "symbols_imag": sequence.imag.tolist(), "indices": indices.tolist(), "info": info, "index_base": 0}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
