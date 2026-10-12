%% gen_samples_bcc.m
% Golden samples for wlanBCCEncode. IEEE 802.11 BCC (g0=133, g1=171 octal)
fprintf('start\n');
rates = {'1/2','2/3','3/4','5/6'};
punc_len = containers.Map({'1/2','2/3','3/4','5/6'}, {2, 4, 6, 10});
min_k = containers.Map({'1/2','2/3','3/4','5/6'}, {40, 60, 40, 108});
samples = [];
seeds = containers.Map({'1/2','2/3','3/4','5/6'}, {2001, 2002, 2003, 2004});

for r = 1:numel(rates)
    rate = rates{r};
    rng(seeds(rate));
    K = randi([min_k(rate), min_k(rate)+40]);
    Q = punc_len(rate) / 2;
    K = ceil(K / Q) * Q;
    bits = randi([0 1], K, 1);
    enc = wlanBCCEncode(bits, rate);
    s = struct();
    s.rate = rate;
    s.input_len = numel(bits);
    s.output_len = numel(enc);
    s.input_bits = bits';
    s.output_bits = enc';
    s.output_hash = mod(sum(double(enc)), 10000);
    s.input_hash = mod(sum(double(bits)), 10000);
    samples = [samples; s];

    % Decode roundtrip
    dec = wlanBCCDecode(enc, rate, 'hard');
    rng(1); % re-seed traceback
    errs = sum(dec ~= bits);
    fprintf('  %s: in=%d out=%d roundtrip_errors=%d\n', rate, s.input_len, s.output_len, errs);
end

jsonOut = jsonencode(samples);
outpath = wt_sample_path('bcc_samples.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d BCC samples\n', numel(samples));
fprintf('done\n');
