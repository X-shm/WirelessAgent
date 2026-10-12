function gen_samples_ble_ideal_receiver()
%GEN_SAMPLES_BLE_IDEAL_RECEIVER R2026a ideal LE1M/LE2M roundtrips.
cases=struct('mode',{},'channel_index',{},'samples_per_symbol',{}, ...
    'message',{},'bits',{},'access_address',{});
for k=1:4
    mode={'LE1M','LE1M','LE2M','LE2M'};
    channel=[37 12 38 4]; sps=[8 4 8 4];
    msg=mod((0:(31+8*k))'+k,2);
    wave=bleWaveformGenerator(msg,'Mode',mode{k}, ...
        'ChannelIndex',channel(k),'SamplesPerSymbol',sps(k));
    [bits,address]=bleIdealReceiver(wave,'Mode',mode{k}, ...
        'ChannelIndex',channel(k),'SamplesPerSymbol',sps(k));
    cases(k)=struct('mode',mode{k},'channel_index',channel(k), ...
        'samples_per_symbol',sps(k),'message',msg.', ...
        'bits',bits.','access_address',address.');
end
fid=fopen(wt_sample_path('ble_ideal_receiver_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(cases)); fclose(fid);
end
