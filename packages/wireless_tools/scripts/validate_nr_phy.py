"""validate_nr_phy.py — Validate nr_prbs/pss/sss/tbs/mcs against MATLAB golden samples."""
from __future__ import annotations
import json
import os
import sys
import numpy as np

# Add tools to path
TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools')
SAMPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'matlab_oracle', 'samples')
sys.path.insert(0, TOOLS)

from nr_prbs import prbs
from nr_pss import pss, pss_indices
from nr_sss import sss
from nr_tbs import tbs as calc_tbs
from nr_mcs_tables import get_mcs_table

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


# ── 1. PRBS ──
print("\n=== PRBS ===")
d = load_json('nr_prbs.json')
for case_name, case in d.items():
    cinit = case['cinit']
    n = case['n']
    expected = np.array(case['seq'], dtype=np.int8)
    if 'offset' in case:
        result = prbs(cinit, [case['offset'], n])
    else:
        result = prbs(cinit, n)
    ok = np.array_equal(result.astype(int), expected.astype(int))
    check(f"PRBS {case_name}", ok, f"first mismatch at {np.where(result != expected)[0][:3]}" if not ok else "")

# ── 2. PSS ──
print("\n=== PSS ===")
d = load_json('nr_pss.json')
for case_name, case in d.items():
    if case_name.startswith('ncellid'):
        nc = case['ncellid']
        expected = np.array(case['sym'], dtype=float)
        result = pss(nc)
        ok = np.allclose(result, expected, atol=1e-10)
        check(f"PSS {case_name}", ok, f"max_err={np.max(np.abs(result-expected)):.2e}" if not ok else "")
    elif 'indices' in case_name:
        expected = np.array(case['indices'], dtype=int)
        base = '0based' if '0based' in case_name else '1based'
        result = pss_indices(base)
        ok = np.array_equal(result.astype(int), expected.astype(int))
        check(f"PSS {case_name}", ok, "" if ok else f"expected={expected[:5]} got={result.astype(int)[:5]}")

# ── 3. SSS ──
print("\n=== SSS ===")
d = load_json('nr_sss.json')
for case_name, case in d.items():
    if case_name.startswith('ncellid'):
        nc = case['ncellid']
        expected = np.array(case['sym'], dtype=float)
        result = sss(nc)
        ok = np.allclose(result, expected, atol=1e-10)
        check(f"SSS {case_name}", ok, f"max_err={np.max(np.abs(result-expected)):.2e}" if not ok else "")
    elif 'indices' in case_name:
        from nr_sss import sss_indices
        expected = np.array(case['indices'], dtype=int)
        result = sss_indices('1based')
        ok = np.array_equal(result.astype(int), expected.astype(int))
        check(f"SSS {case_name}", ok, "")

# ── 4. TBS ──
print("\n=== TBS ===")
d = load_json('nr_tbs.json')
for case_name, case in d.items():
    expected = case['tbs']
    result = calc_tbs(case['modulation'], case['nlayers'], case['nPRB'],
                      case['NREPerPRB'], case['tcr'], case['xOh'], case['tbScaling'])
    ok = result == expected
    check(f"TBS {case_name} (expect {expected})", ok, f"got {result}" if not ok else "")

# ── 5. MCS Tables ──
print("\n=== MCS Tables ===")
d = load_json('nr_mcs_tables.json')
# Our table names map differently
table_map = {
    'QAM64Table': 'QAM64Table',
    'QAM256Table': 'QAM256Table',
    'QAM64LowSETable': 'QAM64LowSETable',
    'QAM1024Table': 'QAM1024Table',
}
for matlab_name, our_name in table_map.items():
    if matlab_name not in d:
        print(f"  SKIP  {matlab_name} (not in samples)")
        continue
    case = d[matlab_name]
    # MATLAB struct array serializes as list of N identical dicts — take first
    if isinstance(case, list):
        case = case[0]

    matlab_qm = case.get('qm', [])
    matlab_tcr = case.get('target_code_rate', [])
    matlab_mcs_idx = case.get('mcs_index', [])

    if not matlab_mcs_idx:
        print(f"  SKIP  {matlab_name} (no data)")
        continue

    our_table = get_mcs_table(our_name)

    # Compare qm values
    qm_ok = True
    tcr_ok = True
    for i, mcs_idx in enumerate(matlab_mcs_idx):
        if mcs_idx is None:
            continue
        # Find matching entry in our table
        our_entry = None
        for row in our_table:
            if row[0] == mcs_idx:
                our_entry = row
                break
        if our_entry is None:
            qm_ok = False
            tcr_ok = False
            break
        if our_entry[2] != matlab_qm[i]:
            qm_ok = False
        # Target code rate: both stored as float now
        our_tcr = our_entry[3]
        matlab_tcr_val = matlab_tcr[i]
        if matlab_tcr_val is not None and our_tcr is not None and abs(our_tcr - matlab_tcr_val) > 1e-9:
            tcr_ok = False
        elif (matlab_tcr_val is None) != (our_tcr is None):
            tcr_ok = False

    check(f"MCS {matlab_name} qm", qm_ok)
    check(f"MCS {matlab_name} tcr", tcr_ok)

# ── Summary ──
print(f"\n{'='*50}")
print(f"Total: {passed} passed, {failed} failed")
if failures:
    print(f"Failed: {failures}")
else:
    print("ALL PASSED!")
