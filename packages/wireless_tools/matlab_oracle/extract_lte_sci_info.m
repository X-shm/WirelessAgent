% All NSLRB-dependent SCI payload lengths.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = 6:110
    info = lteSCIInfo(struct('NSLRB',nrb));
    records{end+1} = struct('nrb',nrb,'info',info); %#ok<AGROW>
end
output = fullfile(root,'samples','lte_sci_info.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
