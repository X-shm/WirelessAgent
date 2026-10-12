%% gen_samples_crc.m
% Generate golden samples for CRC encoding (nrCRCEncode).
% Polynomials: '6','11','16','24A','24B','24C' per TS 38.212 §5.1
fprintf('start\n');
polys = {'6','11','16','24A','24B','24C'};
seeds = containers.Map({'6','11','16','24A','24B','24C'}, ...
                       {1001, 1002, 1003, 1004, 1005, 1006});
samples = [];

for p = 1:numel(polys)
    poly = polys{p};
    rng(seeds(poly));
    % Small input: 12-40 bits
    K = randi([8, 32]);
    blk = randi([0 1], K, 1);
    blkcrc = nrCRCEncode(blk, poly);
    s = struct();
    s.poly = poly;
    s.input_bits = blk';
    s.output_bits = blkcrc';
    s.n_input = numel(blk);
    s.n_output = numel(blkcrc);
    s.n_crc = numel(blkcrc) - numel(blk);
    samples = [samples; s];
end

jsonOut = jsonencode(samples);
outpath = wt_sample_path('crc_samples.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d CRC samples to crc_samples.json\n', numel(samples));

% Verify decode roundtrip
fprintf('\n=== verify roundtrip ===\n');
for p = 1:numel(samples)
    s = samples(p);
    [dec, err] = nrCRCDecode(s.output_bits', s.poly);
    match = isequal(dec, s.input_bits');
    fprintf('  %s: input=%d crc=%d total=%d roundtrip=%d\n', ...
        s.poly, s.n_input, s.n_crc, s.n_output, match);
end
fprintf('done\n');
