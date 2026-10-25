"""Modulation round trips and complete MATLAB MIL-188 constellations."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from comm_digital_modulation import (apskdemod, apskmod, genqamdemod,
                                     genqammod, mil188qamdemod,
                                     mil188qammod, mskdemod, mskmod)


def main():
    apsk = list(range(16))
    modulated = apskmod(apsk, [4, 12], [1, 2], [0, np.pi / 12])
    assert apskdemod(modulated["samples"], [4, 12], [1, 2],
                     [0, np.pi / 12])["symbols"].tolist() == apsk
    constellation = {"real": [-1, 1, -1, 1], "imag": [-1, -1, 1, 1]}
    symbols = [0, 3, 2, 1, 0]
    qam = genqammod(symbols, constellation)["samples"]
    assert genqamdemod(qam, constellation)["symbols"].tolist() == symbols

    golden = json.loads((ROOT / "matlab_oracle" / "samples" /
                         "comm_mil188_constellations.json").read_text(encoding="utf-8"))
    for order in (16, 32, 64, 256):
        expected = np.asarray(golden[f"M{order}"]["real"]) + 1j * np.asarray(golden[f"M{order}"]["imag"])
        actual = mil188qammod(list(range(order)), order)["samples"]
        assert np.array_equal(actual, expected)
        assert mil188qamdemod(actual, order)["symbols"].tolist() == list(range(order))

    bits = [0, 1, 1, 0, 1, 0, 0, 1]
    waveform = mskmod(bits, 8)["samples"]
    assert np.allclose(abs(waveform), 1)
    assert mskdemod(waveform, 8)["bits"].tolist() == bits
    print("PASS 8 Communications digital-modulation entry slices and 368 MIL-188 golden symbols")


if __name__ == "__main__":
    main()
