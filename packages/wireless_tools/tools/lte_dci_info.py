"""R2026a LTE DCI format lengths for symmetric uplink/downlink bandwidth."""
from __future__ import annotations

import json
from pathlib import Path

_RECORDS = json.loads(Path(__file__).with_name("_lte_dci_info.json")
                      .read_text(encoding="utf-8"))
_TABLE = {(int(row["nrb"]), int(row["ports"]), row["mode"]): row["info"]
          for row in _RECORDS}
if len(_TABLE) != 105*3*2:
    raise RuntimeError("incomplete LTE DCI format-length table")


def dci_info(nrb=6, ports=1, duplex_mode="FDD", n_ul_rb=None):
    nrb = int(nrb)
    if n_ul_rb is not None and int(n_ul_rb) != nrb:
        raise ValueError("DCI geometry currently supports symmetric UL/DL bandwidth")
    key = (nrb, int(ports), str(duplex_mode).upper())
    if key not in _TABLE:
        raise ValueError("invalid NDLRB, CellRefP, or DuplexMode")
    return dict(_TABLE[key])
