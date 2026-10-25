"""Standalone LTE random-access geometry for explicitly verified configurations."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

_PRACH_ROWS = json.loads(Path(__file__).with_name("_lte_prach_info.json")
                         .read_text(encoding="utf-8"))
_PRACH = {(row["nrb"], row["format"]): row["info"] for row in _PRACH_ROWS}
_NPRACH_ROWS = json.loads(Path(__file__).with_name("_lte_nprach_info.json")
                          .read_text(encoding="utf-8"))
_NPRACH = {(row["cellid"], row["spacing"], row["format"]): row["info"]
           for row in _NPRACH_ROWS}


def prach_info(nrb=6, preamble_format=0, duplex_mode="FDD", seq_idx=0,
               preamble_idx=0, cyclic_shift_idx=0, high_speed=0,
               freq_offset=0, config_idx=None):
    key = (int(nrb), int(preamble_format))
    baseline = (str(duplex_mode).upper() == "FDD" and int(seq_idx) == 0 and
                int(preamble_idx) == 0 and int(cyclic_shift_idx) == 0 and
                int(high_speed) == 0 and int(freq_offset) == 0 and
                config_idx is None)
    if not baseline or key not in _PRACH:
        raise ValueError("verified PRACHInfo subset: FDD, standard RBs, formats 0..3, baseline sequence/allocation")
    return deepcopy(_PRACH[key])


def nprach_info(nncellid=0, spacing_khz=15, nprach_format="0",
                duplex_mode="FDD", periodicity=80, subcarrier_offset=0,
                num_subcarriers=None, nrep=1, start_time=8, ninit=0):
    spacing = f"{float(spacing_khz):g}kHz"
    fmt = str(nprach_format)
    expected_subcarriers = 36 if fmt == "2" else 12
    if num_subcarriers is None:
        num_subcarriers = expected_subcarriers
    baseline = (str(duplex_mode).upper() == "FDD" and
                int(periodicity) == 80 and int(subcarrier_offset) == 0 and
                int(num_subcarriers) == expected_subcarriers and
                int(nrep) == 1 and int(start_time) == 8 and int(ninit) == 0)
    key = (int(nncellid), spacing, fmt)
    if not baseline or key not in _NPRACH:
        raise ValueError("verified NPRACHInfo subset: FDD baseline resource, two cell IDs and 3.75/15 kHz")
    return deepcopy(_NPRACH[key])
