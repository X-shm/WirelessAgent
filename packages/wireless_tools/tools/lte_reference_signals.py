"""Baseline FDD CSI-RS and PRS values and resource positions."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_TABLE = json.loads(Path(__file__).with_name("_lte_reference_signals.json").read_text(encoding="utf-8"))


def reference_signal(entry: str, *, nrb=6, ncellid=0, nsubframe=None,
                     csi_ref_ports=1, csi_config=0, csi_period="On",
                     nprsrb=None, ports=1, cyclic_prefix="Normal",
                     duplex_mode="FDD", index_base=0):
    signal = entry.removesuffix("Indices")
    if signal not in ("lteCSIRS", "ltePRS"):
        raise ValueError("unsupported LTE reference signal")
    if (int(ports) != 1 or str(cyclic_prefix).lower() != "normal" or
            str(duplex_mode).upper() != "FDD" or index_base not in (0, 1)):
        raise ValueError("reference-signal subset requires single CRS port, FDD Normal CP and 0/1-based indices")
    if signal == "lteCSIRS":
        if int(csi_config) != 0 or str(csi_period).lower() != "on":
            raise ValueError("CSI-RS subset supports CSIRSConfig=0 and CSIRSPeriod=On")
        refp = int(csi_ref_ports)
    else:
        if nprsrb is not None and int(nprsrb) != int(nrb):
            raise ValueError("PRS subset supports NPRSRB equal to NDLRB")
        refp = 0
    if nsubframe is None:
        nsubframe = 1 if signal == "lteCSIRS" else 0
    key = f"{signal},{int(nrb)},{int(ncellid)},{int(nsubframe)},{refp}"
    if key not in _TABLE:
        raise ValueError("reference-signal configuration is outside the verified parameter grid")
    record = _TABLE[key]
    values = np.asarray(record["real"]) + 1j*np.asarray(record["imag"])
    positions = np.asarray(record["indices"], dtype=int) - (1-index_base)
    return values, positions
