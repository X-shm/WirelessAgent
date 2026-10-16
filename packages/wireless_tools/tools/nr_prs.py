"""Standalone single-resource NR PRS symbols and RE indices."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from nr_prbs import prbs


_FREQUENCY_OFFSETS = {
    2: (0, 1) * 6,
    4: (0, 2, 1, 3) * 3,
    6: (0, 3, 1, 4, 2, 5) * 2,
    12: (0, 6, 3, 9, 1, 7, 4, 10, 2, 8, 5, 11),
}


def prs_resource(nrb: int, num_rb: int, rb_offset: int, symbol_start: int,
                 num_symbols: int, comb_size: int, re_offset: int, nprsid: int,
                 slot: int = 0, index_base: str = "1based") -> tuple[list[int], np.ndarray]:
    """Return single active PRS resource in carrier-grid index order."""
    if type(nrb) is not int or not 1 <= nrb <= 275:
        raise ValueError("nrb must be 1..275")
    if type(num_rb) is not int or type(rb_offset) is not int or num_rb < 1 or rb_offset < 0 or rb_offset + num_rb > nrb:
        raise ValueError("PRS RB allocation must be within carrier grid")
    if type(symbol_start) is not int or type(num_symbols) is not int or num_symbols not in (2, 4, 6, 12) or symbol_start < 0 or symbol_start + num_symbols > 14:
        raise ValueError("PRS symbol allocation must fit inside a normal-CP slot")
    if comb_size not in _FREQUENCY_OFFSETS or type(re_offset) is not int or not 0 <= re_offset < comb_size:
        raise ValueError("comb_size must be 2/4/6/12 and re_offset within the comb")
    if type(nprsid) is not int or not 0 <= nprsid <= 4095 or type(slot) is not int or slot < 0:
        raise ValueError("nprsid must be 0..4095 and slot nonnegative")
    if index_base not in ("0based", "1based"):
        raise ValueError("index_base must be 0based or 1based")
    nsc = 12 * nrb
    per_rb = 12 // comb_size
    first_prbs_symbol = rb_offset * per_rb
    indices: list[int] = []
    blocks: list[np.ndarray] = []
    for relative_symbol in range(num_symbols):
        symbol = symbol_start + relative_symbol
        offset = (re_offset + _FREQUENCY_OFFSETS[comb_size][relative_symbol]) % comb_size
        for rb in range(rb_offset, rb_offset + num_rb):
            indices.extend(symbol * nsc + rb * 12 + offset + comb_size * k +
                           int(index_base == "1based") for k in range(per_rb))
        cinit = (2**10 * (14 * slot + symbol + 1) * (2 * nprsid + 1) +
                 nprsid) % (2**31)
        bits = prbs(cinit, 2 * (first_prbs_symbol + num_rb * per_rb)).reshape(-1, 2)
        bits = bits[first_prbs_symbol:first_prbs_symbol + num_rb * per_rb].astype(float)
        blocks.append(((1 - 2 * bits[:, 0]) + 1j * (1 - 2 * bits[:, 1])) / np.sqrt(2))
    return indices, np.concatenate(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent single-resource NR PRS")
    parser.add_argument("--operation", choices=("indices", "symbols", "both"), default="both")
    parser.add_argument("--nrb", type=int, required=True, help="Carrier RB count")
    parser.add_argument("--num_rb", type=int, required=True, help="PRS RB count")
    parser.add_argument("--rb_offset", type=int, default=0, help="PRS RB offset in carrier grid")
    parser.add_argument("--symbol_start", type=int, default=0)
    parser.add_argument("--num_symbols", type=int, choices=(2, 4, 6, 12), default=12)
    parser.add_argument("--comb_size", type=int, choices=(2, 4, 6, 12), default=2)
    parser.add_argument("--re_offset", type=int, default=0)
    parser.add_argument("--nprsid", type=int, default=0)
    parser.add_argument("--slot", type=int, default=0)
    parser.add_argument("--index_base", choices=("0based", "1based"), default="1based")
    args = parser.parse_args()
    try:
        indices, symbols = prs_resource(args.nrb, args.num_rb, args.rb_offset,
                                         args.symbol_start, args.num_symbols,
                                         args.comb_size, args.re_offset,
                                         args.nprsid, args.slot, args.index_base)
        payload: dict = {"n_re": len(indices)}
        if args.operation in ("indices", "both"):
            payload["indices"] = indices
        if args.operation in ("symbols", "both"):
            payload["symbols_real"] = symbols.real.tolist()
            payload["symbols_imag"] = symbols.imag.tolist()
        print(json.dumps(payload))
    except (ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
