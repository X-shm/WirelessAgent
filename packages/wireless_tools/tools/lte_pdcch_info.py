"""LTE FDD PDCCH control-region resource geometry."""
from __future__ import annotations

from lte_phich_info import phich_info


def pdcch_info(nrb=6, cyclic_prefix="Normal", ports=1, cfi=1,
               ng="One", duplex_mode="FDD"):
    nrb, ports, cfi = int(nrb), int(ports), int(cfi)
    cp = str(cyclic_prefix).lower()
    if not 6 <= nrb <= 110 or ports not in (1, 2, 4) or cfi not in (1, 2, 3):
        raise ValueError("invalid nrb, CellRefP, or CFI")
    if cp not in ("normal", "extended"):
        raise ValueError("cyclic_prefix must be Normal or Extended")
    phich = phich_info(nrb=nrb, ng=ng, cyclic_prefix=cyclic_prefix,
                       duplex_mode=duplex_mode)
    nsym = cfi + int(nrb <= 10)
    reg_per_symbol = [2*nrb, (2 if ports == 4 else 3)*nrb, 3*nrb,
                      (2 if cp == "extended" else 3)*nrb]
    nreg = sum(reg_per_symbol[:nsym]) - 4 - phich["NREG"]
    ncce = nreg // 9
    nreg_used = ncce*9
    return {"NREG": nreg, "NRE": nreg*4, "NCCE": ncce,
            "NREGUsed": nreg_used, "NREUsed": nreg_used*4,
            "MTot": nreg*8, "NSymbols": nsym}
