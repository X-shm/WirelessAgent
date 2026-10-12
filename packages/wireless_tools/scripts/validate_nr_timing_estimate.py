"""validate_nr_timing_estimate.py — Validate nr_timing_estimate against MATLAB golden samples."""
from __future__ import annotations
import json
import os
import sys
import numpy as np

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools')
SAMPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'matlab_oracle', 'samples')
sys.path.insert(0, TOOLS)

from nr_timing_estimate import nr_timing_estimate

passed = 0
failed = 0
failures = []


def check(name: str, ok: bool, detail: str = ""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        failures.append(name)
        print(f"  FAIL  {name}  {detail}")


def load_json(name):
    with open(os.path.join(SAMPLES, name), 'r', encoding='utf-8') as f:
        return json.load(f)


print("\n=== Timing Estimate ===")
try:
    d = load_json('nr_timing_estimate.json')
    for case_name, case in d.items():
        # Waveform: T x R
        wf_real = np.array(case['waveform_real'])
        wf_imag = np.array(case['waveform_imag'])
        if wf_real.ndim == 1:
            wf_real = wf_real.reshape(-1, 1)
            wf_imag = wf_imag.reshape(-1, 1)
        waveform = wf_real + 1j * wf_imag

        # Reference: T_ref x P
        ref_real = np.array(case['ref_real'])
        ref_imag = np.array(case['ref_imag'])
        if ref_real.ndim == 1:
            ref_real = ref_real.reshape(-1, 1)
            ref_imag = ref_imag.reshape(-1, 1)
        ref_waveform = ref_real + 1j * ref_imag

        expected_offset = case['offset']
        expected_mag = np.array(case['mag'], dtype=float)

        result_offset, result_mag_list, result_peak = nr_timing_estimate(waveform, ref_waveform)
        result_mag = np.array(result_mag_list, dtype=float)

        ok_offset = result_offset == expected_offset
        ok_mag = np.allclose(result_mag, expected_mag, atol=1e-10)

        ok = ok_offset and ok_mag
        detail = ""
        if not ok_offset:
            detail += f"offset: got {result_offset}, expected {expected_offset} "
        if not ok_mag:
            detail += f"mag_err={np.max(np.abs(result_mag-expected_mag)):.2e}"
        check(f"Timing {case_name}", ok, detail.strip())
except FileNotFoundError as e:
    print(f"  SKIP  (golden samples not found: {e})")

print(f"\nTotal: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
