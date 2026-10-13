"""Validate lte_tbs.py against MATLAB golden samples."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lte_tbs import tbs

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_tbs_samples.json").read_text(encoding="utf-8"))


def to_list(x):
    if isinstance(x, list):
        return x
    return [x]


ok_count = 0
total = 0
for s in samples:
    nprb = s['nprb']
    smnlayer = s['smnlayer']
    if s['type'] == 'nprb':
        got = tbs(nprb)
        exp = s['tbs']
    else:
        itbs = None if not s['itbs'] else s['itbs']
        got = tbs(nprb, itbs, smnlayer)
        exp = s['tbs']
    match = all(a == b for a, b in zip(to_list(got), to_list(exp))) and \
        len(to_list(got)) == len(to_list(exp))
    total += 1
    if match:
        ok_count += 1
    print(f"{'PASS' if match else 'FAIL'} {s['type']} nprb={nprb} L={smnlayer}")

print(f"\n{ok_count}/{total} passed")
sys.exit(0 if ok_count == total else 1)
