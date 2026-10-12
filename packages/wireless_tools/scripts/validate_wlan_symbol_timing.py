"""Validate wlan_symbol_timing against MATLAB golden samples.

MATLAB reference: wlanSymbolTimingEstimate(x, chanbw, threshold)
Golden samples: matlab_oracle/samples/wlan_symbol_timing.json
"""
import json
import os
import sys

import numpy as np

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools')
SAMPLES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'matlab_oracle', 'samples', 'wlan_symbol_timing.json'
)
sys.path.insert(0, TOOLS)
from wlan_symbol_timing import lltf_waveform, symbol_timing_estimate


def to_array(v):
    """Golden samples store real/imag as Ns × Nr (row-major JSON)."""
    return np.asarray(v, dtype=float)


def main():
    with open(SAMPLES_PATH, 'r') as f:
        samples = json.load(f)

    total_ok = 0
    total_cases = 0

    # --- L-LTF amplitude normalization oracle ---
    print("== L-LTF amplitude normalization (mean power should be 1.0) ==")
    for key in sorted(k for k in samples if k.startswith('lltf_cbw')):
        s = samples[key]
        got = lltf_waveform(key.split('_')[1].upper())
        exp = to_array(s['real']) + 1j * to_array(s['imag'])

        len_ok = len(got) == s['length']
        # Relative error: golden samples are generated at double precision
        if len(got) == len(exp):
            err = np.max(np.abs(got - exp))
            rel = err / max(np.max(np.abs(exp)), 1e-15)
            amp_ok = abs(s['mean_power'] - 1.0) < 1e-9
            shape_ok = True
        else:
            err = rel = float('nan')
            amp_ok = shape_ok = False

        status = "PASS" if (len_ok and shape_ok and amp_ok and rel < 1e-9) else "FAIL"
        if status == "PASS":
            total_ok += 1
        total_cases += 1
        print(f"  {status} {key}: len={len(got)} rel_err={rel:.3e} "
              f"mean_power={s['mean_power']}")

    # Cross-check: public wlanLLTF == internal legacyLTF (numTx=1, CSD=0)
    print(f"\n  wlanLLTF vs wlan.internal.legacyLTF max diff: "
          f"{samples['lltf_public_vs_internal_maxdiff']}")

    # --- Symbol timing estimates ---
    print("\n== Symbol timing estimates ==")
    timing_keys = [k for k in samples if k.startswith('timing')]
    for key in timing_keys:
        s = samples[key]
        x = to_array(s['waveform_real']) + 1j * to_array(s['waveform_imag'])
        got_start, got_metric = symbol_timing_estimate(
            x, s['chanbw'], s['threshold'])

        exp_start = s['start_offset']
        exp_metric = to_array(s['metric'])

        if exp_start == []:
            start_ok = got_start is None and len(got_metric) == 0
        else:
            start_ok = got_start == exp_start
            metric_ok = len(got_metric) == len(exp_metric) and \
                np.allclose(got_metric, exp_metric, rtol=1e-9, atol=1e-12)

        status = "PASS" if (start_ok and metric_ok) else "FAIL"
        if status == "PASS":
            total_ok += 1
        total_cases += 1
        print(f"  {status} [{key}] chanbw={s['chanbw']} "
              f"threshold={s['threshold']} start_offset={got_start}"
              f" (expected {exp_start}) metric_n={len(got_metric)}")

    print(f"\n{total_ok}/{total_cases} passed")
    return 0 if total_ok == total_cases else 1


if __name__ == '__main__':
    sys.exit(main())