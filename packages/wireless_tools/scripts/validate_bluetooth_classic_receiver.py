"""Compare BR receiver outputs against R2026a roundtrips."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from bluetooth_classic_waveform import generate
from bluetooth_classic_receiver import receive
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'bluetooth_classic_receiver_samples.json').read_text(encoding='utf-8'))
for case in cases:
    wave,_=generate(np.asarray(case['message'],dtype=np.uint8),
                    {'packet_type':case['packet_type'],'payload_length':case['payload_length']})
    props={'is_id_packet':case['packet_type']=='ID',
           'has_extended_sco':case['packet_type'].startswith('EV'),
           'extended_sco_payload_length':case['payload_length']}
    result=receive(wave,props)
    assert result['bits']==case['bits'],(case['packet_type'],'bits')
    assert result['decoded_info']['packet_type']==case['decoded_packet_type'],case['packet_type']
    assert result['decoded_info']['payload_length']==case['decoded_payload_length'],case['packet_type']
    assert result['decoded_info']['lap']==case['lap'],case['packet_type']
    assert result['packet_valid']==case['packet_valid'],case['packet_type']
print(f'PASS {len(cases)} Bluetooth classic BR receiver golden cases')
