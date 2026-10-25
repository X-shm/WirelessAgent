% Complete symmetric-bandwidth DCI payload geometry over LTE RB range.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = 6:110
    for ports = [1 2 4]
        for mode = {'FDD','TDD'}
            enb = struct('NDLRB',nrb,'NULRB',nrb, ...
                'CellRefP',ports,'DuplexMode',mode{1});
            info = lteDCIInfo(enb);
            records{end+1} = struct('nrb',nrb,'ports',ports, ...
                'mode',mode{1},'info',info); %#ok<AGROW>
        end
    end
end
output = fullfile(root,'samples','lte_dci_info.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
runtime = fullfile(root,'..','tools','_lte_dci_info.json');
fid = fopen(runtime,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
