%% gen_samples_ldpc.m
% Generate golden samples for LDPC encoding (nrLDPCEncode).
% Note: 5G LDPC is NOT systematic; output is the full punctured codeword.
fprintf('start\n');
bgns = [1, 2];
zcs = [8, 16, 32];
samples = [];
for bi = 1:numel(bgns)
    for zi = 1:numel(zcs)
        bgn = bgns(bi);
        zc = zcs(zi);
        nsys = 22; if bgn==2, nsys=10; end
        K = nsys * zc;
        rng(1000 + bgn*100 + zc);
        info = randi([0 1], K, 1);
        cw = nrLDPCEncode(info, bgn);
        s = struct();
        s.bgn = bgn;
        s.zc = zc;
        s.info = info';
        s.codeword = cw';
        s.n_info = K;
        s.n_codeword = numel(cw);
        samples = [samples; s];
    end
end
jsonOut = jsonencode(samples);
outpath = wt_sample_path('ldpc_samples.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d LDPC samples\n', numel(samples));
fprintf('done\n');
