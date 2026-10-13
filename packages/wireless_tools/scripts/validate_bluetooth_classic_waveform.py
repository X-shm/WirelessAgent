"""Compare BR waveform packet prefixes and slot lengths with R2026a."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from bluetooth_classic_waveform import generate
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'bluetooth_classic_waveform_samples.json').read_text(encoding='utf-8'))
for case in cases:
    props={'packet_type':case['packet_type'],'payload_length':case['payload_length']}
    waveform,_=generate(np.asarray(case['message'],dtype=np.uint8),props)
    assert waveform.size==case['samples'],(props,waveform.size,case['samples'])
    reference=np.asarray(case['first_real'])+1j*np.asarray(case['first_imag'])
    assert np.max(np.abs(waveform[:reference.size]-reference))<3e-5,(props,np.max(np.abs(waveform[:reference.size]-reference)))
print(f'PASS {len(cases)} Bluetooth classic BR waveform golden cases')
