"""Compare all legacy BLE LL advertising PDUs with the R2026a oracle."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from ble_ll_advertising import encode,decode

names={'PDUType':'pdu_type','TargetAddress':'target_address',
       'AdvertisingData':'advertising_data','ScannerAddress':'scanner_address',
       'ScanResponseData':'scan_response_data','ConnectionInterval':'connection_interval',
       'UsedChannels':'used_channels','AccessAddress':'access_address',
       'SleepClockAccuracy':'sleep_clock_accuracy','ChannelSelection':'channel_selection'}
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_ll_advertising_samples.json').read_text(encoding='utf-8'))
for case in cases:
    cfg={names[key]:value for key,value in case['configuration'].items()}
    pdu=encode(cfg)
    assert pdu.hex().upper()==case['pdu_hex'],(cfg,pdu.hex().upper(),case['pdu_hex'])
    result=decode(pdu)
    assert result['status']==case['decode_status'],(cfg,result['status'],case['decode_status'])
print(f'PASS {len(cases)} BLE LL advertising PDU golden cases')
