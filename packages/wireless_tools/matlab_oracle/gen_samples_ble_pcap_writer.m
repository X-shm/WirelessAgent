function gen_samples_ble_pcap_writer()
%GEN_SAMPLES_BLE_PCAP_WRITER Compare exact R2026a PCAP bytes.
packets={'D6BE898E4009AB8967452301020106A8F1DF', ...
    'D6BE898E4409AB896745230102010665094E'};
timestamps=[0 18912345];
cases=struct('byte_order',{},'phy_header_present',{},'packets',{},'pcap_hex',{});
for k=1:3
    if k==1, order='little-endian'; hasHeader=false;
    elseif k==2, order='big-endian'; hasHeader=false;
    else, order='little-endian'; hasHeader=true; end
    stem=tempname;
    writer=blePCAPWriter('FileName',stem,'FileExtension','pcap', ...
        'ByteOrder',order,'PhyHeaderPresent',hasHeader);
    casePackets=struct('packet',{},'timestamp_us',{},'phy_header',{});
    for n=1:numel(packets)
        if hasHeader
            header='270A08010A0A0A0A0F00';
            write(writer,packets{n},timestamps(n),'PhyHeader',header);
        else
            header=''; write(writer,packets{n},timestamps(n));
        end
        casePackets(n)=struct('packet',packets{n}, ...
            'timestamp_us',timestamps(n),'phy_header',header);
    end
    delete(writer);
    filename=[stem '.pcap']; fid=fopen(filename,'r'); raw=fread(fid,inf,'uint8'); fclose(fid);
    delete(filename);
    cases(k)=struct('byte_order',order,'phy_header_present',hasHeader, ...
        'packets',casePackets,'pcap_hex',reshape(dec2hex(raw,2).',1,[]));
end
fid=fopen(wt_sample_path('ble_pcap_writer_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(cases)); fclose(fid);

ngCases=struct('byte_order',{},'phy_header_present',{}, ...
    'file_comment',{},'interface',{},'packets',{},'pcapng_hex',{});
for k=1:4
    if k==1, order='little-endian'; hasHeader=false; fileComment=''; interface='BLE';
    elseif k==2, order='big-endian'; hasHeader=false; fileComment='Capture test'; interface='LEradio';
    elseif k==3, order='little-endian'; hasHeader=true; fileComment='Bluetooth LE'; interface='BLE';
    else, order='big-endian'; hasHeader=true; fileComment=''; interface='Radio1'; end
    stem=tempname;
    writer=blePCAPWriter('FileName',stem,'FileExtension','pcapng', ...
        'ByteOrder',order,'PhyHeaderPresent',hasHeader, ...
        'FileComment',fileComment,'Interface',interface);
    casePackets=struct('packet',{},'timestamp_us',{}, ...
        'phy_header',{},'packet_comment',{});
    for n=1:numel(packets)
        if n==1 && k>1, comment='first packet'; else, comment=''; end
        if hasHeader
            header='270A08010A0A0A0A0F00';
            if isempty(comment), write(writer,packets{n},timestamps(n),'PhyHeader',header);
            else, write(writer,packets{n},timestamps(n),'PhyHeader',header, ...
                    'PacketComment',comment); end
        else
            header='';
            if isempty(comment), write(writer,packets{n},timestamps(n));
            else, write(writer,packets{n},timestamps(n),'PacketComment',comment); end
        end
        casePackets(n)=struct('packet',packets{n}, ...
            'timestamp_us',timestamps(n),'phy_header',header, ...
            'packet_comment',comment);
    end
    delete(writer);
    filename=[stem '.pcapng']; fid=fopen(filename,'r'); raw=fread(fid,inf,'uint8'); fclose(fid);
    delete(filename);
    ngCases(k)=struct('byte_order',order,'phy_header_present',hasHeader, ...
        'file_comment',fileComment,'interface',interface, ...
        'packets',casePackets,'pcapng_hex',reshape(dec2hex(raw,2).',1,[]));
end
fid=fopen(wt_sample_path('ble_pcapng_writer_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonencode(ngCases)); fclose(fid);
end
