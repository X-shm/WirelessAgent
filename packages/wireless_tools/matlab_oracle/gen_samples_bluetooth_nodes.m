function gen_samples_bluetooth_nodes()
%GEN_SAMPLES_BLUETOOTH_NODES Public constructor state, R2026a Update 3.
rng(7);
cases=struct('kind',{},'request',{},'nodes',{});

c=bluetoothNode;
cases(end+1)=record_case('classic',struct(),c); %#ok<AGROW>
c=bluetoothNode('central',Name='ClassicA',Position=[1 2 3], ...
    TransmitterGain=2,ReceiverGain=3,ReceiverSensitivity=-95,NoiseFigure=4);
request=struct('role','central','names','ClassicA','positions',[1 2 3], ...
    'properties',struct('transmitter_gain',2,'receiver_gain',3, ...
    'receiver_sensitivity',-95,'noise_figure',4));
cases(end+1)=record_case('classic',request,c); %#ok<AGROW>
c=bluetoothNode('peripheral',Position=[0 0 0;2 0 0], ...
    Name=["ClassicB","ClassicC"]);
request=struct('role','peripheral','names',{{'ClassicB','ClassicC'}}, ...
    'positions',[0 0 0;2 0 0]);
cases(end+1)=record_case('classic',request,c); %#ok<AGROW>

l=bluetoothLENode;
cases(end+1)=record_case('le',struct(),l); %#ok<AGROW>
l=bluetoothLENode('central',Name='LEA',Position=[4 5 6], ...
    TransmitterPower=5,AdvertisingInterval=0.040,ScanInterval=0.010, ...
    RandomAdvertising=true);
request=struct('role','central','names','LEA','positions',[4 5 6], ...
    'properties',struct('transmitter_power',5,'advertising_interval',0.040, ...
    'scan_interval',0.010,'random_advertising',true));
cases(end+1)=record_case('le',request,l); %#ok<AGROW>
l=bluetoothLENode('observer',Position=[0 1 0;0 2 0],Name=["LEB","LEC"]);
request=struct('role','observer','names',{{'LEB','LEC'}}, ...
    'positions',[0 1 0;0 2 0]);
cases(end+1)=record_case('le',request,l); %#ok<AGROW>

c=bluetoothNode('central',InterferenceModeling= ...
    'non-overlapping-adjacent-channel',MaxInterferenceOffset=2e6);
request=struct('role','central','properties',struct( ...
    'interference_modeling','non-overlapping-adjacent-channel', ...
    'max_interference_offset',2e6));
cases(end+1)=record_case('classic',request,c); %#ok<AGROW>
roles={'isochronous-broadcaster','synchronized-receiver', ...
    'broadcaster-observer','broadcaster'};
for k=1:numel(roles)
    l=bluetoothLENode(roles{k});
    cases(end+1)=record_case('le',struct('role',roles{k}),l); %#ok<AGROW>
end

fid=fopen(wt_sample_path('bluetooth_nodes_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(cases)); fclose(fid);
end

function out=record_case(kind,request,nodes)
items=struct('id',{},'name',{},'role',{},'position',{}, ...
    'node_address',{},'properties',{});
for k=1:numel(nodes)
    n=nodes(k);
    props=struct('transmitter_gain',n.TransmitterGain, ...
        'receiver_gain',n.ReceiverGain, ...
        'receiver_sensitivity',n.ReceiverSensitivity, ...
        'noise_figure',n.NoiseFigure, ...
        'interference_modeling',n.InterferenceModeling, ...
        'max_interference_offset',n.MaxInterferenceOffset);
    if strcmp(kind,'le')
        props.transmitter_power=n.TransmitterPower;
        props.advertising_interval=n.AdvertisingInterval;
        props.random_advertising=n.RandomAdvertising;
        props.scan_interval=n.ScanInterval;
        address=[];
        if ~isempty(n.NodeAddress), address=n.NodeAddress; end
    else
        address=n.NodeAddress;
    end
    items(end+1)=struct('id',n.ID,'name',n.Name,'role',n.Role, ...
        'position',n.Position,'node_address',address, ...
        'properties',props); %#ok<AGROW>
end
out=struct('kind',kind,'request',request,'nodes',items);
end
