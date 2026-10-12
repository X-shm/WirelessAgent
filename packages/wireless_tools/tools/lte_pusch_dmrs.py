"""Single-layer LTE PUSCH DM-RS and RE indices for explicit PRB allocation."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np


def _largest_prime_below(value: int) -> int:
    for candidate in range(value - 1, 1, -1):
        if all(candidate % divisor for divisor in range(2, int(math.sqrt(candidate)) + 1)):
            return candidate
    raise ValueError("no prime available")


def _slot_prbs(prb_set):
    value = json.loads(prb_set) if isinstance(prb_set, str) else prb_set
    if not isinstance(value, list) or not value:
        raise ValueError("prb_set must be a nonempty JSON array")
    if isinstance(value[0], list):
        if len(value) != 2:
            raise ValueError("two-slot prb_set must be [slot0_prbs,slot1_prbs]")
        slots = value
    else:
        slots = [value, value]
    return [[int(prb) for prb in slot] for slot in slots]


def _base_sequence(length: int, group: int, sequence_index: int):
    if length < 36:
        raise ValueError("independent PUSCH DM-RS coverage requires at least 3 PRBs")
    nzc = _largest_prime_below(length)
    qbar = nzc * (group + 1) / 31.0
    q = int(math.floor(qbar + 0.5)) + int(sequence_index) * ((-1) ** int(math.floor(2*qbar)))
    n = np.arange(length)
    return np.exp(-1j * math.pi * q * (n % nzc) * ((n % nzc) + 1) / nzc), nzc, q


def pusch_dmrs(nulrb: int, ncellid: int, prb_set, nsubframe: int = 0, cyclic_prefix: str = "Normal", seq_group: int = 0, sequence_index: int = 0, cyclic_shift: int = 0):
    nulrb, ncellid, nsubframe = int(nulrb), int(ncellid), int(nsubframe)
    cp = cyclic_prefix.lower()
    slots = _slot_prbs(prb_set)
    if not 1 <= nulrb <= 110 or not 0 <= ncellid <= 503 or not 0 <= nsubframe <= 9:
        raise ValueError("nulrb 1..110, ncellid 0..503 and nsubframe 0..9 required")
    if cp not in ("normal", "extended") or not 0 <= seq_group <= 29 or sequence_index not in (0, 1) or not 0 <= cyclic_shift <= 11:
        raise ValueError("invalid CP, sequence group/index or cyclic shift")
    if any(len(slot) < 3 or any(prb < 0 or prb >= nulrb for prb in slot) for slot in slots):
        raise ValueError("each slot needs at least 3 valid PRBs")
    symbols_per_slot = 7 if cp == "normal" else 6
    dmrs_symbol = 3 if cp == "normal" else 2
    group = (ncellid + seq_group) % 30
    output = []
    for slot_index, prbs in enumerate(slots):
        carriers = np.concatenate([np.arange(12*prb, 12*prb+12) for prb in prbs])
        base, nzc, root = _base_sequence(len(carriers), group, sequence_index if len(prbs) >= 6 else 0)
        alpha = 2*math.pi*cyclic_shift/12.0
        sequence = base * np.exp(1j*alpha*np.arange(len(base)))
        symbol = slot_index*symbols_per_slot + dmrs_symbol
        indices = np.column_stack([carriers, np.full(len(carriers), symbol), np.zeros(len(carriers), int)])
        output.append({"slot": slot_index, "indices": indices, "symbols": sequence, "root_sequence": root, "nzc": nzc, "sequence_group": group})
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nulrb", type=int, required=True)
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--prb_set", required=True)
    parser.add_argument("--nsubframe", type=int, default=0)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--seq_group", type=int, default=0)
    parser.add_argument("--sequence_index", type=int, default=0)
    parser.add_argument("--cyclic_shift", type=int, default=0)
    args = parser.parse_args()
    try:
        slots = []
        for item in pusch_dmrs(args.nulrb, args.ncellid, args.prb_set, args.nsubframe, args.cyclic_prefix, args.seq_group, args.sequence_index, args.cyclic_shift):
            slots.append({"slot": item["slot"], "indices": item["indices"].tolist(), "symbols_real": item["symbols"].real.tolist(), "symbols_imag": item["symbols"].imag.tolist(), "root_sequence": item["root_sequence"], "nzc": item["nzc"], "sequence_group": item["sequence_group"]})
        print(json.dumps({"slots": slots, "index_base": 0}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
