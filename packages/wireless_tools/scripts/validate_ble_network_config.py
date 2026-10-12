"""Compare eight Bluetooth LE/mesh/CS public configuration constructors."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from ble_network_config import configuration

def snake(name):
    return re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',
                  re.sub(r'([A-Z]+)([A-Z][a-z])',r'\1_\2',name)).lower()

def normalize(value):
    if value is None or value == []:
        return None
    return value

cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_network_config_samples.json').read_text(encoding='utf-8'))
for case in cases:
    props={snake(key):value for key,value in case['properties'].items()}
    cfg=configuration(case['kind'],props)
    # These MATLAB properties are derived/read-only or require a live node object.
    excluded={'AccessAddress','CISID','CISOffset'} if case['kind']=='bluetoothLECISConfig' else set()
    if case['kind']=='bluetoothLEPeriodicAdvConfig': excluded={'AccessAddress','ResponseAccessAddress'}
    if case['kind']=='bluetoothLEGAPConfig': excluded={'TargetNode'}
    oracle={snake(key):normalize(value) for key,value in case['configuration'].items() if key not in excluded}
    assert cfg.keys()==oracle.keys(),(case['kind'],set(cfg)^set(oracle))
    for key,value in cfg.items():
        expected=oracle[key]
        if key=='receive_bis_numbers' and isinstance(expected,int): expected=[expected]
        if isinstance(value,float):
            assert abs(value-expected)<1e-9,(case['kind'],key,value,expected)
        else:
            assert value==expected,(case['kind'],key,value,expected)
print(f'PASS {len(cases)} BLE network configuration golden cases')
