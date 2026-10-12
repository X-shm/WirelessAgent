%% gen_samples_rate_match_v2.m
% Golden samples with FULL output for nrRateMatchLDPC validation.
fprintf('start\n');
samples = [];
rng_seed = 5001;

% BG1 Zc=8: 528-bit codeword -> various outlen/rv/mod
bgn = 1; zc = 8; K = 22*zc;
rng(rng_seed); rng_seed = rng_seed + 1;
info = randi([0 1], K, 1);
cw = nrLDPCEncode(info, 1);

for outlen = [128, 256, 400, 528]
    for rv = 0:0  % just rv=0 for now (simpler validation)
        for mod = {'QPSK', '16QAM'}
            try
                out = nrRateMatchLDPC(cw, outlen, rv, mod{1}, 1);
                s = struct();
                s.bgn = 1; s.zc = 8; s.outlen = outlen; s.rv = rv;
                s.mod = mod{1}; s.nlayers = 1;
                s.cw_len = numel(cw); s.out_len = numel(out);
                s.codeword = cw';
                s.output = out';
                samples = [samples; s];
                fprintf('  BG1 Zc=8 outlen=%d rv=%d mod=%s out=%d\n', outlen, rv, mod{1}, numel(out));
            catch e
                fprintf('  ERROR: %s\n', e.message);
            end
        end
    end
end

% BG2 Zc=8: 400-bit codeword
rng(rng_seed); rng_seed = rng_seed + 1;
info = randi([0 1], 10*8, 1);
cw = nrLDPCEncode(info, 2);
for outlen = [100, 200, 400]
    rv = 0;
    for mod = {'QPSK'}
        out = nrRateMatchLDPC(cw, outlen, rv, mod{1}, 1);
        s = struct();
        s.bgn = 2; s.zc = 8; s.outlen = outlen; s.rv = rv;
        s.mod = mod{1}; s.nlayers = 1;
        s.cw_len = numel(cw); s.out_len = numel(out);
        s.codeword = cw';
        s.output = out';
        samples = [samples; s];
        fprintf('  BG2 Zc=8 outlen=%d rv=%d mod=%s out=%d\n', outlen, rv, mod{1}, numel(out));
    end
end

jsonOut = jsonencode(samples);
outpath = wt_sample_path('rate_match_samples.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d rate match samples\n', numel(samples));
fprintf('done\n');
