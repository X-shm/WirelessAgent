% Independent R2026a NB-IoT shared/control downlink RE cases.
root = fileparts(mfilename('fullpath'));
records = {};
enbs = {struct('NNCellID',0,'NBRefP',1),...
        struct('NNCellID',37,'NBRefP',2,'OperationMode','Inband-SamePCI',...
               'ControlRegionSize',3),...
        struct('NNCellID',5,'NBRefP',1,'OperationMode','Inband-DifferentPCI',...
               'CellRefP',4,'ControlRegionSize',2)};
for k = 1:numel(enbs)
    enb = enbs{k};
    chs = struct('NPDSCHDataType','NotBCCH','NSF',2,'Modulation','QPSK');
    [positions,info] = lteNPDSCHIndices(enb,chs,{'1based','sub'});
    records{end+1} = struct('entry','lteNPDSCHIndices','enb',enb,...
        'channel',chs,'indices',double(positions),'info',info); %#ok<AGROW>
    for ncce = {0,1,[0 1]}
        chs2 = struct('NCCE',ncce{1});
        [positions2,info2] = lteNPDCCHIndices(enb,chs2,{'1based','sub'});
        records{end+1} = struct('entry','lteNPDCCHIndices','enb',enb,...
            'channel',chs2,'indices',double(positions2),'info',info2); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_nb_downlink_indices.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
