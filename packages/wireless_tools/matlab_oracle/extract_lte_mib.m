% Independent R2026a MIB encoding and decoding cases.
root = fileparts(mfilename('fullpath'));
configs = {struct('NDLRB',6),...
           struct('NDLRB',50,'Ng','Half','NFrame',100,'PHICHDuration','Extended'),...
           struct('NDLRB',100,'Ng','Two','NFrame',1023,'PHICHDuration','Normal'),...
           struct('NDLRB',20,'Ng','One','NFrame',7,'PHICHDuration','Extended')};
records = cell(1,numel(configs));
for k = 1:numel(configs)
    bits = lteMIB(configs{k});
    fields = lteMIB(bits);
    records{k} = struct('config',configs{k},'bits',double(bits(:)).',...
                        'decoded',fields);
end
output = fullfile(root,'samples','lte_mib.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
