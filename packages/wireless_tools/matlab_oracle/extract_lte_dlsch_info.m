% Single-transport-block DL-SCH segmentation oracle.
root = fileparts(mfilename('fullpath'));
lengths = [40 132 1000 6120 6144 10000 20000 100000];
records = {};
for length_bits = lengths
    info = lteDLSCHInfo(length_bits);
    records{end+1} = struct('block_length',length_bits,'info',info); %#ok<AGROW>
end
output = fullfile(root,'samples','lte_dlsch_info.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
