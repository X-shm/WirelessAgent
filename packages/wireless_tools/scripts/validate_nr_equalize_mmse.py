"""validate_nr_equalize_mmse.py — Validate nr_equalize_mmse against MATLAB golden samples."""
from __future__ import annotations
import json
import os
import sys
import numpy as np

TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools')
SAMPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'matlab_oracle', 'samples')
sys.path.insert(0, TOOLS)

from nr_equalize_mmse import mmse_equalize

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


def _reshape_matlab(arr, shape):
    """Reshape a flat/partially-flat array using column-major (MATLAB/Fortran) order."""
    flat = np.asarray(arr, dtype=np.float64).flatten(order='F')
    return flat.reshape(shape, order='F')


print("\n=== MMSE Equalize ===")
try:
    d = load_json('nr_equalize_mmse.json')
    for case_name, case in d.items():
        nRe = case['n_re']
        nRx = case['n_rx']
        nLayers = case['n_layers']
        nVar = case['nvar']

        # rx_sym: NRE x R — use metadata to reshape (MATLAB column-major)
        rx_real_flat = np.array(case['rx_real'], dtype=np.float64).flatten(order='F')
        rx_imag_flat = np.array(case['rx_imag'], dtype=np.float64).flatten(order='F')
        rx_real = rx_real_flat.reshape((nRe, nRx), order='F')
        rx_imag = rx_imag_flat.reshape((nRe, nRx), order='F')
        rx_sym = rx_real + 1j * rx_imag

        # hest: NRE x R x P — MATLAB jsonencode serializes in column-major order
        hest_real_flat = np.array(case['hest_real'], dtype=np.float64).flatten(order='F')
        hest_imag_flat = np.array(case['hest_imag'], dtype=np.float64).flatten(order='F')
        # MATLAB: Hest is NRE x R x P, column-major -> flatten order F
        hest_real = hest_real_flat.reshape((nRe, nRx, nLayers), order='F')
        hest_imag = hest_imag_flat.reshape((nRe, nRx, nLayers), order='F')
        hest = hest_real + 1j * hest_imag

        # Expected outputs: out is NRE x P
        out_real_flat = np.array(case['out_real'], dtype=np.float64).flatten(order='F')
        out_imag_flat = np.array(case['out_imag'], dtype=np.float64).flatten(order='F')
        out_real = out_real_flat.reshape((nRe, nLayers), order='F')
        out_imag = out_imag_flat.reshape((nRe, nLayers), order='F')
        expected_out = out_real + 1j * out_imag

        # CSI: NRE x P
        csi_flat = np.array(case['csi'], dtype=np.float64).flatten(order='F')
        expected_csi = csi_flat.reshape((nRe, nLayers), order='F')

        result_out, result_csi = mmse_equalize(rx_sym, hest, nVar)

        # Compare output symbols
        ok_sym = np.allclose(result_out, expected_out, atol=1e-10)
        # Compare CSI (may have slightly different numerical precision)
        ok_csi = np.allclose(result_csi, expected_csi, atol=1e-6, rtol=1e-4)

        ok = ok_sym and ok_csi
        detail = ""
        if not ok_sym:
            detail += f"out_err={np.max(np.abs(result_out-expected_out)):.2e} "
        if not ok_csi:
            detail += f"csi_err={np.max(np.abs(result_csi-expected_csi)):.2e}"
        check(f"MMSE {case_name}", ok, detail.strip())
except FileNotFoundError as e:
    print(f"  SKIP  (golden samples not found: {e})")

print(f"\nTotal: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
