function gen_samples_bluetooth_core()
%GEN_SAMPLES_BLUETOOTH_CORE Deterministic R2026a samples for initial Bluetooth CLIs.
durations = struct('mode',{},'packet_type',{},'payload_length',{},'cte_length',{},'duration_us',{},'num_bits',{});
cases = {{'BR','DH1',18,[]};{'EDR3M','3-DH5',300,[]};{'LE1M','Disabled',4,[]};{'LE2M','ConnectionCTE',20,5};{'LE125K','Disabled',80,[]}};
for k=1:numel(cases)
    c=cases{k};
    if isempty(c{4}), [d,n]=bluetoothPacketDuration(c{1},c{2},c{3}); else, [d,n]=bluetoothPacketDuration(c{1},c{2},c{3},c{4}); end
    durations(k)=struct('mode',c{1},'packet_type',c{2},'payload_length',c{3},'cte_length',c{4},'duration_us',d,'num_bits',n);
end
x=[1;0;1;1;0;0;1;0;1;1;0;1]; init=[1;int2bit(37,6)]; w=bluetoothWhiten('InitialConditionsSource','Input port');
whitening=struct('bits',x','initial_conditions',init','output_bits',w(x,init)');
wf=struct('message',{},'mode',{},'channel_index',{},'samples_per_symbol',{},'pulse_length',{},'real',{},'imag',{});
spec={{[1;0;1;1],'LE1M',37,8,1};{[1;1;0;0;1;0;1],'LE2M',2,4,3}};
for k=1:numel(spec)
    c=spec{k}; y=bleWaveformGenerator(c{1},'Mode',c{2},'ChannelIndex',c{3},'SamplesPerSymbol',c{4},'PulseLength',c{5});
    wf(k)=struct('message',c{1}','mode',c{2},'channel_index',c{3},'samples_per_symbol',c{4},'pulse_length',c{5},'real',real(y)','imag',imag(y)');
end
positions=struct('locator_positions',{},'method',{},'distance',{},'direction',{},'position',{});
positionSpec = {
    {[-18 -40;-10 70], 'angulation', [], [29.0546 -60.2551]}; ...
    {[-5 -15 -30 -12.5;8.6603 -15 -17.3205 -21.6506;-17.3205 21.2132 20 43.3013], 'lateration', [13.2964 33.4221 40 55.0728], []}; ...
    {[2 -3;1 4], 'distance-angle', [sqrt(5) 5], [-153.434948822922 -53.130102354156]}; ...
    {[-10 10 10;-10 -10 10;0 0 0], 'angulation', [], [45 135 -135;35.2643896827547 35.2643896827547 35.2643896827547]}};
for k=1:numel(positionSpec)
    c=positionSpec{k};
    if strcmp(c{2},'angulation')
        p=blePositionEstimate(c{1},c{2},c{4});
    elseif strcmp(c{2},'lateration')
        p=blePositionEstimate(c{1},c{2},c{3});
    else
        p=blePositionEstimate(c{1},c{2},c{3},c{4});
    end
    positions(k)=struct('locator_positions',c{1},'method',c{2},'distance',c{3},'direction',c{4},'position',p');
end
channelSelection=struct('algorithm',{},'hop_increment',{},'access_address',{},'used_channels',{},'subevent_channel_selection',{},'isochronous_event_counter',{},'subevent_numbers',{},'channel_indices',{});
channelSpec = {
    {1,7,'8E89BED6',[0 2 24 6 10 14 26 30 34 36],false,[],[],5}; ...
    {2,5,'8E89BED6',[9 10 21 22 23 33 34 35 36],false,[],[],5}; ...
    {2,5,'8E89BED6',[9 10 21 22 23 33 34 35 36],true,0,[1 2 3],[]}};
for k=1:numel(channelSpec)
    c=channelSpec{k}; selector=bleChannelSelection;
    selector.Algorithm=c{1}; selector.HopIncrement=c{2}; selector.AccessAddress=c{3}; selector.UsedChannels=c{4}; selector.SubeventChannelSelection=c{5};
    if c{5}
        selector.IsochronousEventCounter=c{6}; indices=zeros(1,numel(c{7}));
        for n=1:numel(c{7}), selector.SubeventNumber=c{7}(n); indices(n)=selector(); end
    else
        indices=zeros(1,c{8}); for n=1:c{8}, indices(n)=selector(); end
    end
    channelSelection(k)=struct('algorithm',c{1},'hop_increment',c{2},'access_address',c{3},'used_channels',c{4},'subevent_channel_selection',c{5},'isochronous_event_counter',c{6},'subevent_numbers',c{7},'channel_indices',indices);
end
pathLoss=struct('distance',{},'environment',{},'transmitter_antenna_gain',{},'receiver_antenna_gain',{},'transmitter_cable_loss',{},'receiver_cable_loss',{},'transmitter_antenna_height',{},'receiver_antenna_height',{},'path_loss_exponent',{},'standard_deviation',{},'path_loss_db',{});
pathLossSpec = {
    {[1 5 20], 'Industrial', [5 4 3], 2, 1, 0.5, 1, 1, 2, 0}; ...
    {[1 15 50], 'Outdoor', 1, -2, 0.5, 0.25, 2, 3, 2.2, 0}};
for k=1:numel(pathLossSpec)
    c=pathLossSpec{k}; cfg=bluetoothPathLossConfig;
    cfg.Environment=c{2}; cfg.TransmitterAntennaGain=c{3}; cfg.ReceiverAntennaGain=c{4}; cfg.TransmitterCableLoss=c{5}; cfg.ReceiverCableLoss=c{6}; cfg.TransmitterAntennaHeight=c{7}; cfg.ReceiverAntennaHeight=c{8}; cfg.PathLossExponent=c{9}; cfg.StandardDeviation=c{10};
    value=bluetoothPathLoss(c{1},cfg);
    pathLoss(k)=struct('distance',c{1},'environment',c{2},'transmitter_antenna_gain',c{3},'receiver_antenna_gain',c{4},'transmitter_cable_loss',c{5},'receiver_cable_loss',c{6},'transmitter_antenna_height',c{7},'receiver_antenna_height',c{8},'path_loss_exponent',c{9},'standard_deviation',c{10},'path_loss_db',value);
end
ranges=struct('environment',{},'signal_power_type',{},'received_signal_power',{},'mode',{},'receiver_sensitivity',{},'link_margin',{},'transmitter_power',{},'transmitter_antenna_gain',{},'receiver_antenna_gain',{},'transmitter_cable_loss',{},'receiver_cable_loss',{},'path_loss_exponent',{},'standard_deviation',{},'range_m',{},'path_loss_db',{},'received_power_dbm',{});
rangeSpec = {
    {'Industrial','ReceiverSensitivity',-79,'LE1M',-94,7,10,2,1,1,3.1,2,2}; ...
    {'Home','ReceivedSignalPower',-80,'LE1M',-94,15,10,0,0,1.25,1.25,2.2,2.667}; ...
    {'Office','ReceiverSensitivity',-79,'LE2M',-90,10,15,3,2,0.5,0.25,2.2,2.667}};
for k=1:numel(rangeSpec)
    c=rangeSpec{k}; cfg=bluetoothRangeConfig;
    cfg.Environment=c{1}; cfg.SignalPowerType=c{2}; cfg.ReceivedSignalPower=c{3}; cfg.Mode=c{4}; cfg.ReceiverSensitivity=c{5}; cfg.LinkMargin=c{6}; cfg.TransmitterPower=c{7}; cfg.TransmitterAntennaGain=c{8}; cfg.ReceiverAntennaGain=c{9}; cfg.TransmitterCableLoss=c{10}; cfg.ReceiverCableLoss=c{11}; cfg.PathLossExponent=c{12}; cfg.StandardDeviation=c{13};
    [value,pl,rx]=bluetoothRange(cfg);
    ranges(k)=struct('environment',c{1},'signal_power_type',c{2},'received_signal_power',c{3},'mode',c{4},'receiver_sensitivity',c{5},'link_margin',c{6},'transmitter_power',c{7},'transmitter_antenna_gain',c{8},'receiver_antenna_gain',c{9},'transmitter_cable_loss',c{10},'receiver_cable_loss',c{11},'path_loss_exponent',c{12},'standard_deviation',c{13},'range_m',value,'path_loss_db',pl,'received_power_dbm',rx);
end
n=(0:127)'; cte=exp(1i*(0.013*n+0.0007*n.^2)); iq=bleCTEIQSample(cte,'Mode','LE1M','SamplesPerSymbol',8,'SlotDuration',2,'SampleOffset',4);
cteIQ=struct('real',real(cte)','imag',imag(cte)','mode','LE1M','samples_per_symbol',8,'slot_duration',2,'sample_offset',4,'output_real',real(iq)','output_imag',imag(iq)');
out=struct('durations',durations,'whitening',whitening,'waveforms',wf,'positions',positions,'channel_selection',channelSelection,'path_loss',pathLoss,'ranges',ranges,'cte_iq',cteIQ);
fid=fopen(wt_sample_path('bluetooth_core_samples.json'),'w','n','UTF-8'); fprintf(fid,'%s',jsonencode(out)); fclose(fid);
end
