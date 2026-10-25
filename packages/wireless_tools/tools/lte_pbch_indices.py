"""LTE physical broadcast channel positions in a scheduled subframe."""
from __future__ import annotations

import numpy as np

from lte_cell_rs import cell_rs


def pbch_indices(nrb=6, ncellid=0, cyclic_prefix="Normal", ports=1,
                 nsubframe=0, index_base=0):
    nrb, ncellid, ports, nsubframe = map(int, (nrb, ncellid, ports, nsubframe))
    cp = str(cyclic_prefix).lower()
    if (not 6 <= nrb <= 110 or not 0 <= ncellid <= 503 or
            ports not in (1, 2, 4) or cp not in ("normal", "extended") or
            nsubframe < 0 or index_base not in (0, 1)):
        raise ValueError("invalid PBCH carrier or indexing parameters")
    if nsubframe % 10:
        return np.empty((0, 3), dtype=int)
    slot_symbols = 7 if cp == "normal" else 6
    start = (12*nrb-72)//2
    excluded = set()
    for record in cell_rs(nrb, ncellid, 0, cyclic_prefix, ports=(0, 1, 2, 3)).values():
        excluded.update((int(k), int(l)) for k, l, _ in record["indices"])
    positions = np.asarray(
        [[carrier+index_base, symbol+index_base, port+index_base]
         for port in range(ports)
         for symbol in range(slot_symbols, slot_symbols+4)
         for carrier in range(start, start+72)
         if (carrier, symbol) not in excluded], dtype=int)
    return positions
