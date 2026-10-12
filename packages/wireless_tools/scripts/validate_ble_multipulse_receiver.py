"""Compare uncoded multi-symbol-pulse BLE PHY with R2026a."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from ble_ideal_receiver import receive
from ble_waveform import generate

cases = json.loads((ROOT / "matlab_oracle" / "samples" /
                    "ble_multipulse_receiver_samples.json").read_text(encoding="utf-8"))
for case in cases:
    message = np.asarray(case["message"], dtype=np.uint8)
    waveform, _ = generate(message, mode=case["mode"],
                           channel_index=case["channel_index"],
                           samples_per_symbol=case["samples_per_symbol"],
                           pulse_length=case["pulse_length"],
                           modulation_index=case["modulation_index"])
    oracle_wave = np.asarray(case["waveform_real"]) + 1j * np.asarray(case["waveform_imag"])
    assert waveform.shape == oracle_wave.shape
    assert np.max(np.abs(waveform - oracle_wave)) < 1e-10
    bits, address = receive(waveform, mode=case["mode"],
                            channel_index=case["channel_index"],
                            samples_per_symbol=case["samples_per_symbol"],
                            pulse_length=case["pulse_length"],
                            modulation_index=case["modulation_index"])
    assert bits.tolist() == case["bits"], (case["mode"], case["pulse_length"])
    assert address.tolist() == case["access_address"]
print(f"PASS {len(cases)} BLE uncoded multipulse receiver golden cases")
