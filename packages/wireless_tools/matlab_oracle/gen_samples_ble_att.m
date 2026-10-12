function gen_samples_ble_att()
%GEN_SAMPLES_BLE_ATT All R2026a ATT opcode encoder/decoder cases.
cfgDefault=bleATTPDUConfig;
names=cfgDefault.Opcode_Values;
cases=struct('opcode',{},'pdu_hex',{},'decode_status',{});
for k=1:numel(names)
    name=names{k}; cfg=bleATTPDUConfig('Opcode',name);
    if any(strcmp(name,{'Read response','Read blob response','Write request','Write command',...
            'Handle value notification','Handle value indication','Prepare write request',...
            'Prepare write response','Read by type response','Read by group type response',...
            'Find by type value request'}))
        cfg.AttributeValue='1234';
    end
    pdu=bleATTPDU(cfg);
    [status,~]=bleATTPDUDecode(pdu);
    cases(k)=struct('opcode',name,'pdu_hex',reshape(pdu.',1,[]),'decode_status',char(status));
end
fid=fopen(wt_sample_path('ble_att_samples.json'),'w','n','UTF-8'); fprintf(fid,'%s',jsonencode(cases)); fclose(fid);
end
