"""Validate lte_ofdm.py against MATLAB golden samples (1e-9 tolerance)."""
import json
import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lte_ofdm import lte_ofdm_info, modulate, demodulate, _to_complex

SAMPLES = ROOT / "matlab_oracle" / "samples"
info_table = json.loads((SAMPLES / "lte_ofdm_info_table.json").read_text(encoding="utf-8"))
samples = json.loads((SAMPLES / "lte_ofdm_samples.json").read_text(encoding="utf-8"))

ok_count = 0
total = 0


def report(name, ok):
    global ok_count, total
    total += 1
    ok_count += int(ok)
    print(f"{'PASS' if ok else 'FAIL'} {name}")


# 1) Full info formula check against compiled-lib table (210 entries)
for e in info_table:
    got = lte_ofdm_info(e['nrb'], e['cp'])
    ok = (got['nfft'] == e['nfft']
          and got['windowing'] == e['windowing']
          and abs(got['samplingrate'] - e['samplingrate']) < 1e-9
          and got['cplengths'] == e['cplengths'])
    if not ok:
        report(f"info nrb={e['nrb']} {e['cp']}", False)
        break
else:
    report(f"info formula vs full table ({len(info_table)} entries)", True)


def to_np(arr):
    return np.asarray(arr, dtype=np.complex128)


for x in samples:
    if x['mode'] == 'info':
        got = lte_ofdm_info(x['nrb'], x['cp'])
        ok = (got['nfft'] == x['nfft'] and got['windowing'] == x['windowing']
              and abs(got['samplingrate'] - x['samplingrate']) < 1e-9
              and got['cplengths'] == x['cplengths'])
        report(f"info nrb={x['nrb']} {x['cp']}", ok)

    elif x['mode'] == 'modulate':
        grid = to_np(x['grid_real']) + 1j * to_np(x['grid_imag'])
        win = None if not x['windowing'] else x['windowing']
        wf, info = modulate(x['nrb'], x['cp'], grid, win, None)
        exp = to_np(x['waveform_real']) + 1j * to_np(x['waveform_imag'])
        got = wf.reshape(-1)
        ok = np.allclose(got, exp.reshape(-1), atol=1e-9, rtol=1e-9)
        mx = np.max(np.abs(got - exp.reshape(-1))) if got.size else 0.0
        report(f"modulate nrb={x['nrb']} {x['cp']} win={win} sub={x['subframes']} (maxdiff={mx:.2e})", ok)

    else:  # demodulate
        wf = to_np(x['waveform_real']) + 1j * to_np(x['waveform_imag'])
        cpf = 0.55 if not x['cpfraction'] else x['cpfraction']
        rg = demodulate(x['nrb'], x['cp'], wf, cpf, None)
        exp = to_np(x['regrid_real']) + 1j * to_np(x['regrid_imag'])
        ok = np.allclose(rg.reshape(-1), exp.reshape(-1), atol=1e-9, rtol=1e-9)
        mx = np.max(np.abs(rg.reshape(-1) - exp.reshape(-1))) if rg.size else 0.0
        report(f"demodulate nrb={x['nrb']} {x['cp']} cpf={cpf} (maxdiff={mx:.2e})", ok)

print(f"\n{ok_count}/{total} passed")
sys.exit(0 if ok_count == total else 1)
