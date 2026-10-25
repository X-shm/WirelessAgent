"""MATLAB reference permutations and shift-register round trips."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_interleaver_family import (algdeintrlv, algintrlv, convdeintrlv,
                                     convintrlv, heldeintrlv, helintrlv,
                                     helscandeintrlv, helscanintrlv,
                                     muxdeintrlv, muxintrlv)


def main():
    source = list(range(8))
    encoded = algintrlv(source, 8, "takeshita-costello", k=3, h=1)["data"]
    assert encoded.tolist() == [2, 6, 1, 0, 7, 5, 4, 3]  # MATLAB R2026a
    assert algdeintrlv(encoded, 8, "takeshita-costello", k=3, h=1)["data"].tolist() == source
    welch = algintrlv(list(range(6)), 6, "welch-costas", alpha=3)["data"]
    assert algdeintrlv(welch, 6, "welch-costas", alpha=3)["data"].tolist() == list(range(6))

    spiral = helscanintrlv(list(range(12)), 3, 4, 1)["data"]
    assert spiral.tolist() == [0, 5, 10, 3, 4, 9, 2, 7, 8, 1, 6, 11]  # MATLAB R2026a
    assert helscandeintrlv(spiral, 3, 4, 1)["data"].tolist() == list(range(12))

    data = list(range(24))
    shift = convintrlv(data, 3, 1)
    assert shift["data"][:12] == [0, 0, 0, 3, 1, 0, 6, 4, 2, 9, 7, 5]  # MATLAB R2026a
    assert convdeintrlv(shift["data"], 3, 1)["data"][6:] == data[:-6]
    assert muxintrlv(data, [0, 1, 2])["data"] == shift["data"]
    assert muxdeintrlv(shift["data"], [0, 1, 2])["data"][6:] == data[:-6]
    helical = helintrlv(data, 3, 2, 1)["data"]
    assert heldeintrlv(helical, 3, 2, 1)["data"][6:] == data[:-6]
    first = muxintrlv(data[:12], [0, 1, 2])
    second = muxintrlv(data[12:], [0, 1, 2], first["state"])
    assert first["data"] + second["data"] == muxintrlv(data, [0, 1, 2])["data"]
    print("PASS 10 Communications interleaver entry slices")


if __name__ == "__main__":
    main()
