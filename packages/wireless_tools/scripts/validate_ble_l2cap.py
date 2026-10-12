"""Compare BLE L2CAP frame encoding and decoding to MATLAB R2026a."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from ble_l2cap import encode, decode

NAME_MAP={
    'ChannelIdentifier':'channel_identifier','CommandType':'command_type',
    'Credits':'credits','CommandRejectReason':'command_reject_reason',
}
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_l2cap_samples.json').read_text(encoding='utf-8'))
for case in cases:
    cfg={NAME_MAP[k]:v for k,v in case['configuration'].items()}
    sdu=bytes.fromhex(case['sdu_hex']) if case['sdu_hex'] else None
    frame=encode(cfg,sdu)
    assert frame.hex().upper()==case['frame_hex'],(cfg,frame.hex(),case['frame_hex'])
    result=decode(frame)
    assert result['status']==case['decode_status'],(cfg,result)
    if sdu is not None:
        assert result['sdu_hex']==case['decoded_sdu_hex'],(cfg,result)
print(f'PASS {len(cases)} BLE L2CAP R2026a frame cases')
