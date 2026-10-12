"""Validate BLE CTE IQ sampling against R2026a."""
import json, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'tools'))
from ble_cte_iq_sample import iq_sample
s=json.loads((ROOT/'matlab_oracle'/'samples'/'bluetooth_core_samples.json').read_text())['cte_iq']
got=iq_sample(np.asarray(s['real'])+1j*np.asarray(s['imag']),mode=s['mode'],samples_per_symbol=s['samples_per_symbol'],slot_duration=s['slot_duration'],sample_offset=s['sample_offset'])
want=np.asarray(s['output_real'])+1j*np.asarray(s['output_imag'])
assert got.shape==want.shape and np.max(np.abs(got-want))<1e-10, np.max(np.abs(got-want))
print(f'PASS {got.size} BLE CTE IQ golden samples')
