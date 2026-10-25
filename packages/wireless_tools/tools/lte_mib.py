"""LTE 24-bit master information block encode and decode."""
from __future__ import annotations

import numpy as np


_BANDWIDTHS = (6, 15, 25, 50, 75, 100)
_NG = ("Sixth", "Half", "One", "Two")


def _field(value, width):
    return [(int(value) >> shift) & 1 for shift in range(width-1, -1, -1)]


def _number(bits):
    return sum(int(bit) << (len(bits)-1-k) for k, bit in enumerate(bits))


def mib(bits=None, nrb=6, ng="Sixth", nframe=0, phich_duration="Normal",
        fields=None):
    if bits is not None:
        data = np.asarray(bits, dtype=int).reshape(-1)
        if np.any((data != 0) & (data != 1)):
            raise ValueError("MIB bits must be binary")
        data = np.pad(data[:24], (0, max(0, 24-len(data))))
        bandwidth = _number(data[:3])
        decoded = {"NDLRB": _BANDWIDTHS[bandwidth] if bandwidth < 6 else 0,
                   "PHICHDuration": ("Normal", "Extended")[int(data[3])],
                   "Ng": _NG[_number(data[4:6])],
                   "NFrame": _number(data[6:14])*4}
        return {"bits": data.tolist(), "fields": decoded}

    fields = {} if fields is None else dict(fields)
    nrb = int(fields.get("NDLRB", nrb))
    ng = str(fields.get("Ng", ng))
    nframe = int(fields.get("NFrame", nframe))
    phich_duration = str(fields.get("PHICHDuration", phich_duration))
    if ng not in _NG or phich_duration not in ("Normal", "Extended"):
        raise ValueError("invalid Ng or PHICHDuration")
    if not 1 <= nrb <= 110 or not 0 <= nframe <= 1023:
        raise ValueError("NDLRB or NFrame outside LTE range")
    bandwidth = _BANDWIDTHS.index(nrb) if nrb in _BANDWIDTHS else 7
    data = (_field(bandwidth, 3) +
            [int(phich_duration == "Extended")] +
            _field(_NG.index(ng), 2) + _field(nframe//4, 8) + [0]*10)
    return {"bits": data, "fields": {"NDLRB": nrb, "PHICHDuration": phich_duration,
                                      "Ng": ng, "NFrame": nframe}}


def sl_mib(bits=None, nrb=6, duplex_mode="FDD", tdd_config=0, nframe=0,
           nsubframe=0, in_coverage=0, fields=None):
    if bits is not None:
        data = np.asarray(bits, dtype=int).reshape(-1)
        if np.any((data != 0) & (data != 1)):
            raise ValueError("Sidelink MIB bits must be binary")
        data = np.pad(data[:40], (0, max(0, 40-len(data))))
        bandwidth = _number(data[:3])
        duplex = _number(data[3:6])
        decoded = {"NSLRB": _BANDWIDTHS[bandwidth] if bandwidth < 6 else 0,
                   "DuplexMode": "FDD" if duplex == 0 else "TDD",
                   "TDDConfig": max(0, duplex-1),
                   "NFrame": _number(data[6:16]),
                   "NSubframe": _number(data[16:20]),
                   "InCoverage": int(data[20])}
        return {"bits": data.tolist(), "fields": decoded}

    fields = {} if fields is None else dict(fields)
    nrb = int(fields.get("NSLRB", nrb))
    duplex_mode = str(fields.get("DuplexMode", duplex_mode)).upper()
    tdd_config = int(fields.get("TDDConfig", tdd_config))
    nframe = int(fields.get("NFrame", nframe))
    nsubframe = int(fields.get("NSubframe", nsubframe))
    in_coverage = int(fields.get("InCoverage", in_coverage))
    if (not 1 <= nrb <= 110 or duplex_mode not in ("FDD", "TDD") or
            not 0 <= tdd_config <= 6 or not 0 <= nframe <= 1023 or
            not 0 <= nsubframe <= 9 or in_coverage not in (0, 1)):
        raise ValueError("invalid sidelink MIB fields")
    bandwidth = _BANDWIDTHS.index(nrb) if nrb in _BANDWIDTHS else 7
    data = (_field(bandwidth, 3) +
            _field(0 if duplex_mode == "FDD" else tdd_config+1, 3) +
            _field(nframe, 10) + _field(nsubframe, 4) +
            [in_coverage] + [0]*19)
    return {"bits": data, "fields": {"NSLRB": nrb, "DuplexMode": duplex_mode,
                                      "TDDConfig": tdd_config, "NFrame": nframe,
                                      "NSubframe": nsubframe, "InCoverage": in_coverage}}
