"""NB-IoT NPUSCH FDD slot data positions and codeword geometry."""
from __future__ import annotations

import numpy as np

from lte_npusch_drs_indices import npusch_drs_indices


def npusch_indices(spacing_khz=15, npusch_format="Data", subcarrier_set=None,
                   duplex_mode="FDD", index_base=0, nru=1, nul_slots=None,
                   modulation="BPSK"):
    drs = npusch_drs_indices(spacing_khz, npusch_format, subcarrier_set,
                             duplex_mode, index_base=0)
    carriers = ([0] if subcarrier_set is None else
                sorted(np.asarray(subcarrier_set, dtype=int).reshape(-1).tolist()))
    reserved = {(int(k), int(l)) for k, l, _ in drs}
    positions = np.asarray([[k+index_base, l+index_base, index_base]
                            for l in range(7) for k in carriers
                            if (k, l) not in reserved], dtype=int)
    count = len(carriers)
    expected_slots = (4 if str(npusch_format).lower() == "control" else
                      {1: 16, 3: 8, 6: 4, 12: 2}[count])
    slots = expected_slots if nul_slots is None else int(nul_slots)
    nru = int(nru)
    modulation = str(modulation).upper()
    if slots != expected_slots or nru not in (1, 2, 3, 4, 5, 6, 8, 10):
        raise ValueError("invalid NPUSCH resource-unit and slot combination")
    if str(npusch_format).lower() == "control" and (nru != 1 or modulation != "BPSK"):
        raise ValueError("NPUSCH Control requires one resource unit and BPSK")
    if modulation not in ("BPSK", "QPSK", "16QAM"):
        raise ValueError("unsupported NPUSCH modulation")
    bits_per_symbol = {"BPSK": 1, "QPSK": 2, "16QAM": 4}[modulation]
    gd = nru*slots*len(positions)
    return positions, {"G": bits_per_symbol*gd, "Gd": gd}
