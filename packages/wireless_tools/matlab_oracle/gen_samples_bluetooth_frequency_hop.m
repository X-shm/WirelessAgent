function gen_samples_bluetooth_frequency_hop()
%GEN_SAMPLES_BLUETOOTH_FREQUENCY_HOP All 11 R2026a sequence types.
names={'Page scan','Inquiry scan','Page','Inquiry','Central page response', ...
    'Peripheral page response','Inquiry response','Connection basic', ...
    'Connection adaptive','Interlaced page scan','Interlaced inquiry scan'};
clocks={'2C','12C','44','2C','1123','2A','2C','12C','12C','2C','2C'};
cases=struct('configuration',{},'clock',{},'channel_index',{},'x',{});
for k=1:numel(names)
    props=struct('SequenceType',names{k},'DeviceAddress','2A96EF25');
    if strcmp(names{k},'Connection adaptive'), props.UsedChannels=22:78; end
    if contains(names{k},'response'), props.Counter=3; end
    if startsWith(names{k},'Interlaced'), props.InterlaceOffset=9; end
    fh=bluetoothFrequencyHop;
    fields=fieldnames(props);
    for n=1:numel(fields), fh.(fields{n})=props.(fields{n}); end
    [channel,x]=nextHop(fh,clocks{k});
    cases(k)=struct('configuration',props,'clock',clocks{k}, ...
        'channel_index',channel,'x',x);
end
fid=fopen(wt_sample_path('bluetooth_frequency_hop_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(cases)); fclose(fid);
end
