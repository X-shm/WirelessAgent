% Independent R2026a PBCH resource-element index cases.
root = fileparts(mfilename('fullpath'));
configs = {struct('NDLRB',6,'NCellID',0,'CellRefP',1,'NSubframe',0),...
           struct('NDLRB',50,'NCellID',37,'CellRefP',4,'NSubframe',0),...
           struct('NDLRB',25,'NCellID',1,'CellRefP',2,...
                  'CyclicPrefix','Extended','NSubframe',0),...
           struct('NDLRB',6,'NCellID',0,'CellRefP',1,'NSubframe',1)};
records = cell(1,numel(configs));
for k = 1:numel(configs)
    positions = ltePBCHIndices(configs{k},{'1based','sub'});
    records{k} = struct('config',configs{k},'indices',double(positions));
end
output = fullfile(root,'samples','lte_pbch_indices.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
