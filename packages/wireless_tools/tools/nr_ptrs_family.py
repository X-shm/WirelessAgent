"""Single-port, non-transform-precoded NR PT-RS positions and symbols."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import run_cli
from nr_dmrs import dmrs_sequence


def _indices(nrb: int, rb_set, symbol_start: int, num_symbols: int,
             dmrs_symbols, frequency_density: int, time_density: int,
             re_offset: int, index_base: int):
    rbs = sorted(set(int(rb) for rb in rb_set))
    if not rbs or min(rbs) < 0 or max(rbs) >= nrb or not 1 <= nrb <= 275:
        raise ValueError("rb_set must be nonempty and within nrb")
    if frequency_density not in (2, 4) or time_density not in (1, 2, 4):
        raise ValueError("frequency_density must be 2/4; time_density 1/2/4")
    if not 0 <= re_offset < 12 or not 0 <= symbol_start < 14 or num_symbols < 1 or symbol_start + num_symbols > 14:
        raise ValueError("invalid RE offset or symbol allocation")
    if index_base not in (0, 1):
        raise ValueError("index_base must be 0/1")
    dmrs = set(int(x) for x in dmrs_symbols)
    data_symbols = [l for l in range(symbol_start, symbol_start + num_symbols) if l not in dmrs]
    selected = data_symbols[::time_density]
    rbs = rbs[::frequency_density]
    coordinates = [(rb * 12 + re_offset, l) for l in selected for rb in rbs]
    return {"indices": [index_base + l * nrb * 12 + sc for sc, l in coordinates],
            "subscripts": coordinates, "n_re": len(coordinates)}


def pdsch_ptrs_indices(nrb: int, rb_set, symbol_start: int = 0, num_symbols: int = 14,
                       dmrs_symbols=(2,), frequency_density: int = 2,
                       time_density: int = 1, re_offset: int = 0, index_base: int = 1):
    return _indices(nrb, rb_set, symbol_start, num_symbols, dmrs_symbols,
                    frequency_density, time_density, re_offset, index_base)


def pusch_ptrs_indices(nrb: int, rb_set, symbol_start: int = 0, num_symbols: int = 14,
                       dmrs_symbols=(2,), frequency_density: int = 2,
                       time_density: int = 1, re_offset: int = 0, index_base: int = 1):
    return _indices(nrb, rb_set, symbol_start, num_symbols, dmrs_symbols,
                    frequency_density, time_density, re_offset, index_base)


def _symbols(nrb: int, rb_set, nid: int, slot: int, symbol_start: int,
             num_symbols: int, dmrs_symbols, frequency_density: int,
             time_density: int, re_offset: int):
    result = _indices(nrb, rb_set, symbol_start, num_symbols, dmrs_symbols,
                      frequency_density, time_density, re_offset, 1)
    if not 0 <= nid <= 65535 or slot < 0:
        raise ValueError("nid must be 0..65535 and slot nonnegative")
    symbols = []
    for sc, l in result["subscripts"]:
        sequence = dmrs_sequence(nid, 0, slot, l, nrb)
        symbols.append(sequence[6 * (sc // 12)])
    return {"symbols": np.asarray(symbols), "indices": result["indices"]}


def pdsch_ptrs(nrb: int, rb_set, nid: int, slot: int = 0, symbol_start: int = 0,
               num_symbols: int = 14, dmrs_symbols=(2,), frequency_density: int = 2,
               time_density: int = 1, re_offset: int = 0):
    return _symbols(nrb, rb_set, nid, slot, symbol_start, num_symbols,
                    dmrs_symbols, frequency_density, time_density, re_offset)


def pusch_ptrs(nrb: int, rb_set, nid: int, slot: int = 0, symbol_start: int = 0,
               num_symbols: int = 14, dmrs_symbols=(2,), frequency_density: int = 2,
               time_density: int = 1, re_offset: int = 0):
    return _symbols(nrb, rb_set, nid, slot, symbol_start, num_symbols,
                    dmrs_symbols, frequency_density, time_density, re_offset)


if __name__ == "__main__":
    run_cli("Single-port NR PT-RS resource subsets", {
        "nrPDSCHPTRS": pdsch_ptrs,
        "nrPDSCHPTRSIndices": pdsch_ptrs_indices,
        "nrPUSCHPTRS": pusch_ptrs,
        "nrPUSCHPTRSIndices": pusch_ptrs_indices,
    })
