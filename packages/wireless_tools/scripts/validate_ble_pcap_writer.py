"""Compare exact BLE PCAP 2.4 bytes with R2026a captures."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from ble_pcap_writer import build_pcap
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'ble_pcap_writer_samples.json').read_text(encoding='utf-8'))
for case in cases:
    packets=[dict(packet=item['packet'],timestamp_us=int(item['timestamp_us'])) for item in case['packets']]
    if case['phy_header_present']:
        for packet,item in zip(packets,case['packets']): packet['phy_header']=item['phy_header']
    capture=build_pcap(packets,byte_order=case['byte_order'],
                       phy_header_present=case['phy_header_present'])
    assert capture.hex().upper()==case['pcap_hex'],(case['byte_order'],capture.hex().upper(),case['pcap_hex'])
print(f'PASS {len(cases)} BLE PCAP golden cases')
