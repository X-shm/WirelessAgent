"""Noiseless and one-bit-error sequence codec checks."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_sequence_decode import mlseeq, tpcdec, tpcenc, vitdeccore


def main():
    msg = np.arange(16) & 1
    code = tpcenc(msg, [7, 7], [4, 4])["codeword"]
    assert len(code) == 49
    llr = np.where(code, -8.0, 8.0)
    llr[3] *= -1
    assert np.array_equal(tpcdec(llr, [7, 7], [4, 4])["message"], msg)
    observed = [1, -1, 1, 1, -1]
    assert mlseeq(observed, [1], [-1, 1])["symbols"].tolist() == observed
    trellis = {"numInputSymbols": 2, "numOutputSymbols": 4, "numStates": 1,
               "nextStates": [[0, 0]], "outputs": [[0, 3]]}
    assert vitdeccore([0, 0, 1, 1, 1, 1], trellis)["decoded_bits"].tolist() == [0, 1, 1]
    print("PASS 4 Communications sequence entry slices")


if __name__ == "__main__":
    main()
