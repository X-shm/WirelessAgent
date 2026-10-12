"""Validate Bluetooth whitening against R2026a golden samples."""
import json, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'tools'))
from _bluetooth_algorithms import whiten
s=json.loads((ROOT/'matlab_oracle'/'samples'/'bluetooth_core_samples.json').read_text())['whitening']
y,_=whiten(np.asarray(s['bits'],dtype=np.uint8),0,list(map(int,s['initial_conditions'])))
assert y.tolist()==s['output_bits']
print('PASS Bluetooth whitening golden sample')
