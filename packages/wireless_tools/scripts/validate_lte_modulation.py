"""Validate lte_modulation.py against MATLAB golden samples."""
import json
import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lte_modulation import modulate

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "lte_modulation_samples.json").read_text(encoding="utf-8"))

ok_count = 0
total = 0
for s in samples:
    mod = s['modulation']
    bits = np.array(s['bits'], dtype=int)
    expected = np.array(s['symbols_real']) + 1j * np.array(s['symbols_imag'])
    got = modulate(bits, mod)
    err = np.max(np.abs(got - expected))
    status = "PASS" if err < 1e-9 else "FAIL"
    total += 1
    if status == "PASS":
        ok_count += 1
    print(f"{status} {mod:8s} n_sym={len(got):3d} max_err={err:.2e}")

print(f"\n{ok_count}/{total} passed")
sys.exit(0 if ok_count == total else 1)
