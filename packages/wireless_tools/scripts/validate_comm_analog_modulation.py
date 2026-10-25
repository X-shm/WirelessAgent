"""Fixed carrier formulas and noiseless analog modulation round trips."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_analog_modulation import (amdemod, ammod, fmdemod, fmmod,
                                    pmdemod, pmmod, ssbdemod, ssbmod)


def main():
    fs, fc = 1024, 128
    t = np.arange(1024) / fs
    x = .2 * np.cos(2 * np.pi * 8 * t)
    carrier = np.cos(2 * np.pi * fc * t)
    assert np.allclose(ammod(x, fc, fs)["samples"], x * carrier)
    assert np.max(abs(amdemod(ammod(x, fc, fs)["samples"], fc, fs,
                             cutoff_hz=16)["samples"] - x)) < 1e-12

    fm = fmmod(x, fc, fs, 20)["samples"]
    expected_phase = 2 * np.pi * fc * t + 2 * np.pi * 20 * np.cumsum(x) / fs
    assert np.allclose(fm, np.cos(expected_phase))
    assert np.max(abs(fmdemod(fm, fc, fs, 20)["samples"][20:-20] - x[20:-20])) < 1e-9

    pm = pmmod(x, fc, fs, 1)["samples"]
    assert np.allclose(pm, np.cos(2 * np.pi * fc * t + x))
    assert np.max(abs(pmdemod(pm, fc, fs, 1)["samples"][20:-20] - x[20:-20])) < 1e-9

    for sideband in ("lower", "upper"):
        ssb = ssbmod(x, fc, fs, sideband)["samples"]
        recovered = ssbdemod(ssb, fc, fs, sideband, cutoff_hz=16)["samples"]
        assert np.max(abs(recovered - x)) < 1e-12
    print("PASS 8 Communications sampled analog modulation entry slices")


if __name__ == "__main__":
    main()
