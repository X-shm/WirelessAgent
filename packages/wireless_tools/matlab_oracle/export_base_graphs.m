%% export_base_graphs.m
% Export 5G NR LDPC base graphs (BG1/BG2) from baseGraph.mat to JSON.
% BG1: 46x68, BG2: 42x52. V(i,j) = shift value (0..Zc-1) or -1 (null).
% Export the 8 lifting-set variants for each BG.
fprintf('start\n');
bgs = coder.load('nr5g/internal/ldpc/baseGraph');
names = fieldnames(bgs);
fprintf('fields: %s\n', strjoin(names, ', '));
out = struct();
for f = 1:numel(names)
    V = bgs.(names{f});
    out.(names{f}) = V;
end
jsonOut = jsonencode(out);
outpath = wt_sample_path('base_graphs.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %s (%d KB)\n', outpath, numel(jsonOut)/1024);
fprintf('done\n');
