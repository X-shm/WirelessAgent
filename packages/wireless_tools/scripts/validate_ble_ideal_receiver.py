"""Check pure-Python BLE ideal receiver against R2026a bit outputs."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from ble_waveform import generate
from ble_ideal_receiver import receive
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_ideal_receiver_samples.json').read_text(encoding='utf-8'))
for case in cases:
    wave,_=generate(np.asarray(case['message'],dtype=np.uint8),mode=case['mode'],
                    channel_index=case['channel_index'],samples_per_symbol=case['samples_per_symbol'])
    bits,address=receive(wave,mode=case['mode'],channel_index=case['channel_index'],
                         samples_per_symbol=case['samples_per_symbol'])
    assert bits.tolist()==case['bits'],case
    assert address.tolist()==case['access_address'],case
print(f'PASS {len(cases)} BLE ideal receiver golden cases')
