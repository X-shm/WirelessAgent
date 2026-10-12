"""Validate nr_ldpc_rm.py rate_match against MATLAB golden samples.

Each golden sample contains the full LDPC codeword and the expected
rate-matched output, so we can validate directly without regenerating.
"""
import json, sys, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from nr_ldpc_rm import rate_match

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "rate_match_samples.json").read_text(encoding="utf-8"))

ok = 0
for s in samples:
    bgn = s['bgn']
    zc = s['zc']
    outlen = s['outlen']
    rv = s['rv']
    mod = s['mod']
    nlayers = s['nlayers']
    codeword = np.array(s['codeword'], dtype=np.int8)
    expected = np.array(s['output'], dtype=np.int8)

    got = rate_match(codeword, outlen, rv, mod, nlayers)
    match = len(got) == len(expected) and np.array_equal(got, expected)
    if match:
        ok += 1
    print(f"{'PASS' if match else 'FAIL'} bgn={bgn} zc={zc} outlen={outlen} "
          f"rv={rv} mod={mod} nlayers={nlayers} "
          f"got_len={len(got)} exp_len={len(expected)}")

print(f"\n{ok}/{len(samples)} passed")
