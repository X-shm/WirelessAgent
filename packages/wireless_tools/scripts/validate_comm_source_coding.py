"""Independent source-coding invariants and exact small examples."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_source_coding import (arithdeco, arithenco, dpcmdeco, dpcmenco,
                                dpcmopt, huffmandeco, huffmandict,
                                huffmanenco, lloyds)


def main():
    d = huffmandict([1, 2, 3], [.5, .25, .25])
    assert d["dictionary"] == [
        {"symbol": 1, "code": [0]}, {"symbol": 2, "code": [1, 0]},
        {"symbol": 3, "code": [1, 1]}]
    assert d["average_length"] == 1.5
    data = [1, 3, 2, 1, 1, 3]
    encoded = huffmanenco(data, d)["bits"]
    assert huffmandeco(encoded, d)["symbols"] == data

    rng = np.random.default_rng(21)
    for alphabet in range(2, 7):
        counts = rng.integers(1, 10, alphabet).tolist()
        for length in (1, 8, 100):
            symbols = rng.integers(1, alphabet + 1, length).tolist()
            stream = arithenco(symbols, counts)["bits"]
            assert arithdeco(stream, counts, length)["symbols"] == symbols

    q = lloyds([-1, -.8, .8, 1], 2)
    assert np.allclose(q["partition"], [0])
    assert np.allclose(q["codebook"], [-.9, .9])
    assert np.isclose(q["distortion"], .01)
    opt = dpcmopt([0, 1, 0, 1, 0, 1], 1, 2)
    assert len(opt["predictor"]) == 1 and len(opt["codebook"]) == 2
    coded = dpcmenco([0, 1, 0, 1], [0, 1], [.5])
    assert dpcmdeco(coded["indices"], [0, 1], [.5])["samples"] == coded["samples"]
    print("PASS 9 Communications source-coding entry slices")


if __name__ == "__main__":
    main()
