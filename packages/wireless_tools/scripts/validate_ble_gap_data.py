"""Compare BLE GAP AD encoding/decoding with R2026a golden samples."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from ble_gap_data import encode,decode
NAMES={'AdvertisingDataTypes':'advertising_data_types','LEDiscoverability':'le_discoverability',
       'TxPowerLevel':'tx_power_level','AdvertisingInterval':'advertising_interval',
       'LocalNameShortening':'local_name_shortening','LocalName':'local_name',
       'Identifiers':'identifiers','IdentifierType':'identifier_type',
       'ConnectionIntervalRange':'connection_interval_range','BREDR':'bredr','LE':'le'}
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_gap_data_samples.json').read_text(encoding='utf-8'))
for case in cases:
    cfg={NAMES[k]:v for k,v in case['configuration'].items()}
    block=encode(cfg)
    assert block.hex().upper()==case['data_block_hex'],(cfg,block.hex(),case['data_block_hex'])
    assert decode(block)['status']==case['decode_status'],cfg
print(f'PASS {len(cases)} BLE GAP AD golden cases')
