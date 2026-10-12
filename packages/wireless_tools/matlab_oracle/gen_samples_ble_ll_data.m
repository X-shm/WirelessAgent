function gen_samples_ble_ll_data()
%GEN_SAMPLES_BLE_LL_DATA R2026a data and all six control opcode samples.
cases=struct('configuration',{},'payload_hex',{},'pdu_hex',{},'decode_status',{});
spec={ ...
    struct('LLID','Data (continuation fragment/empty)'), ...
    struct('LLID','Data (start fragment/complete)','NESN',1,'SequenceNumber',1,'MoreData',true), ...
    struct('LLID','Control','ControlConfig',struct('Opcode','Connection update indication')), ...
    struct('LLID','Control','ControlConfig',struct('Opcode','Channel map indication','UsedChannels',[0 4 12 16 18 24 25],'Instant',12)), ...
    struct('LLID','Control','ControlConfig',struct('Opcode','Terminate indication','ErrorCode','Connection timeout')), ...
    struct('LLID','Control','ControlConfig',struct('Opcode','Unknown response','UnknownOpcode','21')), ...
    struct('LLID','Control','ControlConfig',struct('Opcode','Version indication','VersionNumber','4.2','CompanyIdentifier','1234','SubVersionNumber','ABCD')), ...
    struct('LLID','Control','ControlConfig',struct('Opcode','Reject indication','ErrorCode','Controller busy'))};
for k=1:numel(spec)
    props=spec{k}; cfg=bleLLDataChannelPDUConfig;
    fields=fieldnames(props);
    for n=1:numel(fields)
        if strcmp(fields{n},'ControlConfig')
            c=bleLLControlPDUConfig; values=props.ControlConfig; names=fieldnames(values);
            for m=1:numel(names), c.(names{m})=values.(names{m}); end
            cfg.ControlConfig=c;
        else
            cfg.(fields{n})=props.(fields{n});
        end
    end
    if strcmp(cfg.LLID,'Data (start fragment/complete)')
        payload='030004000A0100';
    else
        payload='';
    end
    if isempty(payload), bits=bleLLDataChannelPDU(cfg);
    else, bits=bleLLDataChannelPDU(cfg,payload); end
    bytes=bit2int(reshape(bits,8,[]),8,0);
    [status,~,~]=bleLLDataChannelPDUDecode(bits,cfg.CRCInitialization);
    cases(k)=struct('configuration',props,'payload_hex',payload, ...
        'pdu_hex',reshape(dec2hex(bytes,2).',1,[]),'decode_status',char(status));
end
fid=fopen(wt_sample_path('ble_ll_data_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(cases)); fclose(fid);
end
