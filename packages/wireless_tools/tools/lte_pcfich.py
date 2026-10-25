"""LTE PCFICH first-symbol resource groups and fixed geometry."""
from __future__ import annotations

import numpy as np

from lte_modulation import modulate
from lte_prbs import lte_prbs


def pcfich_indices(nrb=6, ncellid=0, ports=1, cyclic_prefix="Normal",
                    index_base=0):
    nrb, ncellid, ports = map(int, (nrb, ncellid, ports))
    if not 6 <= nrb <= 110 or not 0 <= ncellid <= 503 or ports not in (1, 2, 4):
        raise ValueError("invalid LTE PCFICH bandwidth, cell identity, or ports")
    if str(cyclic_prefix).lower() not in ("normal", "extended") or index_base not in (0, 1):
        raise ValueError("invalid cyclic prefix or index base")
    shift = ncellid % 6
    excluded = {shift, (shift+3) % 6}
    base = 6*(ncellid % (2*nrb))
    carriers = []
    for reg in range(4):
        start = (base + 6*(reg*nrb//2)) % (12*nrb)
        carriers.extend((start+offset) % (12*nrb) for offset in range(6)
                        if (start+offset) % 6 not in excluded)
    if len(carriers) != 16:
        raise ValueError("PCFICH REG allocation did not contain 16 RE")
    return np.asarray([[k+index_base, index_base, port+index_base]
                       for port in range(ports) for k in carriers], dtype=int)


def pcfich_info():
    return {"NREG": 4, "NRE": 16}


def _scramble_bits(ncellid, nsubframe):
    ncellid, nsubframe = int(ncellid), int(nsubframe)
    if not 0 <= ncellid <= 503 or not 0 <= nsubframe <= 9:
        raise ValueError("invalid PCFICH cell identity or subframe")
    cinit = (nsubframe+1)*(2*ncellid+1)*512+ncellid
    return lte_prbs(cinit, 32)


def pcfich_encode(bits, ncellid=0, nsubframe=0, ports=1):
    if int(ports) != 1:
        raise ValueError("this PCFICH subset supports one transmit port")
    data = np.asarray(bits, dtype=int).reshape(-1)
    if np.any((data != 0) & (data != 1)):
        raise ValueError("PCFICH codeword must be binary")
    data = np.pad(data[:32], (0, max(0, 32-len(data))))
    return modulate(data ^ _scramble_bits(ncellid, nsubframe), "QPSK")


def pcfich_decode(symbols, ncellid=0, nsubframe=0, ports=1):
    if int(ports) != 1:
        raise ValueError("this PCFICH subset supports one transmit port")
    values = np.asarray(symbols, dtype=complex).reshape(-1)
    if len(values) != 16 or not np.all(np.isfinite(values)):
        raise ValueError("single-port PCFICH needs 16 finite QPSK symbols")
    demod = -np.column_stack((values.real, values.imag)).reshape(-1)
    return demod*(1-2*_scramble_bits(ncellid, nsubframe).astype(int))
