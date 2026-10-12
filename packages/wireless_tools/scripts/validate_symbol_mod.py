"""Validate nr_modulation.py against MATLAB golden samples."""
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from nr_modulation import modulate

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "symbol_mod_samples.json").read_text(encoding="utf-8"))

ok_count = 0
for s in samples:
    mod = s['modulation']
    bits = np.array(s['bits'], dtype=int)
    expected = np.array(s['symbols_real']) + 1j * np.array(s['symbols_imag'])
    got = modulate(bits, mod)
    err = np.max(np.abs(got - expected))
    status = "PASS" if err < 1e-9 else "FAIL"
    if status == "PASS":
        ok_count += 1
    print(f"{status} {mod:8s} max_err={err:.2e}")

print(f"\n{ok_count}/{len(samples)} passed")
