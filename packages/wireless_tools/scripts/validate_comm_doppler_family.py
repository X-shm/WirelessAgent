"""Doppler closed-form samples and energy/shape properties."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_doppler_family import (ajakesir, bellir, bigaussianir, doppler,
                                 flatir, gaussianir, jakesir, rjakesir,
                                 roundedir)


def main():
    t = np.linspace(-.02, .02, 41)
    flat = flatir(100, t)["impulse_response"]
    raw_flat = np.sqrt(200) * np.sinc(200 * t) * np.hamming(len(t))
    assert np.allclose(flat, raw_flat / np.linalg.norm(raw_flat))
    gaussian = gaussianir(100, t)["impulse_response"]
    assert np.argmax(gaussian) == 20 and np.allclose(gaussian, gaussian[::-1])
    jakes = jakesir(100, t)["impulse_response"]
    assert np.all(np.isfinite(jakes)) and np.allclose(jakes, jakes[::-1])
    responses = [flat, gaussian, jakes,
                 bellir(100, 1, t)["impulse_response"],
                 roundedir(100, [1, -.5], t)["impulse_response"],
                 bigaussianir(100, [.2, .2], [-.5, .5], [1, 1], t)["impulse_response"],
                 rjakesir(100, [-.8, .8], t)["impulse_response"],
                 ajakesir(100, [-.8, .8], t)["impulse_response"]]
    assert all(len(h) == len(t) and np.isclose(np.sum(abs(h)**2), 1) for h in responses)
    assert doppler("Jakes", maximum_shift=100)["parameters"]["maximum_shift"] == 100
    print("PASS 9 Communications Doppler entry slices")


if __name__ == "__main__":
    main()
