"""LTE sidelink SCI payload size, TS 36.212 format 0/1."""
from __future__ import annotations


def sci_info(nrb=6):
    nrb = int(nrb)
    if not 6 <= nrb <= 110:
        raise ValueError("nrb must be 6..110")
    riv_count = nrb*(nrb+1)//2
    riv_bits = (riv_count-1).bit_length()
    return {"Format0": 32+riv_bits, "Format1": 32}
