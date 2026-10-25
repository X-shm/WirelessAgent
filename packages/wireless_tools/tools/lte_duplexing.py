"""LTE FDD and normal-prefix TDD SSC-0 subframe geometry."""
from __future__ import annotations


_TDD = ("DSUUUDSUUU", "DSUUDDSUUD", "DSUDDDSUDD",
        "DSUUUDDDDD", "DSUUDDDDDD", "DSUDDDDDDD",
        "DSUUUDSUUD")


def duplexing_info(duplex_mode="FDD", tdd_config=0, nsubframe=0,
                   cyclic_prefix="Normal", cyclic_prefix_ul=None, ssc=0):
    mode = str(duplex_mode).upper()
    cp_dl = str(cyclic_prefix).lower()
    cp_ul = "normal" if cyclic_prefix_ul is None else str(cyclic_prefix_ul).lower()
    if mode not in ("FDD", "TDD") or cp_dl not in ("normal", "extended") or cp_ul not in ("normal", "extended"):
        raise ValueError("invalid duplex mode or cyclic prefix")
    if mode == "FDD":
        kind = "Uplink" if cyclic_prefix_ul is not None else "Downlink"
    else:
        tdd_config, nsubframe = int(tdd_config), int(nsubframe)
        if not 0 <= tdd_config <= 6 or not 0 <= nsubframe <= 9:
            raise ValueError("invalid TDD configuration or subframe")
        kind = {"D": "Downlink", "S": "Special", "U": "Uplink"}[
            _TDD[tdd_config][nsubframe]]
    if kind == "Special":
        if int(ssc) != 0 or cp_dl != "normal" or cp_ul != "normal":
            raise ValueError("this subset supports normal-prefix TDD SSC 0")
        counts = (3, 10, 1)
    elif kind == "Downlink":
        counts = (14 if cp_dl == "normal" else 12, 0, 0)
    else:
        counts = (0, 0, 14 if cp_ul == "normal" else 12)
    info = {"SubframeType": kind, "NSymbols": sum(counts),
            "NSymbolsDL": counts[0], "NSymbolsGuard": counts[1],
            "NSymbolsUL": counts[2]}
    return info
