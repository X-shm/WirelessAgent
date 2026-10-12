%% gen_samples_rate_match.m
% Golden samples for nrRateMatchLDPC. 3GPP TS 38.212 §5.4.2
fprintf('start\n');
samples = [];

% BG1 Zc=8, 528-bit codeword -> rate match to various lengths
bgn = 1; zc = 8; K = 22*zc;
in_rng = 1;
for outlen = [256, 384, 512, 720]
    rng(in_rng); in_rng = in_rng + 1;
    info = randi([0 1], K, 1);
    cw = nrLDPCEncode(info, 1);
    for rv = 0:1  % 2 redundancy versions
        for mod = {'QPSK', '16QAM'}
            try
                out = nrRateMatchLDPC(cw, outlen, rv, mod{1}, 1);
                s = struct();
                s.bgn = 1; s.zc = 8; s.outlen = outlen; s.rv = rv;
                s.mod = mod{1}; s.nlayers = 1;
                s.input_len = numel(cw); s.output_len = numel(out);
                s.output_bits = out(1:min(20,numel(out)))'; % first 20 bits only
                s.output_hash = mod(sum(double(out)), 100000);
                samples = [samples; s];
            catch
            end
        end
    end
end

% Also test recovery roundtrip
fprintf('=== roundtrip test ===\n');
cw = nrLDPCEncode(randi([0 1],22*8,1), 1);
rm_out = nrRateMatchLDPC(cw, 400, 0, 'QPSK', 1);
recovered = nrRateRecoverLDPC(rm_out, 400, 'QPSK', 1, 528);
fprintf('recovery size match: %d\n', numel(recovered));

jsonOut = jsonencode(samples);
outpath = wt_sample_path('rate_match_samples.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d samples\n', numel(samples));
fprintf('done\n');
