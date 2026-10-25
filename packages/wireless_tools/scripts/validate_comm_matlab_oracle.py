"""Differential samples from local MATLAB R2026a for key Communications slices."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from comm_analysis_family import bersync
from comm_cyclic_trellis import cyclgen
from comm_gsm_family import gsmDownlinkConfig, gsmInfo
from comm_ldpc_family import dvbs2ldpc
from comm_sequence_decode import tpcenc
from comm_signal_config import iqimbal2coef, ofdmPrecode


def main():
    sample = json.loads((ROOT / "matlab_oracle" / "samples" /
                         "comm_remaining_oracle.json").read_text(encoding="utf-8"))
    cyclic = cyclgen(7, [1, 1, 0, 1])
    assert np.array_equal(cyclic["parity_check"], sample["cyclgen"]["h"]), "cyclgen H"
    assert np.array_equal(cyclic["generator"], sample["cyclgen"]["g"]), "cyclgen G"
    assert np.array_equal(tpcenc(np.arange(16)&1, [7, 7], [4, 4])["codeword"],
                          sample["tpcenc"]), "tpcenc"
    coeff = iqimbal2coef(2, 15)["coefficient"].item()
    assert np.isclose(coeff, complex(sample["iqimbal2coef"]["real"],
                                     sample["iqimbal2coef"]["imag"])), "iqimbal2coef"
    grid = np.arange(8).reshape(2, 2, 2, order="F")
    assert np.array_equal(ofdmPrecode(grid, np.eye(2))["symbols"],
                          sample["ofdmPrecode"]), "ofdmPrecode"
    assert np.allclose(bersync([0, 5], .1)["ber"], sample["bersync"], atol=1e-5), "bersync"
    info = gsmInfo(gsmDownlinkConfig())
    for python_key, matlab_key in (("symbol_rate", "SymbolRate"),
                                   ("sample_rate", "SampleRate"),
                                   ("frame_length_samples", "FrameLengthInSamples")):
        assert np.isclose(info[python_key], sample["gsmInfo"][matlab_key]), "gsmInfo"
    sparse = dvbs2ldpc("1/2", row_start=0, row_stop=5)
    pairs = {(r+1, c+1) for r, c in zip(sparse["row_indices"], sparse["col_indices"])}
    assert pairs == {tuple(pair) for pair in sample["dvbs2ldpc_first5"]}, "dvbs2ldpc"
    print("PASS 7 key Communications functions against MATLAB R2026a samples")


if __name__ == "__main__":
    main()
