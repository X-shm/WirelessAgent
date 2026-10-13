"""Create serializable configurations for five Bluetooth BR/EDR APIs."""
from __future__ import annotations
from copy import deepcopy
from _bluetooth_common import InputError, run_cli

DEFAULTS={
'connection':{'central_to_peripheral_acl_packet_type':'DH1','peripheral_to_central_acl_packet_type':'DH1','sco_packet_type':'None','hopping_sequence_type':'Connection adaptive','used_channels':list(range(79)),'poll_interval':40,'instant_offset':240,'transmitter_power':20,'supervision_timeout':32000},
'phy':{'mode':'BR','device_address':'0123456789AB','modulation_index':.32,'samples_per_symbol':8,'whiten_status':'On','whiten_initialization':[1]*7,'has_extended_sco':False,'extended_sco_payload_length':18,'is_id_packet':False},
'waveform':{'packet_type':'FHS','payload_length':18,'logical_transport_address':[0,0,1],'header_control_bits':[1,1,1],'llid':[1,1],'flow_indicator':True,'output_data_type':None,'mode':'BR','device_address':'0123456789AB','modulation_index':.32,'samples_per_symbol':8,'whiten_status':'On','whiten_initialization':[1]*7,'has_extended_sco':False,'extended_sco_payload_length':18,'is_id_packet':False},
'test_waveform':{'mode':'LE1M','payload_length':255,'whiten_status':'Off','whiten_initialization':[1]*7,'modulation_index':.5,'pulse_length':1,'packet_type':'Disabled','payload_type':0,'samples_per_symbol':8,'cte_length':2,'cte_type':[0,0]},
'rf_phy_test':{'test':'Output power','mode':'LE1M','payload_length':37,'packet_type':'Disabled','modulation_index':.5,'pulse_length':1,'array_size':4,'element_spacing':.5,'center_frequency':'Low','num_test_frequencies':10,'resolution_bw':3e6,'output_power':0,'initial_frequency_offset':0,'carrier_drift':0,'wanted_signal_level':-67,'interferer1_signal_level':[-88,-82,-50,-40],'interferer2_signal_level':-50,'blocking_signal_level':[-30,-35,-35,-30],'blocking_signal_freq_resolution':[1e7,3e6,3e6,25e6],'num_packets':1,'per_upper_limit':30.8,'payload_type':0,'samples_per_symbol':8,'cte_length':2,'cte_type':[0,0]}}
MODES={'BR','EDR2M','EDR3M','LE1M','LE2M','LE125K','LE500K'}
RF_TESTS={'Output power','Inband emissions','Modulation characteristics','Carrier frequency offset and drift','Tx power stability','C/I','Blocking','Intermodulation','Receiver sensitivity','Maximum input signal level','PER report integrity','IQ samples coherency','IQ samples dynamic range'}

