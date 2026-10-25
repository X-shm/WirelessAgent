% Independent R2026a NRS sequence and index cases for Python validation.
root = fileparts(mfilename('fullpath'));
settings = {struct('NNCellID',0,'NSubframe',0,'NBRefP',1),...
            struct('NNCellID',10,'NSubframe',2,'NBRefP',2),...
            struct('NNCellID',503,'NSubframe',9,'NBRefP',2)};
records = cell(1,numel(settings));
for k = 1:numel(settings)
    enb = settings{k};
    values = lteNRS(enb);
    positions = lteNRSIndices(enb,{'1based','sub'});
    records{k} = struct('config',enb,'real',real(values(:)).',...
                        'imag',imag(values(:)).','indices',double(positions));
end
output = fullfile(root,'samples','lte_nrs.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
