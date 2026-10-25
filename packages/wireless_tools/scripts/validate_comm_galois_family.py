"""Independent GF(2^m), prime-field and polynomial reference checks."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_galois_family import (cosets, gf, gfcosets, gfdiv, gflineq,
                                gfminpol, gfpretty, gfprimck, gfprimdf,
                                gfprimfd, gfrank, gfrepcov, gfroots,
                                gfsub, gftable, gftuple, gfweight,
                                isprimitive, primpoly)


def main():
    assert gf([0, 1, 2, 3], 2)["values"].tolist() == [0, 1, 2, 3]
    assert gfdiv([1, 2, 3], [1, 2, 3], 2)["values"].tolist() == [1, 1, 1]
    assert gfsub([1, 2, 3], [1, 1, 1], 3)["values"].tolist() == [0, 1, 2]
    solved = gflineq([[1, 1], [1, 0]], [1, 0])
    assert solved["valid"] and solved["solution"].tolist() == [0, 1]
    assert not gflineq([[1, 1], [1, 1]], [0, 1])["valid"]
    assert gfrank([[1, 1], [1, 0]])["rank"] == 2
    assert gfrank([[1, 1], [1, 1]])["rank"] == 1
    assert gfrepcov([0, 3, 4])["coefficients_ascending"] == [1, 0, 0, 1, 1]
    assert gfpretty([1, 0, 1])["polynomial"] == "x^2 + 1"
    assert cosets(3)["cosets"] == [[0], [1, 2, 4], [3, 6, 5]]
    assert gfcosets(3)["cosets"] == cosets(3)["cosets"]
    assert gfprimck(0xB)["primitive"] and isprimitive(0xB)["primitive"]
    assert not gfprimck(0xF)["primitive"]
    assert gfprimdf(3)["polynomial"] == 0xB
    assert gfprimfd(3, True)["polynomials"] == [0xB, 0xD]
    assert primpoly(3)["polynomials"] == [0xB]
    table = gftable(3)
    assert table["exp"][:4] == [1, 2, 4, 3]
    assert gftuple([0, 1, 2], 2)["exponents"] == [-1, 0, 1]
    assert gfroots([1, 0, 1])["roots"] == [1]
    assert gfweight([[1, 0, 1], [0, 1, 1]])["minimum_distance"] == 2
    assert gfminpol([1, 3], 3)["polynomials_descending"] == [
        [1, 0, 1, 1], [1, 1, 0, 1]]
    print("PASS 19 Communications Galois and polynomial entry slices")


if __name__ == "__main__":
    main()
