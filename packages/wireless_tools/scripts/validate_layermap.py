"""Validate nr_layer_map.py against MATLAB golden samples."""
import json, sys, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from nr_layer_map import layer_map

samples = json.loads((ROOT / "matlab_oracle" / "samples" / "layermap_samples.json").read_text(encoding="utf-8"))

ok = 0
for s in samples:
    nl = s['nLayers']
    in_re = np.array(s['in_real'], dtype=float)
    in_im = np.array(s['in_imag'], dtype=float)
    symbols = in_re + 1j * in_im

    got = layer_map(symbols, nl)  # (out_rows, out_cols) = (n_symbols/nl, nl)

    if nl == 1:
        exp_re = np.array(s['out_real'], dtype=float).reshape(-1, 1)
        exp_im = np.array(s['out_imag'], dtype=float).reshape(-1, 1)
    else:
        exp_re = np.array(s['out_real'], dtype=float).T
        exp_im = np.array(s['out_imag'], dtype=float).T

    err = np.max(np.abs(got.real - exp_re)) + np.max(np.abs(got.imag - exp_im))
    match = err < 1e-9
    if match:
        ok += 1
    print(f"{'PASS' if match else 'FAIL'} nLayers={nl} n_symbols={s['n_symbols']} "
          f"shape={got.shape} max_err={err:.2e}")

print(f"\n{ok}/{len(samples)} passed")
