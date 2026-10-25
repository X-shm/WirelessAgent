"""NB-IoT NPDSCH/NPDCCH resource locations for one downlink subframe."""
from __future__ import annotations

import numpy as np

from lte_cell_rs import cell_rs
from lte_nrs import nrs


def npdsch_indices(nncellid=0, nb_ref_ports=1, operation_mode="Standalone",
                   cell_ref_ports=None, control_region_size=3,
                   data_type="NotBCCH", nsf=1, modulation="QPSK", index_base=0):
    nncellid, nb_ref_ports = int(nncellid), int(nb_ref_ports)
    if not 0 <= nncellid <= 503 or nb_ref_ports not in (1, 2):
        raise ValueError("invalid NB cell or reference-port count")
    mode = str(operation_mode)
    if mode not in ("Standalone", "Guardband", "Inband-SamePCI", "Inband-DifferentPCI"):
        raise ValueError("invalid NB-IoT operation mode")
    if data_type not in ("NotBCCH", "SIB1NB", "BCCHNotSIB1NB"):
        raise ValueError("invalid NPDSCH data type")
    if modulation not in ("QPSK", "16QAM") or index_base not in (0, 1):
        raise ValueError("invalid modulation or index base")
    if mode.startswith("Inband-"):
        first_symbol = 3 if data_type == "SIB1NB" else int(control_region_size)
        cell_ports = nb_ref_ports if mode == "Inband-SamePCI" or cell_ref_ports is None else int(cell_ref_ports)
        if cell_ports not in (nb_ref_ports, 4):
            raise ValueError("cell_ref_ports must match NBRefP or equal 4")
    else:
        first_symbol = 0
        cell_ports = 0
    if not 0 <= first_symbol <= 13:
        raise ValueError("control_region_size must be 0..13")
    excluded = set()
    _, positions = nrs(nncellid=nncellid, nb_ref_ports=nb_ref_ports, index_base=0)
    excluded.update((int(k), int(l)) for k, l, _ in positions)
    if cell_ports:
        for record in cell_rs(6, nncellid, 0, ports=tuple(range(cell_ports))).values():
            excluded.update((int(k), int(l)) for k, l, _ in record["indices"] if k < 12)
    per_port = [(k, symbol) for symbol in range(first_symbol, 14)
                for k in range(12) if (k, symbol) not in excluded]
    indices = np.asarray([[k+index_base, symbol+index_base, port+index_base]
                          for port in range(nb_ref_ports) for k, symbol in per_port], dtype=int)
    nsf = 8 if data_type == "SIB1NB" else int(nsf)
    if nsf < 1:
        raise ValueError("nsf must be positive")
    gd = len(per_port)*nsf
    return indices, {"G": (2 if modulation == "QPSK" else 4)*gd, "Gd": gd}


def npdcch_indices(nncellid=0, nb_ref_ports=1, operation_mode="Standalone",
                   cell_ref_ports=None, control_region_size=3, ncce=(0, 1),
                   index_base=0):
    selected = tuple(int(x) for x in np.atleast_1d(ncce))
    if not selected or any(x not in (0, 1) for x in selected):
        raise ValueError("ncce must contain 0 or 1")
    indices, _ = npdsch_indices(nncellid, nb_ref_ports, operation_mode,
                                cell_ref_ports, control_region_size,
                                "NotBCCH", 1, "QPSK", index_base)
    selected_set = set(selected)
    indices = np.asarray([row for row in indices
                          if ((int(row[0])-index_base)//6) in selected_set], dtype=int)
    gd = len(indices)//int(nb_ref_ports)
    return indices, {"G": 2*gd, "Gd": gd}
