"""Compare conditioned BLE CS step-mode waveforms with R2026a."""
import json,re,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from ble_cs_waveform import generate
def snake(name):
    return re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',name).lower()
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_cs_waveform_samples.json').read_text(encoding='utf-8'))
for case in cases:
    props={snake(k):v for k,v in case['properties'].items()}
    wave,info=generate(props,access_address=case['access_address'] or None,
                       optional_sequence=case['optional_sequence'] or None,
                       tone_extension_bit=case['tone_extension_bit'] if props['step_mode'] in (2,3) else None)
    assert wave.size==case['samples'],(props,wave.size,case['samples'])
    for part in ('first','last'):
        ref=np.asarray(case[part+'_real'])+1j*np.asarray(case[part+'_imag'])
        observed=wave[:ref.size] if part=='first' else wave[-ref.size:]
        assert np.max(np.abs(observed-ref))<3e-5,(props,part,np.max(np.abs(observed-ref)))
print(f'PASS {len(cases)} BLE CS waveform golden cases')
