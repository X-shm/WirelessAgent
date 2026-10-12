"""Compare BLE LL data and control PDU cases against R2026a."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from ble_ll_data import encode,decode
NAMES={'LLID':'llid','NESN':'nesn','SequenceNumber':'sequence_number',
       'MoreData':'more_data','ControlConfig':'control_config'}
CONTROL={'Opcode':'opcode','UsedChannels':'used_channels','Instant':'instant',
         'ErrorCode':'error_code','UnknownOpcode':'unknown_opcode',
         'VersionNumber':'version_number','CompanyIdentifier':'company_identifier',
         'SubVersionNumber':'sub_version_number'}
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_ll_data_samples.json').read_text(encoding='utf-8'))
for case in cases:
    cfg={NAMES[key]:value for key,value in case['configuration'].items()}
    if 'control_config' in cfg:
        cfg['control_config']={CONTROL[key]:value for key,value in cfg['control_config'].items()}
    payload=bytes.fromhex(case['payload_hex'])
    pdu=encode(cfg,payload)
    assert pdu.hex().upper()==case['pdu_hex'],(cfg,pdu.hex().upper(),case['pdu_hex'])
    assert decode(pdu)['status']==case['decode_status'],cfg
print(f'PASS {len(cases)} BLE LL data/control PDU golden cases')
