"""Independent exact and property checks for legacy Communications numerics."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_legacy_numeric import (berconfint, bi2de, compand, de2bi, hex2poly,
                                 modnorm, noisebw, oct2poly, quantiz, randerr,
                                 randsrc, vec2mat)


def main():
    assert bi2de([[1, 0, 1], [0, 1, 1]])["values"].tolist() == [5, 6]
    assert bi2de([[1, 0, 1]], "left-msb")["values"].tolist() == [5]
    assert de2bi([5, 6], 3)["bits"].tolist() == [[1, 0, 1], [0, 1, 1]]
    assert de2bi([6], 3, "left-msb")["bits"].tolist() == [[1, 1, 0]]
    assert hex2poly("0xB")["coefficients"] == [1, 0, 1, 1]
    assert oct2poly("13")["coefficients"] == [1, 0, 1, 1]
    assert hex2poly("B", "ascending")["coefficients"] == [1, 1, 0, 1]

    assert noisebw([1], [1], 8, 1000)["bandwidth_hz"] == 1000
    assert np.isclose(noisebw([1, 1], [1], 8, 1000)["bandwidth_hz"], 500)
    assert np.isclose(modnorm([1, -1, 3, -3])["scale"], 1 / np.sqrt(5))
    assert np.isclose(modnorm([1, -1, 3, -3], "peakpow", 9)["scale"], 1)
    matrix = vec2mat([1, 2, 3, 4, 5], 2, -1)
    assert matrix["matrix"].tolist() == [[1, 2], [3, 4], [5, -1]]
    assert matrix["padded"] == 1

    error_pattern = randerr(5, 8, 2, seed=7)["pattern"]
    assert error_pattern.shape == (5, 8) and np.all(error_pattern.sum(axis=1) == 2)
    assert np.array_equal(error_pattern, randerr(5, 8, 2, seed=7)["pattern"])
    source = randsrc(100, 1, [0, 1], [.0, 1.0], seed=3)["values"]
    assert source.shape == (100, 1) and np.all(source == 1)

    for method in ("mu/compressor", "A/compressor"):
        encoded = compand([-.8, 0, .8], 87, 1, method)["samples"]
        recovered = compand(encoded, 87, 1, method.replace("compressor", "expander"))["samples"]
        assert np.allclose(recovered, [-.8, 0, .8], atol=1e-12)
    q = quantiz([-.2, .5, .6, 2], [.5], [0, 1])
    assert q["indices"].tolist() == [0, 0, 1, 1]
    assert np.isclose(q["distortion"], (.04 + .25 + .16 + 1) / 4)

    interval = berconfint(0, 10)
    assert interval["ber"] == 0 and interval["interval"][0] == 0
    assert np.isclose(interval["interval"][1], 1 - .025**(.1))
    print("PASS 12 Communications legacy numeric entry slices")


if __name__ == "__main__":
    main()
