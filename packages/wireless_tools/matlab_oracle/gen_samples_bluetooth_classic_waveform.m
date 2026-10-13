function gen_samples_bluetooth_classic_waveform()
%GEN_SAMPLES_BLUETOOTH_CLASSIC_WAVEFORM R2026a BR packet prefixes.
types={'ID','NULL','POLL','FHS','DM1','DH1','HV1','HV2','HV3','AUX1', ...
    'DV','EV3','EV4','EV5','DM3','DH3','DM5','DH5'};
cases=struct('packet_type',{},'payload_length',{},'message',{}, ...
    'samples',{},'first_real',{},'first_imag',{});
for k=1:numel(types)
    cfg=bluetoothWaveformConfig('PacketType',types{k},'Mode','BR', ...
        'DeviceAddress','0123456789AB');
    if any(strcmp(types{k},{'DM1','DH1','AUX1','DV','EV3','EV4', ...
            'EV5','DM3','DH3','DM5','DH5'})), cfg.PayloadLength=10; end
    len=getPayloadLength(cfg);
    data=mod((0:len*8-1)'+k,2);
    wave=bluetoothWaveformGenerator(data,cfg);
    n=min(512,numel(wave));
    cases(k)=struct('packet_type',types{k},'payload_length',cfg.PayloadLength, ...
        'message',data.','samples',numel(wave), ...
        'first_real',real(wave(1:n)).','first_imag',imag(wave(1:n)).');
end
fid=fopen(wt_sample_path('bluetooth_classic_waveform_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(cases)); fclose(fid);
end
