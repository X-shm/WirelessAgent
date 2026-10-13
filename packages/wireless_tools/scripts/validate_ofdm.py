"""Validate nr_ofdm.py against MATLAB golden samples."""
import json, sys, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from nr_ofdm import ofdm_modulate, ofdm_demodulate

data = json.loads((ROOT / "matlab_oracle" / "samples" / "ofdm_samples.json").read_text(encoding="utf-8"))

nrb = data['nrb']
nfft = data['nfft']
n_symbols = data['n_symbols']
n_sc = nrb * 12

grid_re = np.array(data['grid_real'], dtype=float)
grid_im = np.array(data['grid_imag'], dtype=float)
expected_wave_re = np.array(data['wave_real'], dtype=float)
expected_wave_im = np.array(data['wave_imag'], dtype=float)

grid = (grid_re + 1j * grid_im).T  # (n_symbols, n_sc) -> (n_sc, n_symbols)
expected_wave = expected_wave_re + 1j * expected_wave_im

# Test modulate
got_wave = ofdm_modulate(grid, nfft)
err_mod = np.max(np.abs(got_wave - expected_wave)) if len(got_wave) == len(expected_wave) else float('inf')
match_mod = err_mod < 1e-9

print(f"{'PASS' if match_mod else 'FAIL'} OFDM modulate: nrb={nrb} nfft={nfft} "
      f"n_sc={n_sc} n_symbols={n_symbols} wave_len={len(got_wave)} "
      f"exp_len={len(expected_wave)} max_err={err_mod:.2e}")

# Test demodulate roundtrip
got_grid = ofdm_demodulate(got_wave, n_sc, nfft, n_symbols)
err_demod = np.max(np.abs(got_grid - grid))
match_demod = err_demod < 1e-9

print(f"{'PASS' if match_demod else 'FAIL'} OFDM demodulate roundtrip: "
      f"max_err={err_demod:.2e} (MATLAB demod_err={data['demod_err']:.2e})")

ok = int(match_mod) + int(match_demod)
print(f"\n{ok}/2 passed")
