"""validate_nr_pbch.py — Validate nr_pbch against MATLAB golden samples."""
from __future__ import annotations
import json
import os
import sys
import numpy as np

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools')
SAMPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'matlab_oracle', 'samples')
sys.path.insert(0, TOOLS)

from nr_pbch import pbch_encode, pbch_decode

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


# ── 1. PBCH Encode ──
print("\n=== PBCH Encode ===")
try:
    d = load_json('nr_pbch.json')
    encode_cases = [(k, v) for k, v in d.items() if k.startswith('encode_')]
    for case_name, case in encode_cases:
        cw = np.array(case['cw'], dtype=np.int8)
        ncellid = case['ncellid']
        v = case['v']
        expected = np.array(case['sym_real']) + 1j * np.array(case['sym_imag'])
        result = pbch_encode(cw, ncellid, v)
        ok = np.allclose(result, expected, atol=1e-10)
        check(f"Encode {case_name}", ok,
              f"max_err={np.max(np.abs(result-expected)):.2e}" if not ok else "")
except FileNotFoundError as e:
    print(f"  SKIP  (golden samples not found: {e})")

# ── 2. PBCH Decode ──
print("\n=== PBCH Decode ===")
try:
    d = load_json('nr_pbch.json')
    decode_cases = [(k, v) for k, v in d.items() if k.startswith('decode_')]
    for case_name, case in decode_cases:
        sym = np.array(case['sym_real']) + 1j * np.array(case['sym_imag'])
        ncellid = case['ncellid']
        v = case['v']
        nvar = case.get('nvar', 1e-10)
        expected = np.array(case['soft_bits'], dtype=float)
        result = pbch_decode(sym, ncellid, v, nvar)
        # Match MATLAB sign convention: soft bits < 0 => bit=1
        # Verify relative tolerance since numerical methods may differ slightly
        ok = np.allclose(result, expected, atol=1e-6, rtol=1e-4)
        check(f"Decode {case_name}", ok,
              f"max_err={np.max(np.abs(result-expected)):.2e}" if not ok else "")
except FileNotFoundError as e:
    print(f"  SKIP  (golden samples not found: {e})")

# ── 3. Roundtrip (encode -> decode hard decision) ──
print("\n=== PBCH Roundtrip ===")
np.random.seed(42)
for ncellid in [0, 17, 500, 1007]:
    for v in [0, 3, 7]:
        cw = np.random.randint(0, 2, size=864, dtype=np.int8)
        sym = pbch_encode(cw, ncellid, v)
        soft = pbch_decode(sym, ncellid, v)
        hard = (soft < 0).astype(np.int8)  # MATLAB convention: <0 => bit=1
        ok = np.array_equal(cw, hard)
        check(f"Roundtrip ncellid={ncellid} v={v}", ok,
              f"errors={np.sum(cw!=hard)}" if not ok else "")

print(f"\nTotal: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
