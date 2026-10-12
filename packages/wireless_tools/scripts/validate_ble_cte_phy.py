"""Compare LE CTE waveform and data-bit recovery with R2026a."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ble_ideal_receiver import receive
from ble_waveform import generate

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "ble_cte_phy_samples.json").read_text(encoding="utf-8"))
for case in cases:
    message = np.asarray(case["message"], dtype=np.uint8)
    waveform, detail = generate(message, mode=case["mode"],
                                channel_index=case["channel_index"],
                                samples_per_symbol=case["samples_per_symbol"],
                                whiten_status=case["whiten_status"],
                                pulse_length=case["pulse_length"],
                                modulation_index=case["modulation_index"],
                                df_packet_type=case["df_packet_type"])
    expected = np.asarray(case["waveform_real"]) + 1j * np.asarray(case["waveform_imag"])
    assert waveform.size == expected.size, (case["mode"], waveform.size, expected.size)
    assert float(np.max(np.abs(waveform - expected))) < 1e-10, case["df_packet_type"]
    factor = 2 if case["mode"] == "LE2M" else 1
    assert detail["cte_symbols"] == case["cte_time"] * 8 * factor
    bits, address, iq = receive(waveform, mode=case["mode"],
                                channel_index=case["channel_index"],
                                samples_per_symbol=case["samples_per_symbol"],
                                whiten_status=case["whiten_status"],
                                pulse_length=case["pulse_length"],
                                modulation_index=case["modulation_index"],
                                df_packet_type=case["df_packet_type"],
                                return_iq=True)
    assert bits.tolist() == case["bits"], (case["mode"], case["df_packet_type"])
    assert address.tolist() == case["access_address"]
    oracle_iq = np.asarray(case["iq_real"]) + 1j * np.asarray(case["iq_imag"])
    assert iq.shape == oracle_iq.shape, (case["mode"], iq.shape, oracle_iq.shape)
    assert np.max(np.abs(iq - oracle_iq)) < 1e-10, case["df_packet_type"]
print(f"PASS {len(cases)} BLE CTE waveform/receiver golden cases")
