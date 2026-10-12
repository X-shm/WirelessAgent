"""Validate nr_polar.py against MATLAB golden samples."""
import json, sys, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from nr_polar import polar_encode

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "polar_samples.json").read_text(encoding="utf-8"))

ok = 0
for s in samples:
    mode = s['mode']
    nmax = s['nmax']
    iil = s['iil']
    K = s['K']
    E = s['E']
    N = s['N']
    bits = np.array(s['input_bits'], dtype=np.uint8)
    expected = np.array(s['output_bits'], dtype=np.uint8)

    got = polar_encode(bits, E, nmax=nmax, iil=iil)
    len_got = len(got)
    len_exp = len(expected)
    match = (len_got == len_exp and
             len_got > 0 and
             np.array_equal(got, expected))
    if match:
        ok += 1

    print(f"{'PASS' if match else 'FAIL'} {mode} K={K} E={E} N={N} "
          f"got_len={len_got} exp_len={len_exp}")

print(f"\n{ok}/{len(samples)} passed")
