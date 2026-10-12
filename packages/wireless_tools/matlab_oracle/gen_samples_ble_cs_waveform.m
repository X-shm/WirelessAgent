function gen_samples_ble_cs_waveform()
%GEN_SAMPLES_BLE_CS_WAVEFORM R2026a conditioned waveform samples.
spec={struct('StepMode',0,'DeviceRole','Initiator'), ...
    struct('StepMode',0,'DeviceRole','Reflector','Mode','LE2M','ToneDuration',80), ...
    struct('StepMode',1,'SequenceLength',32), ...
    struct('StepMode',1,'DeviceRole','Reflector','Mode','LE2M', ...
           'SequenceType','Random Sequence','SequenceLength',64), ...
    struct('StepMode',2,'ToneDuration',20), ...
    struct('StepMode',3,'Mode','LE2M','ToneDuration',10,'SequenceLength',32), ...
    struct('StepMode',3,'DeviceRole','Reflector','SequenceLength',32)};
cases=struct('properties',{},'access_address',{},'optional_sequence',{}, ...
    'tone_extension_bit',{},'samples',{},'first_real',{},'first_imag',{}, ...
    'last_real',{},'last_imag',{});
for k=1:numel(spec)
    p=spec{k}; cfg=bleCSConfig;
    keys=fieldnames(p); for n=1:numel(keys), cfg.(keys{n})=p.(keys{n}); end
    [wave,address]=bleCSWaveform(cfg);
    factor=1; if ~strcmp(cfg.Mode,'LE1M'), factor=2; end
    syncLen=44; if factor==2, syncLen=52; end
    if any(cfg.StepMode==[1 3]), syncLen=syncLen+cfg.SequenceLength; end
    toneLen=cfg.ToneDuration*cfg.SamplesPerSymbol*factor;
    extension=0;
    if any(cfg.StepMode==[2 3])
        if cfg.StepMode==3 && strcmp(cfg.DeviceRole,'Initiator')
            extension=any(abs(wave(end-toneLen+1:end))>0.1);
        else
            extension=any(abs(wave(toneLen+1:2*toneLen))>0.1);
        end
    end
    if cfg.StepMode==2
        sequence=[];
    else
        syncStart=1;
        if cfg.StepMode==3 && strcmp(cfg.DeviceRole,'Reflector')
            syncStart=toneLen+10*cfg.SamplesPerSymbol*factor+1;
            if extension, syncStart=syncStart+toneLen; end
        end
        syncWave=wave(syncStart:syncStart+syncLen*cfg.SamplesPerSymbol-1);
        symbols=reshape(syncWave,cfg.SamplesPerSymbol,[]);
        bits=mean(angle(symbols(2:end,:).*conj(symbols(1:end-1,:))),1)>0;
        first=44; if factor==2, first=52; end
        sequence=double(bits(first+1:end));
    end
    n=min(256,numel(wave));
    cases(k)=struct('properties',p,'access_address',double(address.'), ...
        'optional_sequence',sequence,'tone_extension_bit',double(extension), ...
        'samples',numel(wave),'first_real',real(wave(1:n)).', ...
        'first_imag',imag(wave(1:n)).','last_real',real(wave(end-n+1:end)).', ...
        'last_imag',imag(wave(end-n+1:end)).');
end
fid=fopen(wt_sample_path('ble_cs_waveform_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(cases)); fclose(fid);
end
