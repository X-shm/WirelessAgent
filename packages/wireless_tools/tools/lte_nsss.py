"""LTE NB-IoT NSSS and resource positions from the public R2026a M-file."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lte_cell_rs import cell_rs

_MASKS = np.asarray(json.loads(Path(__file__).with_name("_lte_nsss_binary.json").read_text(encoding="utf-8")),
                    dtype=np.int8)


def nsss(nncellid=1, nsubframe=9, nframe=0, operation_mode="Standalone",
         ncellid=None, cell_ref_ports=None, port=0, index_base=0):
    nncellid, nsubframe, nframe, port = map(int, (nncellid, nsubframe, nframe, port))
    if not 0 <= nncellid <= 503 or not 0 <= nsubframe <= 9 or nframe < 0 or port < 0:
        raise ValueError("invalid NB cell, subframe, frame, or antenna port")
    if operation_mode not in ("Standalone", "Guardband", "Inband-SamePCI", "Inband-DifferentPCI"):
        raise ValueError("unsupported NB-IoT operation mode")
    if index_base not in (0, 1):
        raise ValueError("index_base must be 0 or 1")
    if (nframe*10+nsubframe) % 20 != 9:
        return np.empty(0, dtype=complex), np.empty((0, 3), dtype=int)

    u = nncellid % 126 + 3
    q = nncellid // 126
    theta = (33/132) * ((nframe/2) % 4)
    n = np.arange(132, dtype=float)
    nd = np.concatenate((np.arange(131, dtype=float), [0.]))
    masks = np.concatenate((_MASKS[q], _MASKS[q, :4]))
    sequence = masks * np.exp(-1j*np.pi*(2*theta*n + u*nd*(nd+1)/131))

    excluded = set()
    if operation_mode.startswith("Inband-") and ncellid is not None and cell_ref_ports is not None:
        count = int(cell_ref_ports)
        if count not in (1, 2, 4):
            raise ValueError("cell_ref_ports must be 1, 2, or 4")
        if not 0 <= int(ncellid) <= 503:
            raise ValueError("ncellid must be 0..503")
        for record in cell_rs(6, int(ncellid), nsubframe, ports=tuple(range(count))).values():
            excluded.update((int(k), int(l)) for k, l, _ in record["indices"] if k < 12)

    positions = [(k, symbol) for symbol in range(3, 14) for k in range(12)
                 if (k, symbol) not in excluded]
    values = np.asarray([sequence[(symbol-3)*12+k] for k, symbol in positions])
    indices = np.asarray([[k+index_base, symbol+index_base, port+index_base]
                          for k, symbol in positions], dtype=int)
    return values, indices


def npss(nsubframe=5, operation_mode="Standalone", ncellid=None,
         cell_ref_ports=None, port=0, index_base=0):
    nsubframe, port = int(nsubframe), int(port)
    if not 0 <= nsubframe <= 9 or port < 0 or index_base not in (0, 1):
        raise ValueError("invalid NPSS subframe, port, or index base")
    if operation_mode not in ("Standalone", "Guardband", "Inband-SamePCI", "Inband-DifferentPCI"):
        raise ValueError("unsupported NB-IoT operation mode")
    if nsubframe != 5:
        return np.empty(0, dtype=complex), np.empty((0, 3), dtype=int)
    excluded = set()
    if operation_mode.startswith("Inband-") and ncellid is not None and cell_ref_ports is not None:
        count = int(cell_ref_ports)
        if count not in (1, 2, 4) or not 0 <= int(ncellid) <= 503:
            raise ValueError("invalid inband CRS settings")
        for record in cell_rs(6, int(ncellid), nsubframe, ports=tuple(range(count))).values():
            excluded.update((int(k), int(l)) for k, l, _ in record["indices"] if k < 12)
    m = np.arange(11)
    sequence = np.exp(-1j*np.pi*5*m*(m+1)/11)
    signs = [0, 0, 0, 1, 1, 1, 1, -1, -1, 1, 1, 1, -1, 1]
    positions = [(k, symbol) for symbol in range(3, 14) for k in range(11)
                 if (k, symbol) not in excluded]
    values = np.asarray([sequence[k]*signs[symbol] for k, symbol in positions])
    indices = np.asarray([[k+index_base, symbol+index_base, port+index_base]
                          for k, symbol in positions], dtype=int)
    return values, indices
