"""Compare 11 classic Bluetooth frequency-hop modes with R2026a."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from bluetooth_frequency_hop import next_hop
NAMES={'SequenceType':'sequence_type','DeviceAddress':'device_address',
       'UsedChannels':'used_channels','Counter':'counter','InterlaceOffset':'interlace_offset'}
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'bluetooth_frequency_hop_samples.json').read_text(encoding='utf-8'))
for case in cases:
    props={NAMES[key]:value for key,value in case['configuration'].items()}
    result=next_hop(props,case['clock'])
    assert result=={'channel_index':case['channel_index'],'x':case['x']},(props,result,case)
print(f'PASS {len(cases)} Bluetooth frequency-hop golden cases')
