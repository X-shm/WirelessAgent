% Independent R2026a NPBCH index and info cases for Python validation.
root = fileparts(mfilename('fullpath'));
settings = {struct('NNCellID',0,'NBRefP',1,'NSubframe',0,'NFrame',0),...
            struct('NNCellID',10,'NBRefP',2,'NSubframe',0,'NFrame',4),...
            struct('NNCellID',503,'NBRefP',2,'NSubframe',1,'NFrame',0)};
records = cell(1,numel(settings));
for k = 1:numel(settings)
    enb = settings{k};
    [indices,info] = lteNPBCHIndices(enb,{'1based','sub'});
    records{k} = struct('config',enb,'indices',double(indices),'info',info);
end
output = fullfile(root,'samples','lte_npbch_indices.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
