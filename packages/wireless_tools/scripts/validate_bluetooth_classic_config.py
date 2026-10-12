"""Validate R2026a-observed defaults for five classic config constructors."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from bluetooth_classic_config import create
assert create('connection',{})['poll_interval']==40
assert create('phy',{})['device_address']=='0123456789AB'
assert create('waveform',{})['packet_type']=='FHS'
assert create('test_waveform',{})['payload_length']==255
assert create('rf_phy_test',{})['test']=='Output power'
assert create('test_waveform',{'mode':'BR','packet_type':'DM3'})['fixed_payload_length']==121
print('PASS five Bluetooth classic configuration constructor defaults')
