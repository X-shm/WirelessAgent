%% gen_samples_lte_crc.m
% Generate golden samples for lte_crc (lteCRCEncode).
% Output: lte_crc_samples.json
% Run: matlab -batch "run('gen_samples_lte_crc.m')"
polys = {'24A','24B','16','8'};
samples = {};
seed = 1;
for p = 1:numel(polys)
    poly = polys{p};
    for len = [8 40 100]
        rng(seed); seed = seed + 1;
        bits = randi([0 1], len, 1);
        crc = lteCRCEncode(bits, poly);
        samples{end+1} = struct('poly', poly, 'bits', bits.', 'crc', crc.');
    end
    % Masked CRC (RNTI 0x1234), MSB-first xor
    rng(seed); seed = seed + 1;
    bits = randi([0 1], 24, 1);
    crc = lteCRCEncode(bits, poly, 0x1234);
    samples{end+1} = struct('poly', poly, 'bits', bits.', 'mask', uint16(0x1234), 'crc', crc.');
    % Filler bits (-1 treated as logical 0 in CRC calc, preserved in output)
    rng(seed); seed = seed + 1;
    bits = randi([0 1], 50, 1);
    bits(1:3) = -1;
    crc = lteCRCEncode(bits, poly);
    samples{end+1} = struct('poly', poly, 'bits', bits.', 'crc', crc.');
end

jsonOut = jsonencode(samples);
fid = fopen(wt_sample_path('lte_crc_samples.json'),'w','n','UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('Wrote lte_crc_samples.json (%d samples)\n', numel(samples));
