% Independent R2026a PCFICH info and RE positions.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 50]
    for ncellid = [0 1 37]
        for ports = [1 2 4]
            enb = struct('NDLRB',nrb,'NCellID',ncellid,'CellRefP',ports);
            positions = ltePCFICHIndices(enb,{'1based','sub'});
            records{end+1} = struct('nrb',nrb,'ncellid',ncellid,...
                'ports',ports,'indices',double(positions)); %#ok<AGROW>
        end
    end
end
info = ltePCFICHInfo();
output = fullfile(root,'samples','lte_pcfich.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(struct('positions',{records},'info',info)));
fclose(fid);
disp(output);
