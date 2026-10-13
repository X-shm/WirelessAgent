"""Single-layer PUSCH DM-RS uplink channel estimation."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex
from lte_pusch_dmrs import pusch_dmrs


def ul_channel_estimate(received_grid, nulrb, ncellid, prb_set, nsubframe=0, cyclic_prefix="Normal", seq_group=0, sequence_index=0, cyclic_shift=0, smoothing=1):
    received = np.asarray(received_grid, dtype=complex)
    if received.ndim == 2:
        received = received[:, :, None]
    nsym = 14 if cyclic_prefix.lower() == "normal" else 12
    if received.ndim != 3 or received.shape[:2] != (12*int(nulrb), nsym) or smoothing < 1:
        raise ValueError("received_grid must be 12*nulrb by 14/12 symbols by receive antennas")
    references = pusch_dmrs(nulrb, ncellid, prb_set, nsubframe, cyclic_prefix, seq_group, sequence_index, cyclic_shift)
    estimate = np.zeros(received.shape, complex)
    residual = []
    symbols_per_slot = nsym//2
    for slot in references:
        indices, symbols = slot["indices"][:, :2], slot["symbols"]
        carriers = indices[:, 0]
        for rx in range(received.shape[2]):
            ls = received[carriers, indices[:, 1], rx] / symbols
            if smoothing > 1:
                kernel = np.ones(smoothing)/smoothing
                ls = np.convolve(ls.real, kernel, mode="same") + 1j*np.convolve(ls.imag, kernel, mode="same")
            first, last = slot["slot"]*symbols_per_slot, (slot["slot"]+1)*symbols_per_slot
            estimate[carriers, first:last, rx] = ls[:, None]
            predicted = symbols*ls
            residual.extend(np.abs(received[carriers, indices[:, 1], rx]-predicted)**2)
    return estimate, float(np.mean(residual)) if residual else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--received_grid", required=True)
    parser.add_argument("--nulrb", type=int, required=True)
    parser.add_argument("--ncellid", type=int, required=True)
    parser.add_argument("--prb_set", required=True)
    parser.add_argument("--nsubframe", type=int, default=0)
    parser.add_argument("--cyclic_prefix", choices=["Normal", "Extended"], default="Normal")
    parser.add_argument("--seq_group", type=int, default=0)
    parser.add_argument("--sequence_index", type=int, default=0)
    parser.add_argument("--cyclic_shift", type=int, default=0)
    parser.add_argument("--smoothing", type=int, default=1)
    args = parser.parse_args()
    try:
        estimate, noise = ul_channel_estimate(parse_complex(args.received_grid), args.nulrb, args.ncellid, args.prb_set, args.nsubframe, args.cyclic_prefix, args.seq_group, args.sequence_index, args.cyclic_shift, args.smoothing)
        print(json.dumps({"channel_estimate": complex_json(estimate), "noise_variance": noise}))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
