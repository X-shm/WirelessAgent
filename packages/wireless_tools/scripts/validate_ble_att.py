"""Compare every ATT opcode's bytes and decode status to R2026a."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from ble_att import encode,decode
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_att_samples.json').read_text(encoding='utf-8'))
value_names={'Read response','Read blob response','Write request','Write command',
             'Handle value notification','Handle value indication','Prepare write request',
             'Prepare write response','Read by type response','Read by group type response',
             'Find by type value request'}
for case in cases:
    cfg={'opcode':case['opcode']}
    if case['opcode'] in value_names:cfg['attribute_value']='1234'
    actual=encode(cfg)
    assert actual.hex().upper()==case['pdu_hex'],(case['opcode'],actual.hex(),case['pdu_hex'])
    result=decode(actual)
    assert result['status']==case['decode_status'],(case['opcode'],result,case['decode_status'])
print(f"PASS {len(cases)} BLE ATT opcode golden cases")
