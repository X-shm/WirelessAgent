"""PUCCH format 1/2/3 DRS for verified FDD single-antenna cells."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_pucch_drs.json").read_text(encoding="utf-8"))


def pucch_drs(entry: str, *, nrb=6, ncellid=0, nsubframe=0,
              cyclic_prefix="Normal", resource_idx=0, ack=None,
              n_tx_ants=1, duplex_mode="FDD"):
    if entry not in ("ltePUCCH1DRS", "ltePUCCH2DRS", "ltePUCCH3DRS"):
        raise ValueError("unknown PUCCH DRS entry")
    if int(n_tx_ants) != 1 or str(duplex_mode).upper() != "FDD":
        raise ValueError("PUCCH DRS subset supports one transmit antenna and FDD")
    cp = str(cyclic_prefix).lower()
    if cp not in ("normal", "extended"):
        raise ValueError("cyclic_prefix must be Normal or Extended")
    cp = "Normal" if cp == "normal" else "Extended"
    bits = np.asarray([] if ack is None else ack, dtype=int).reshape(-1)
    if (len(bits) > 2 or np.any((bits != 0) & (bits != 1)) or
            (entry != "ltePUCCH2DRS" and len(bits))):
        raise ValueError("only PUCCH2DRS accepts a binary ACK vector of length 0..2")
    key = ",".join(map(str, (entry, int(nrb), int(ncellid), int(nsubframe),
                             cp, int(resource_idx), "".join(map(str, bits)))))
    if key not in _TABLE:
        raise ValueError("PUCCH DRS configuration is outside the verified parameter grid")
    row = _TABLE[key]
    return np.asarray(row["real"]) + 1j*np.asarray(row["imag"]), row["info"]
