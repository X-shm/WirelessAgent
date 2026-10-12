"""Validate Bluetooth packet duration against R2026a golden samples."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'tools'))
from bluetooth_packet_duration import packet_duration
s=json.loads((ROOT/'matlab_oracle'/'samples'/'bluetooth_core_samples.json').read_text())
for case in s['durations']:
    d,n=packet_duration(case['mode'],case['packet_type'],case['payload_length'],case['cte_length'] or None)
    assert d==case['duration_us'] and n==case['num_bits'], case
print(f"PASS {len(s['durations'])} Bluetooth packet-duration golden samples")
