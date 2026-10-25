"""Cell-specific LTE SRS subframe scheduling, TS 36.211 section 5.5.3.3."""
from __future__ import annotations

_FDD = (
    (1, 0), (2, 0), (2, 1), (5, 0), (5, 1), (5, 2), (5, 3),
    (5, [0, 1]), (5, [2, 3]), (10, 0), (10, 1), (10, 2),
    (10, 3), (10, [0, 1, 2, 3, 4, 6, 8]),
    (10, [0, 1, 2, 3, 4, 5, 6, 8]), (1, -1),
)
_TDD = (
    (5, 1), (5, [1, 2]), (5, [1, 3]), (5, [1, 4]),
    (5, [1, 2, 3]), (5, [1, 2, 4]), (5, [1, 3, 4]),
    (5, [1, 2, 3, 4]), (10, [1, 2, 6]), (10, [1, 3, 6]),
    (10, [1, 6, 7]), (10, [1, 2, 6, 8]), (10, [1, 3, 6, 9]),
    (10, [1, 4, 6, 7]), (1, -1), (1, -1),
)


def srs_info(subframe_config=0, duplex_mode="FDD", nsubframe=0):
    config = int(subframe_config)
    subframe = int(nsubframe)
    mode = str(duplex_mode).upper()
    if not 0 <= config <= 15:
        raise ValueError("subframe_config must be 0..15")
    if mode not in ("FDD", "TDD"):
        raise ValueError("duplex_mode must be FDD or TDD")
    if not 0 <= subframe <= 9:
        raise ValueError("nsubframe must be 0..9")
    period, offset = (_FDD if mode == "FDD" else _TDD)[config]
    offsets = offset if isinstance(offset, list) else [offset]
    return {"CellPeriod": period, "CellOffset": offset,
            "IsSRSSubframe": int(subframe % period in offsets)}
