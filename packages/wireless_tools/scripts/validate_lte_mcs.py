"""Validate lte_mcs.py against MATLAB golden samples."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lte_mcs import mcs

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_mcs_samples.json").read_text(encoding="utf-8"))


def to_list(x):
    if isinstance(x, list):
        return x
    return [x]


ok_count = 0
total = 0
for i, s in enumerate(samples):
    got = mcs(s['imcs'], s['table'])
    got_l = [to_list(g) for g in got]
    exp_l = [to_list(e) for e in (s['itbs'], s['mod'], s['rv'])]
    match = all(g == e for g, e in zip(got_l, exp_l))
    total += 1
    if match:
        ok_count += 1
    label = "scalar" if isinstance(s['imcs'], int) else f"n={len(s['imcs'])}"
    print(f"{'PASS' if match else 'FAIL'} {s['table']} {label}")

print(f"\n{ok_count}/{total} passed")
sys.exit(0 if ok_count == total else 1)
