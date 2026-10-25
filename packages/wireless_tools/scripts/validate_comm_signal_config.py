"""Independent properties for signal config slices."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_signal_config import (arrayConfig, dpdPreprocessor, iqcoef2imbal, iqimbal,
                                iqimbal2coef, ofdmPilotConfig, ofdmPilotGrid,
                                ofdmPrecode, srmdelay)


def main():
    assert arrayConfig([2, 2], .5)["element_positions"][-1] == [0.0, .5, .5]
    assert ofdmPilotConfig([[0, 0], [2, 1]], [1, -1])["indices"] == [[0, 0], [2, 1]]
    assert ofdmPilotGrid(3, 2, [[2, 1]], 2)["grid"][2, 1] == 2
    x = np.arange(8).reshape(2, 2, 2)
    p = [[1, 0], [0, 1]]
    assert np.allclose(ofdmPrecode(x, p)["symbols"], x)
    samples = np.array([1+1j, -1+2j])
    assert np.allclose(iqimbal(samples, 0)["samples"], samples)
    c = iqimbal2coef(2, 15)["coefficient"].item()
    recovered = iqcoef2imbal([c])
    assert np.isclose(recovered["amplitude_db"][0], 2, atol=1e-5)
    assert np.isclose(recovered["phase_deg"][0], 15, atol=1e-5)
    assert srmdelay([1, 2], [4, 4], 2, 4)["rate_factors"] == [[2, 1], [1, 1]]
    features = dpdPreprocessor([1+2j, 3+4j], 2, [1, 2])["features"]
    assert features.shape == (2, 6) and np.allclose(features[1, :2], [1, 3])
    print("PASS 9 Communications signal/config entry slices")


if __name__ == "__main__":
    main()
