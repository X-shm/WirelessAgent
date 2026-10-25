% FDD baseline PRACH information for standard LTE bandwidths and formats.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 15 25 50 75 100]
    for format = 0:3
        ue = struct('NULRB',nrb,'DuplexMode','FDD');
        chs = struct('Format',format,'SeqIdx',0,'PreambleIdx',0, ...
            'CyclicShiftIdx',0,'HighSpeed',0,'FreqOffset',0);
        info = ltePRACHInfo(ue,chs);
        records{end+1} = struct('nrb',nrb,'format',format,'info',info); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_prach_info.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
runtime = fullfile(root,'..','tools','_lte_prach_info.json');
fid = fopen(runtime,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
