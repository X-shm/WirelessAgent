% Verified finite control-channel RE allocation configurations.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 25 50 100]
    for cellid = [0 37]
        for ports = [1 2 4]
            for cfi = [1 2 3]
                enb = struct('NDLRB',nrb,'NCellID',cellid,'CellRefP',ports, ...
                    'CFI',cfi,'NSubframe',0,'PHICHDuration','Normal','Ng','One');
                for entry = {'ltePDCCHIndices','ltePHICHIndices'}
                    name = entry{1};
                    positions = feval(name,enb,{'1based','sub'});
                    records{end+1} = struct('entry',name,'nrb',nrb,'ncellid',cellid, ...
                        'ports',ports,'cfi',cfi,'indices',double(positions)); %#ok<AGROW>
                end
            end
        end
    end
end
output = fullfile(root,'samples','lte_control_indices.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
