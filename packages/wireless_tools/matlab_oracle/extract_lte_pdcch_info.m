% Extract FDD PDCCH control-region resources over key configurations.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 15 25 50 75 100]
    for cp = {'Normal','Extended'}
        for ports = [1 2 4]
            for cfi = 1:3
                for ng = {'Sixth','One','Two'}
                    enb = struct('NDLRB',nrb,'CyclicPrefix',cp{1}, ...
                        'CellRefP',ports,'CFI',cfi,'Ng',ng{1});
                    info = ltePDCCHInfo(enb);
                    records{end+1} = struct('nrb',nrb,'cyclic_prefix',cp{1}, ...
                        'ports',ports,'cfi',cfi,'ng',ng{1},'info',info); %#ok<AGROW>
                end
            end
        end
    end
end
output = fullfile(root,'samples','lte_pdcch_info.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
