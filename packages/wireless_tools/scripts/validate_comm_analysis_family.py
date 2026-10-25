"""Independent checks for BER and headless visualization data."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.special import erfc

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_analysis_family import berfit, bersync, eyediagram, scatterplot, semianalytic


def main():
    fitted = berfit([0, 2, 4], [.2, .1, .02])["ber"]
    assert np.all(np.diff(fitted) < 0) and np.isclose(fitted[1], .1)
    assert np.isclose(bersync([0], 0)["ber"][0], .5*erfc(1))
    assert bersync([3], .1)["ber"][0] > bersync([3], 0)["ber"][0]
    assert scatterplot([1, 2, 3, 4], 2)["sample_indices"].tolist() == [0, 2]
    assert eyediagram(list(range(16)), 4)["trace_count"] == 3
    constellation = [-1, 1]
    result = semianalytic(constellation, constellation, "psk/nondiff", 2, 1, [10], 10000, 123)
    assert result["ber"][0] < .01
    print("PASS 5 Communications analysis entry slices")


if __name__ == "__main__":
    main()
