"""Check complete R2026a MATLAB vectors for selected new NR subsets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from nr_bch_codec import bch, bch_decode
from nr_channel_models import path_loss
from nr_control_codec import uci_encode, uci_decode
from nr_pucch_family import pucch1, pucch_decode


def main() -> int:
    sample = json.loads((ROOT / "matlab_oracle" / "samples" /
                         "nr_remaining_oracle.json").read_text(encoding="utf-8"))
    assert sample["matlab_release"] == "2026a"
    checks = 0

    for case in sample["bch"]:
        expected = np.asarray(case["codeword"], dtype=np.uint8).reshape(-1)
        actual = bch(case["payload"], case["sfn"], case["hrf"], case["lssb"],
                     case["idxoffset"], case["ncellid"])["codeword"]
        assert len(expected) == 864 and np.array_equal(actual, expected)
        decoded = bch_decode((1 - 2 * expected.astype(float)) * 25,
                             case["lssb"], case["ncellid"])
        assert decoded["crc_ok"]
        assert np.array_equal(decoded["payload"], np.asarray(case["payload"]).reshape(-1))
        checks += 1

    for case in sample["uci"]:
        expected = np.asarray(case["codeword"], dtype=np.uint8).reshape(-1)
        actual = uci_encode(case["payload"], case["e"])["codeword"]
        assert len(expected) == case["e"] and np.array_equal(actual, expected)
        decoded = uci_decode((1 - 2 * expected.astype(float)) * 25,
                             len(np.asarray(case["payload"]).reshape(-1)))
        assert decoded["crc_ok"]
        assert np.array_equal(decoded["payload"], np.asarray(case["payload"]).reshape(-1))
        checks += 1

    case = sample["uma_los"]
    actual = path_loss(case["freq_hz"], case["bs"], case["ue"], True, "UMa")
    assert abs(actual["pathloss_db"] - case["pathloss_db"]) < 1e-10
    assert actual["shadow_fading_std_db"] == case["shadow_fading_std_db"]
    checks += 1

    for case in sample["pucch1"]:
        ack = np.asarray(case["ack"], dtype=np.uint8).reshape(-1)
        expected = (np.asarray(case["symbols_real"]).reshape(-1) +
                    1j * np.asarray(case["symbols_imag"]).reshape(-1))
        actual = pucch1(ack, nid=7, num_symbols=4, slot=case["slot"])["symbols"]
        assert len(expected) == 24 and np.allclose(actual, expected, atol=1e-12, rtol=0)
        decoded = pucch_decode(expected, 1, nid=7, num_symbols=4,
                               uci_bits_length=len(ack), slot=case["slot"])
        assert np.array_equal(decoded["bits"], ack)
        checks += 1

    print(f"PASS {checks} complete MATLAB R2026a NR oracle cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
