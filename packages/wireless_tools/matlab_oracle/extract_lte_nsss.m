% Capture independent R2026a oracle cases for standalone Python validation.
root = fileparts(mfilename('fullpath'));
cases = cell(1,4);
cases{1} = struct('OperationMode','Standalone','NNCellID',1,'NSubframe',9,'NFrame',0);
cases{2} = struct('OperationMode','Standalone','NNCellID',300,'NSubframe',9,'NFrame',2);
cases{3} = struct('OperationMode','Inband-SamePCI','NNCellID',1,'NSubframe',9,...
                  'NFrame',0,'NCellID',1,'CellRefP',1);
cases{4} = struct('OperationMode','Standalone','NNCellID',1,'NSubframe',9,'NFrame',1);
records = cell(1,numel(cases));
for k = 1:numel(cases)
    enb = cases{k};
    values = lteNSSS(enb);
    positions = lteNSSSIndices(enb,0,{'1based','sub'});
    records{k} = struct('config',enb,'real',real(values(:)).',...
                        'imag',imag(values(:)).','indices',double(positions));
end
output = fullfile(root,'samples','lte_nsss.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);

npssCases = cell(1,3);
npssCases{1} = struct('OperationMode','Standalone','NSubframe',5);
npssCases{2} = struct('OperationMode','Inband-SamePCI','NSubframe',5,...
                      'NCellID',1,'CellRefP',1);
npssCases{3} = struct('OperationMode','Standalone','NSubframe',4);
npssRecords = cell(1,numel(npssCases));
for k = 1:numel(npssCases)
    enb = npssCases{k};
    values = lteNPSS(enb);
    positions = lteNPSSIndices(enb,0,{'1based','sub'});
    npssRecords{k} = struct('config',enb,'real',real(values(:)).',...
                            'imag',imag(values(:)).','indices',double(positions));
end
output = fullfile(root,'samples','lte_npss.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(npssRecords));
fclose(fid);
disp(output);
