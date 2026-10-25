"""Polynomial CRC vectors and detected-error checks."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_crc_family import crcConfig, crcDetect, crcGenerate


def main():
    cfg = crcConfig("z^3+z+1")
    # Complete local MATLAB R2026a crcGenerate vector for this input/config.
    assert crcGenerate([1, 0, 1, 1], cfg)["codeword"] == [1, 0, 1, 1, 0, 0, 0]
    assert crcDetect([1, 0, 1, 1, 0, 0, 0], cfg) == {
        "message": [1, 0, 1, 1], "errors": [False], "valid": True}
    corrupted = [1, 0, 1, 1, 0, 1, 0]
    assert crcDetect(corrupted, cfg)["errors"] == [True]

    rng = np.random.default_rng(17)
    for count in (1, 2, 4):
        config = crcConfig([1, 0, 0, 1, 1], checksums_per_frame=count)
        payload = rng.integers(0, 2, 16 * count).tolist()
        encoded = crcGenerate(payload, config)["codeword"]
        checked = crcDetect(encoded, config)
        assert checked["valid"] and checked["message"] == payload
    print("PASS 3 Communications CRC entry slices")


if __name__ == "__main__":
    main()
