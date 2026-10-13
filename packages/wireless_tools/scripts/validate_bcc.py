"""Validate wlan_bcc.py against MATLAB golden samples."""
import json, sys, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from wlan_bcc import bcc_decode, bcc_encode

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "bcc_samples.json").read_text(encoding="utf-8"))

ok = 0
total = 0
for s in samples:
    rate = s['rate']
    bits = np.array(s['input_bits'], dtype=np.uint8)
    expected = np.array(s['output_bits'], dtype=np.uint8)
    got = bcc_encode(bits, rate)
    match = len(got) == len(expected) and np.array_equal(got, expected)
    total += 1
    if match:
        ok += 1
    print(f"{'PASS' if match else 'FAIL'} rate={rate} in={s['input_len']} "
          f"out={len(got)} exp={s['output_len']} match={match}")

    decoded = bcc_decode(expected, rate)
    round_trip = np.array_equal(decoded, bits)
    total += 1
    if round_trip:
        ok += 1
    print(f"{'PASS' if round_trip else 'FAIL'} rate={rate} hard-decision round trip")

    # A central single-bit hard-decision error avoids the un-terminated
    # trellis boundary and should be correctable for every supported rate.
    corrupted = expected.copy()
    corrupted[len(corrupted) // 2] ^= 1
    corrected = bcc_decode(corrupted, rate)
    single_error = np.array_equal(corrected, bits)
    total += 1
    if single_error:
        ok += 1
    print(f"{'PASS' if single_error else 'FAIL'} rate={rate} single-error correction")

print(f"\n{ok}/{total} BCC checks passed")
sys.exit(0 if ok == total else 1)
