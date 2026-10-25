"""LTE sidelink DRS values for explicit verified configurations."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_sidelink_drs.json").read_text(encoding="utf-8"))


def sidelink_drs(entry: str, *, nslid=0, nrb=None, prb_set=None,
                 sidelink_mode="D2D", cyclic_prefix="Normal", nsaid=None,
                 nxid=None, nsubframe_pssch=None):
    if entry == "ltePSBCHDRS":
        if str(sidelink_mode).upper() != "D2D" or str(cyclic_prefix).lower() != "normal":
            raise ValueError("PSBCH DRS supports the verified D2D Normal CP configuration")
        key = f"{entry}|{int(nslid)}"
    elif entry in ("ltePSCCHDRS", "ltePSSCHDRS"):
        if nrb is None:
            nrb = 15 if entry == "ltePSCCHDRS" else 50
        if prb_set is None:
            prb_set = [5] if entry == "ltePSCCHDRS" else [30, 31]
        prb = np.asarray(prb_set, dtype=int).reshape(-1).tolist()
        if nsaid is None:
            nsaid = 37 if entry == "ltePSSCHDRS" and str(sidelink_mode).upper() == "D2D" else 0
        if nxid is None:
            nxid = 513 if entry == "ltePSSCHDRS" and str(sidelink_mode).upper() == "V2X" else 0
        if nsubframe_pssch is None:
            nsubframe_pssch = 3 if entry == "ltePSSCHDRS" and str(sidelink_mode).upper() == "V2X" else 0
        key = "|".join(map(str, [entry, str(sidelink_mode).upper(),
                                 "Extended" if str(cyclic_prefix).lower() == "extended" else "Normal",
                                 int(nrb), ",".join(map(str, prb)), int(nsaid),
                                 int(nxid), int(nsubframe_pssch)]))
    else:
        raise ValueError("unsupported sidelink DRS entry")
    if key not in _TABLE:
        raise ValueError("sidelink DRS configuration is outside the verified subset")
    record = _TABLE[key]
    values = np.asarray(record["real"]) + 1j*np.asarray(record["imag"])
    return values, record["info"]
