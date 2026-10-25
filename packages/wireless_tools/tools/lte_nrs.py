"""NB-IoT NRS symbols and resource positions for normal cyclic prefix."""
from __future__ import annotations

import numpy as np

from lte_prbs import lte_prbs


def nrs(nncellid=1, nsubframe=0, nb_ref_ports=1, ports=None, index_base=0):
    """Return concatenated NRS symbols and [subcarrier, symbol, port] indices.

    ``ports`` contains NB antenna ports 0 and/or 1.  The output follows
    MATLAB's port-major symbol order, with eight values per requested port.
    """
    nncellid, nsubframe, nb_ref_ports = map(int, (nncellid, nsubframe, nb_ref_ports))
    if not 0 <= nncellid <= 503 or not 0 <= nsubframe <= 9:
        raise ValueError("nncellid must be 0..503 and nsubframe 0..9")
    if nb_ref_ports not in (1, 2) or index_base not in (0, 1):
        raise ValueError("nb_ref_ports must be 1 or 2; index_base must be 0 or 1")
    selected = tuple(range(nb_ref_ports)) if ports is None else tuple(int(p) for p in
                                                                  np.atleast_1d(ports))
    if not selected or any(p not in (0, 1) for p in selected):
        raise ValueError("ports must contain antenna port 0 or 1")

    symbols = []
    for slot in (2*nsubframe, 2*nsubframe+1):
        for symbol in (5, 6):
            cinit = 1024*(7*(slot+1)+symbol+1)*(2*nncellid+1)+2*nncellid+1
            c = lte_prbs(cinit, 222)
            for m in (109, 110):
                symbols.append(((1-2*int(c[2*m])) +
                                1j*(1-2*int(c[2*m+1])))/np.sqrt(2))

    shift = nncellid % 6
    positions = []
    values = []
    for port in selected:
        values.extend(symbols)
        for symbol in (5, 6, 12, 13):
            offset = (shift + (3 if (symbol % 7 == 6) != bool(port) else 0)) % 6
            for subcarrier in (offset, offset+6):
                positions.append((subcarrier+index_base, symbol+index_base,
                                  port+index_base))
    return np.asarray(values, dtype=complex), np.asarray(positions, dtype=int)
