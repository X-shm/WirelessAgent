"""Compare RF-PHY CRC test branches to R2026a."""
import json,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from bluetooth_test_waveform import generate
from bluetooth_test_waveform_validate import validate
cases=json.loads((ROOT/'matlab_oracle'/'samples'/'bluetooth_test_waveform_validate_samples.json').read_text(encoding='utf-8'))
for case in cases:
    wave,_=generate({'mode':case['mode'],'payload_length':case['payload_length'],
                     'samples_per_symbol':case['samples_per_symbol'],'payload_type':1})
    result=validate(wave,test=case['test'],mode=case['mode'],
                    samples_per_symbol=case['samples_per_symbol'],payload_length=case['payload_length'])
    assert result['crc_error']==case['crc_error'],(case,result)
# Public RF-PHY measurement families use named JSON fields rather than
# MATLAB's positional output arguments.  Exercise their deterministic
# waveform shape and unit-bearing fields independently of MATLAB runtime.
mod_a,_=generate({'mode':'LE1M','payload_length':37,'payload_type':1})
mod_b,_=generate({'mode':'LE1M','payload_length':37,'payload_type':2})
modulation=validate(np.column_stack((mod_a,mod_b)),configuration={'test':'Modulation characteristics'})
assert modulation['test_id']=='RF-PHY/TRM/BV-09-C'
assert len(modulation['frequency_demodulated_hz'])==2304
assert len(modulation['average_frequency_deviation_hz'])==2
assert len(modulation['maximum_frequency_deviation_hz'])==280
assert np.allclose(modulation['average_frequency_deviation_hz'],[250000,295263.255100083],atol=1e-6)
assert abs(modulation['average_center_frequency_hz'][0][0]) < 1e-8
assert abs(modulation['maximum_frequency_deviation_hz'][-1]-295263.255100083) < 1e-6
carrier,_=generate({'mode':'LE1M','payload_length':37,'payload_type':1})
offset=validate(carrier,configuration={'test':'Carrier frequency offset and drift','payload_length':37})
assert offset['test_id']=='RF-PHY/TRM/BV-06-C'
assert len(offset['carrier_frequency_drift_hz'])==29
assert abs(offset['initial_frequency_offset_hz']) < 1e-8
assert np.allclose([offset['carrier_frequency_drift_hz'][0],offset['carrier_frequency_drift_hz'][-1]],
                   [47653.3925335144,47653.3925335147],atol=1e-6)
cte,_=generate({'mode':'LE1M','payload_length':37,'payload_type':1,'packet_type':'ConnectionCTE',
                'cte_length':20,'cte_type':[0,1]})
coherency=validate(cte,configuration={'test':'IQ samples coherency','packet_type':'ConnectionCTE',
                                       'cte_length':20,'cte_type':[0,1]})
dynamic_range=validate(cte,configuration={'test':'IQ samples dynamic range','packet_type':'ConnectionCTE',
                                           'cte_length':20,'cte_type':[0,1]})
assert coherency['measurement']=='iq_samples_coherency' and coherency['relative_phase_rad']
assert dynamic_range['measurement']=='iq_samples_dynamic_range'
assert dynamic_range['mean_amplitude_reference_antennas']
assert np.isclose(coherency['sum_relative_phase']['real'][0],3)
assert np.isclose(coherency['sum_reference_phase_deviation']['real'][0],8)
assert np.isclose(dynamic_range['mean_amplitude_reference_antennas'][0],0.909316854454121)
assert np.isclose(dynamic_range['mean_amplitude_nonreference_antennas'][0][0],0.909316854454121)
with tempfile.TemporaryDirectory() as folder:
    case=next(item for item in cases if item['mode']=='LE125K')
    path=str(Path(folder)/'test_waveform.npz')
    tx=subprocess.run([sys.executable,str(ROOT/'tools'/'bluetooth_test_waveform.py'),
        '--input',json.dumps({'properties':{'mode':case['mode'],
            'payload_length':case['payload_length'],'payload_type':1}}),
        '--output_file',path,'--inline_limit','1'],capture_output=True,text=True)
    assert tx.returncode==0,tx.stdout+tx.stderr
    rx=subprocess.run([sys.executable,str(ROOT/'tools'/'bluetooth_test_waveform_validate.py'),
        '--input',json.dumps({'waveform_file':path,'mode':case['mode'],'test':case['test'],
            'payload_length':case['payload_length']})],capture_output=True,text=True)
    assert rx.returncode==0,rx.stdout+rx.stderr
    assert json.loads(rx.stdout)['result']['crc_error']==case['crc_error']
    modulation_path=str(Path(folder)/'modulation.npz')
    np.savez(modulation_path,waveform=np.column_stack((mod_a,mod_b)))
    measurement=subprocess.run([sys.executable,str(ROOT/'tools'/'bluetooth_test_waveform_validate.py'),
        '--input',json.dumps({'waveform_file':modulation_path,
            'configuration':{'test':'Modulation characteristics'}})],capture_output=True,text=True)
    assert measurement.returncode==0,measurement.stdout+measurement.stderr
    assert json.loads(measurement.stdout)['result']['measurement']=='modulation_characteristics'
print(f'PASS {len(cases)} Bluetooth RF-PHY CRC golden cases plus frequency/IQ measurement checks')
