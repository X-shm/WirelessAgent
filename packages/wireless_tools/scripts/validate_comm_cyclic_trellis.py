"""GF(2) cyclic and trellis invariants."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_cyclic_trellis import (cyclgen, cyclpoly, distspec, gen2par,
                                 iscatastrophic, istrellis, mask2shift,
                                 shift2mask, syndtable)


def main():
    p = cyclpoly(7, 4)["polynomials_ascending"][0]
    result = cyclgen(7, p)
    g, h = result["generator"], result["parity_check"]
    assert g.shape == (4, 7) and h.shape == (3, 7) and not np.any((h @ g.T) & 1)
    assert np.array_equal(gen2par(g)["matrix"], h)
    table = syndtable(h)["coset_leaders"]
    assert len(table) == 8 and table[0] == [0]*7
    trellis = {"numInputSymbols": 2, "numOutputSymbols": 4, "numStates": 1,
               "nextStates": [[0, 0]], "outputs": [[0, 3]]}
    assert istrellis(trellis)["valid"] and not iscatastrophic(trellis)["catastrophic"]
    assert distspec(trellis, 1)["dfree"] == 2
    mask = shift2mask([1, 0, 1, 1], 2)["mask"]
    assert mask2shift([1, 0, 1, 1], mask)["shift"] == 2
    print("PASS 9 Communications cyclic/trellis entry slices")


if __name__ == "__main__":
    main()
