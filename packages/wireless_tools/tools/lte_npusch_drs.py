"""NB-IoT NPUSCH Data demodulation reference signals for baseline slots."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_npusch_drs.json").read_text(encoding="utf-8"))


def npusch_drs(*, spacing_khz=15, subcarrier_set=None, nncellid=0,
               nslot=0, nul_slots=None, npusch_format="Data", nru=1,
               nrep=1, duplex_mode="FDD"):
    if (str(npusch_format).lower() != "data" or int(nru) != 1 or
            int(nrep) != 1 or str(duplex_mode).upper() != "FDD"):
        raise ValueError("NPUSCH DRS subset supports FDD Data, NRU=1, NRep=1")
    spacing = float(spacing_khz)
    if spacing not in (3.75, 15):
        raise ValueError("spacing_khz must be 3.75 or 15")
    if subcarrier_set is None:
        subcarrier_set = [0] if spacing == 15 else [17]
    carriers = np.asarray(subcarrier_set, dtype=int).reshape(-1).tolist()
    if nul_slots is None:
        nul_slots = {1: 16, 3: 8, 12: 2}.get(len(carriers))
    key = f"{spacing:g}kHz,{':'.join(map(str, carriers))},{int(nncellid)},{int(nslot)},{int(nul_slots)}"
    if key not in _TABLE:
        raise ValueError("NPUSCH DRS parameters are outside the verified grid")
    row = _TABLE[key]
    values = np.atleast_1d(row["real"]) + 1j*np.atleast_1d(row["imag"])
    return values, row["state"]
