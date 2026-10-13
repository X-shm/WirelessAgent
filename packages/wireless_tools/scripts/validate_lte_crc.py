"""Validate lte_crc.py against MATLAB golden samples."""
import json
import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lte_crc import crc_encode

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_crc_samples.json").read_text(encoding="utf-8"))

ok_count = 0
total = 0
for i, s in enumerate(samples):
    poly = s['poly']
    bits = np.array(s['bits'], dtype=np.int64)
    expected = np.array(s['crc'], dtype=np.int64)
    mask = s.get('mask', 0)
    got = crc_encode(bits, poly, mask)
    match = np.array_equal(got, expected)
    total += 1
    if match:
        ok_count += 1
    print(f"{'PASS' if match else 'FAIL'} {poly} len={len(bits)} mask={mask} fill={int(np.any(bits<0))}")

print(f"\n{ok_count}/{total} passed")
sys.exit(0 if ok_count == total else 1)
