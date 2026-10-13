"""Validate nr_pdsch TX chain against MATLAB golden samples.

Verifies each stage: CRC → LDPC → rate match → modulation → layer mapping.
OFDM is separately validated (uses our own nr_ofdm.py which has its own tests).
"""
import json
import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.nr_pdsch import pdsch_transmit

SAMPLES_PATH = ROOT / "matlab_oracle" / "samples" / "nr_pdsch_samples.json"


def main():
    samples = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))

    ok = 0
    total = len(samples) * 5  # 5 stages to check per sample

    for i, s in enumerate(samples):
        name = s['case_name']
        bgn = s['bgn']
        zc = s['zc']
        mod = s['modulation']
        nfft = s['nfft']
        n_sc = s['n_sc']
        n_sym = s['n_symbols']

        tb = np.array(s['tb_bits'], dtype=np.uint8)
        exp_crc = np.array(s['crc_bits'], dtype=np.uint8)
        exp_ldpc = np.array(s['ldpc_codeword'], dtype=np.int8)
        exp_rm = np.array(s['rm_bits'], dtype=np.int8)
        exp_sym_r = np.array(s['symbols_real'], dtype=np.float64)
        exp_sym_i = np.array(s['symbols_imag'], dtype=np.float64)
        exp_sym = exp_sym_r + 1j * exp_sym_i
        exp_lyr_r = np.array(s['layered_real'], dtype=np.float64)
        exp_lyr_i = np.array(s['layered_imag'], dtype=np.float64)

        result = pdsch_transmit(tb, bgn, mod, nfft, n_sc, n_sym, rv=0)

        # Check 1: CRC
        got_crc = np.array(result['crc_bits'], dtype=np.uint8)
        crc_ok = np.array_equal(got_crc, exp_crc)
        if crc_ok: ok += 1
        print(f"  [{i+1}/{len(samples)}] {name} CRC: {'PASS' if crc_ok else 'FAIL'} "
              f"({np.sum(got_crc != exp_crc)} mismatches)")

        # Check 2: LDPC codeword
        got_ldpc = np.array(result['ldpc_codeword'], dtype=np.int8)
        ldpc_ok = np.array_equal(got_ldpc, exp_ldpc)
        if ldpc_ok: ok += 1
        print(f"  [{i+1}/{len(samples)}] {name} LDPC: {'PASS' if ldpc_ok else 'FAIL'} "
              f"({np.sum(got_ldpc != exp_ldpc)} mismatches)")

        # Check 3: Rate matching
        got_rm = np.array(result['rm_bits'], dtype=np.int8)
        rm_ok = np.array_equal(got_rm, exp_rm)
        if rm_ok: ok += 1
        print(f"  [{i+1}/{len(samples)}] {name} RM: {'PASS' if rm_ok else 'FAIL'} "
              f"({np.sum(got_rm != exp_rm)} mismatches)")

        # Check 4: Modulation symbols
        got_sym_r = np.array(result['symbols_real'], dtype=np.float64)
        got_sym_i = np.array(result['symbols_imag'], dtype=np.float64)
        got_sym = got_sym_r + 1j * got_sym_i
        sym_err = np.max(np.abs(got_sym - exp_sym))
        sym_ok = sym_err < 1e-9
        if sym_ok: ok += 1
        print(f"  [{i+1}/{len(samples)}] {name} MOD: {'PASS' if sym_ok else 'FAIL'} "
              f"(max err={sym_err:.2e})")

        # Check 5: Layer mapping
        got_lyr_r = np.array(result['layered_real'], dtype=np.float64)
        got_lyr_i = np.array(result['layered_imag'], dtype=np.float64)
        got_lyr = got_lyr_r + 1j * got_lyr_i
        exp_lyr_flat = exp_lyr_r.flatten() + 1j * exp_lyr_i.flatten()
        # MATLAB returns (N, nlayers) shape, our tool returns same shape
        # but flatten for comparison
        lyr_err = np.max(np.abs(got_lyr.flatten() - exp_lyr_flat))
        lyr_ok = lyr_err < 1e-9
        if lyr_ok: ok += 1
        print(f"  [{i+1}/{len(samples)}] {name} LAYER: {'PASS' if lyr_ok else 'FAIL'} "
              f"(max err={lyr_err:.2e})")

        print()

    print(f"{ok}/{total} checks passed ({len(samples)} samples × 5 stages)")
    return 0 if ok == total else 1


if __name__ == '__main__':
    sys.exit(main())
