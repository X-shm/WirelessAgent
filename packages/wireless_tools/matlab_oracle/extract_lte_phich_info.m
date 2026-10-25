% Extract FDD PHICH resource geometry over bandwidth, Ng, CP and duration.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 15 25 50 75 100]
    for ng = {'Sixth','Half','One','Two'}
        for cp = {'Normal','Extended'}
            for duration = {'Normal','Extended'}
                enb = struct('NDLRB',nrb,'Ng',ng{1}, ...
                    'CyclicPrefix',cp{1},'PHICHDuration',duration{1});
                info = ltePHICHInfo(enb);
                records{end+1} = struct('nrb',nrb,'ng',ng{1}, ...
                    'cyclic_prefix',cp{1},'phich_duration',duration{1}, ...
                    'info',info); %#ok<AGROW>
            end
        end
    end
end
output = fullfile(root,'samples','lte_phich_info.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
