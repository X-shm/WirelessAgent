"""Validate wlan_scramble against MATLAB golden samples."""
import json
import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.wlan_scramble import scramble

SAMPLES_PATH = ROOT / "matlab_oracle" / "samples" / "scramble_samples.json"


def main():
    samples = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))

    ok = 0
    total = len(samples)

    for i, s in enumerate(samples):
        name = s['case_name']
        seed = s['seed']
        inp = np.array(s['input_bits'], dtype=np.uint8)
        exp_scr = np.array(s['scrambled_bits'], dtype=np.uint8)

        # Test scrambling direction
        got_scr = scramble(inp, seed)
        scr_match = np.array_equal(got_scr, exp_scr)

        # Test descrambling roundtrip
        got_desc = scramble(got_scr, seed)
        desc_match = np.array_equal(got_desc, inp)

        status = "PASS" if (scr_match and desc_match) else "FAIL"
        if scr_match and desc_match:
            ok += 1
            print(f"  {status} [{i+1}/{total}] {name}: seed={seed} len={len(inp)}")
        else:
            print(f"  {status} [{i+1}/{total}] {name}: seed={seed} len={len(inp)}")
            if not scr_match:
                mismatches = np.sum(got_scr != exp_scr)
                print(f"    scramble mismatches: {mismatches}/{len(exp_scr)}")
                print(f"    first 16 expected: {exp_scr[:16].tolist()}")
                print(f"    first 16 got:      {got_scr[:16].tolist()}")
            if not desc_match:
                mismatches = np.sum(got_desc != inp)
                print(f"    descramble roundtrip errors: {mismatches}")

    print(f"\n{ok}/{total} passed")
    return 0 if ok == total else 1


if __name__ == '__main__':
    sys.exit(main())
