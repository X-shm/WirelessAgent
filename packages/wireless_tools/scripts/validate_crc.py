"""Validate nr_crc.py against MATLAB golden samples."""
import json, sys, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from nr_crc import _crc_encode_bits

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "crc_samples.json").read_text(encoding="utf-8"))

ok = 0
for s in samples:
    poly = s['poly']
    inp = np.array(s['input_bits'], dtype=np.uint8)
    expected = np.array(s['output_bits'], dtype=np.uint8)
    got = _crc_encode_bits(inp, poly)
    match = np.array_equal(got, expected)
    if match: ok += 1
    print(f"{'PASS' if match else 'FAIL'} {poly:4s} input={s['n_input']} crc={s['n_crc']} total={s['n_output']}")

print(f"\n{ok}/{len(samples)} passed")
