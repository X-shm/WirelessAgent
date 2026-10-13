"""Compare BR/LE test waveform lengths and samples with R2026a."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from bluetooth_test_waveform import generate
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'bluetooth_test_waveform_samples.json').read_text(encoding='utf-8'))
for case in cases:
    names={'Mode':'mode','PayloadLength':'payload_length',
           'PayloadType':'payload_type','PacketType':'packet_type',
           'CTELength':'cte_length','CTEType':'cte_type'}
    props={names[key]:value for key,value in case['properties'].items()}
    wave,_=generate(props)
    assert wave.size==case['samples'],(props,wave.size,case['samples'])
    reference=np.asarray(case['waveform_real'])+1j*np.asarray(case['waveform_imag'])
    assert np.max(np.abs(wave[:reference.size]-reference))<2e-5,props
print(f'PASS {len(cases)} Bluetooth BR/LE test waveform golden cases')
