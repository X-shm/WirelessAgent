"""LDPC matrix and codec invariants including all DVB-S2 rates."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from comm_ldpc_family import (dvbs2ldpc, ldpcDecode, ldpcDecoderConfig,
                              ldpcEncode, ldpcEncoderConfig, ldpcPCM,
                              ldpcQuasiCyclicMatrix)


def main():
    data = json.loads((Path(__file__).resolve().parents[1] / "matlab_oracle" / "samples" /
                       "comm_dvbs2_tables.json").read_text(encoding="utf-8"))
    for rate in data:
        window = dvbs2ldpc(rate, 0, 5)
        assert window["shape"] == [5, 64800]
        assert len(window["row_indices"]) == len(window["col_indices"])
        assert all(0 <= r < 5 for r in window["row_indices"])
    q = ldpcQuasiCyclicMatrix(3, [[0, -1, 1]])
    assert q["shape"] == [3, 9] and len(q["row_indices"]) == 6
    h = [[1, 1, 0], [0, 1, 1]]
    assert ldpcPCM(h=h)["shape"] == [2, 3]
    enc = ldpcEncoderConfig(h)
    dec = ldpcDecoderConfig(h)
    assert enc["num_information_bits"] == dec["num_information_bits"] == 1
    code = ldpcEncode([1], enc)["codeword"]
    assert code.tolist() == [1, 1, 1]
    decoded = ldpcDecode(np.where(code, -8.0, 8.0), dec)
    assert decoded["information_bits"].tolist() == [1]
    assert not np.any(decoded["final_parity_checks"])
    print("PASS 7 Communications LDPC entry slices, 11 DVB-S2 rate tables")


if __name__ == "__main__":
    main()
