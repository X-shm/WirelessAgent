"""Validate nr_ldpc.py encode against MATLAB golden samples."""
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from nr_ldpc import encode

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "ldpc_samples.json").read_text(encoding="utf-8"))

ok = 0
for s in samples:
    bgn, zc = s['bgn'], s['zc']
    info = np.array(s['info'], dtype=np.int8)
    expected = np.array(s['codeword'], dtype=np.int8)
    try:
        got = encode(info, bgn)
        match = np.array_equal(got, expected)
        if match:
            ok += 1
        print(f"{'PASS' if match else 'FAIL'} BG{bgn} Zc={zc} n={len(expected)} (first mismatches: "
              f"{np.nonzero(got != expected)[0][:5].tolist() if not match else 'none'})")
    except Exception as e:
        print(f"ERROR BG{bgn} Zc={zc}: {e}")

print(f"\n{ok}/{len(samples)} passed")
