"""NB-IoT NPBCH resource positions for one scheduled subframe."""
from __future__ import annotations

import numpy as np

from lte_cell_rs import cell_rs
from lte_nrs import nrs


def npbch_indices(nncellid=1, nb_ref_ports=1, nsubframe=0, nframe=0,
                  index_base=0):
    nncellid, nb_ref_ports, nsubframe, nframe = map(int, (nncellid, nb_ref_ports,
                                                         nsubframe, nframe))
    if not 0 <= nncellid <= 503 or nb_ref_ports not in (1, 2):
        raise ValueError("nncellid must be 0..503 and nb_ref_ports 1 or 2")
    if nsubframe < 0 or nframe < 0 or index_base not in (0, 1):
        raise ValueError("invalid subframe, frame, or index base")
    if nsubframe % 10:
        return np.empty((0, 3), dtype=int), {"G": 0, "Gd": 0}

    excluded = set()
    for record in cell_rs(6, nncellid, 0, ports=(0, 1, 2, 3)).values():
        excluded.update((int(k), int(l)) for k, l, _ in record["indices"] if k < 12)
    _, reference_positions = nrs(nncellid, 0, nb_ref_ports=2, index_base=0)
    excluded.update((int(k), int(l)) for k, l, _ in reference_positions)
    per_port = [(carrier, symbol) for symbol in range(3, 14)
                for carrier in range(12) if (carrier, symbol) not in excluded]
    positions = np.asarray([[carrier+index_base, symbol+index_base, port+index_base]
                            for port in range(nb_ref_ports)
                            for carrier, symbol in per_port], dtype=int)
    return positions, {"G": 16*len(per_port), "Gd": 8*len(per_port)}
