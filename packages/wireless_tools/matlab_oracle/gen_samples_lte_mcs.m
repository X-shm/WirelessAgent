function gen_samples_lte_mcs()
% Generate golden samples for lte_mcs (lteMCS).
% Output: lte_mcs_samples.json
s = {};
s{1} = mkSample(-1:31, 'PDSCH');          % full range incl DTX(-1)
s{2} = mkSample(17, 'PDSCH');             % scalar
s{3} = mkSample([0 4 10 15 20 27 31], 'PDSCHTable2');
s{4} = mkSample([0 8 15 18 25 30 31], 'PDSCHTable3');
s{5} = mkSample(0:31, 'PUSCH');           % full incl reserved RV
s{6} = mkSample([29 30 31], 'PUSCH');     % RV signaling
s{7} = mkSample(-1, 'PDSCH');             % scalar DTX
samples = cat(2, s{:});
jsonOut = jsonencode(samples);
fid = fopen(wt_sample_path('lte_mcs_samples.json'),'w','n','UTF-8');
fprintf(fid,'%s',jsonOut);
fclose(fid);
fprintf('Wrote lte_mcs_samples.json (%d samples)\n', numel(samples));
end

function s = mkSample(imcs, table)
[itbs, mod, rv] = lteMCS(imcs, table);
if ischar(mod)
    modc = {mod};
else
    modc = mod(:).';
end
s = struct();
s.table = table;
s.imcs = imcs(:).';
s.itbs = itbs(:).';
s.mod = modc;
s.rv = rv(:).';
end