def create(kind,properties):
    if kind not in DEFAULTS: raise InputError('kind must be connection, phy, waveform, test_waveform, or rf_phy_test')
    if not isinstance(properties,dict): raise InputError('properties must be a JSON object')
    unknown=set(properties)-set(DEFAULTS[kind])
    if unknown: raise InputError('unsupported properties: '+', '.join(sorted(unknown)))
    cfg=deepcopy(DEFAULTS[kind]); cfg.update(properties)
    if 'mode' in cfg and cfg['mode'] not in MODES: raise InputError('mode is unsupported')
    if 'device_address' in cfg and (not isinstance(cfg['device_address'],str) or len(cfg['device_address'])!=12 or any(c not in '0123456789abcdefABCDEF' for c in cfg['device_address'])): raise InputError('device_address must be 12 hexadecimal digits')
    if 'samples_per_symbol' in cfg and (not isinstance(cfg['samples_per_symbol'],int) or cfg['samples_per_symbol']<1): raise InputError('samples_per_symbol must be a positive integer')
    if 'whiten_status' in cfg and cfg['whiten_status'] not in {'On','Off'}: raise InputError('whiten_status must be On or Off')
    if 'whiten_initialization' in cfg and (not isinstance(cfg['whiten_initialization'],list) or len(cfg['whiten_initialization'])!=7 or any(x not in (0,1,False,True) for x in cfg['whiten_initialization'])): raise InputError('whiten_initialization must contain seven binary values')
    if kind=='connection':
        channels=cfg['used_channels']
        if not isinstance(channels,list) or len(set(channels))<20 or any(not isinstance(x,int) or x<0 or x>78 for x in channels): raise InputError('used_channels requires at least 20 indices in 0..78')
        cfg['used_channels']=sorted(set(channels))
        if cfg['poll_interval']%2 or not 6<=cfg['poll_interval']<=4096 or cfg['instant_offset']%2 or not 96<=cfg['instant_offset']<=69120000: raise InputError('poll_interval and instant_offset must be valid even slot counts')
    if kind in {'test_waveform','rf_phy_test'}:
        # MATLAB stores 0.5 as the LE default and exposes 0.32 when a
        # test-waveform configuration is switched to a classic PHY.
        if kind=='test_waveform' and cfg['mode'] in {'BR','EDR2M','EDR3M'} and cfg['modulation_index']==.5:
            cfg['modulation_index']=.32
        if not isinstance(cfg['payload_length'],int) or not 0<=cfg['payload_length']<=255: raise InputError('payload_length must be an integer in 0..255')
        bounds=(.45,.55) if cfg['mode'].startswith('LE') else (.28,.35)
        if not bounds[0]<=cfg['modulation_index']<=bounds[1]: raise InputError('modulation_index is invalid for mode')
    if kind=='rf_phy_test':
        if cfg['mode'] not in {'LE1M','LE2M','LE125K','LE500K'}: raise InputError('rf_phy_test mode must be a Bluetooth LE PHY')
        if cfg['test'] not in RF_TESTS: raise InputError('unsupported rf_phy_test test')
        if not isinstance(cfg['payload_length'],int) or not 31<=cfg['payload_length']<=255: raise InputError('rf_phy_test payload_length must be an integer in 31..255')
        if cfg['packet_type'] not in {'Disabled','ConnectionCTE'}: raise InputError('rf_phy_test packet_type must be Disabled or ConnectionCTE')
        if not isinstance(cfg['pulse_length'],int) or not 1<=cfg['pulse_length']<=4: raise InputError('rf_phy_test pulse_length must be an integer in 1..4')
        if cfg['center_frequency'] not in {'Low','Mid','High'}: raise InputError('rf_phy_test center_frequency must be Low, Mid, or High')
        if not isinstance(cfg['cte_length'],int) or not 2<=cfg['cte_length']<=20: raise InputError('rf_phy_test cte_length must be an integer in 2..20')
        if not isinstance(cfg['cte_type'],list) or len(cfg['cte_type'])!=2 or any(bit not in (0,1,False,True) for bit in cfg['cte_type']) or cfg['cte_type']==[1,1]: raise InputError('rf_phy_test cte_type must be a two-bit CTE type 0..2')
        if not isinstance(cfg['array_size'],int) or cfg['array_size']<2: raise InputError('rf_phy_test array_size must be an integer >= 2')
        if not isinstance(cfg['element_spacing'],(int,float)) or isinstance(cfg['element_spacing'],bool) or cfg['element_spacing']<=0: raise InputError('rf_phy_test element_spacing must be positive')
        if not isinstance(cfg['num_packets'],int) or cfg['num_packets']<1: raise InputError('rf_phy_test num_packets must be a positive integer')
    if kind=='test_waveform':
        classic_types={'BR':{'DH1','DH3','DH5','DM1','DM3','DM5'},
                       'EDR2M':{'2-DH1','2-DH3','2-DH5','2-EV3','2-EV5'},
                       'EDR3M':{'3-DH1','3-DH3','3-DH5','3-EV3','3-EV5'}}
        if cfg['mode'] in classic_types:
            if cfg['packet_type']=='Disabled':
                cfg['packet_type']={'BR':'DH1','EDR2M':'2-DH1','EDR3M':'3-DH1'}[cfg['mode']]
            if cfg['packet_type'] not in classic_types[cfg['mode']]:
                raise InputError('packet_type is invalid for classic test mode')
        cfg['fixed_payload_length']={'DH1':27,'DH3':183,'DH5':339,'DM1':17,'DM3':121,'DM5':224,
            '2-DH1':54,'2-DH3':367,'2-DH5':679,'2-EV3':60,'2-EV5':360,
            '3-DH1':83,'3-DH3':552,'3-DH5':1021,'3-EV3':90,'3-EV5':540}.get(cfg['packet_type'],27)
    return cfg
def _handler(_args,request): return {'result':{'configuration':create(request.get('kind'),request.get('properties',{}))}}
if __name__=='__main__': run_cli('bluetooth_classic_config',_handler,description=__doc__)
