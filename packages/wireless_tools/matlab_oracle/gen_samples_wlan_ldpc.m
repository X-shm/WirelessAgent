%% gen_samples_wlan_ldpc.m
% Export WLAN LDPC H matrices and generate golden samples.
% Covers rates 1/2, 2/3, 3/4, 5/6 at block lengths 648, 1296, 1944.
fprintf('start wlan ldpc sample generation\n');

% Part 1: Export H matrices in sparse format (row, col, val)
rates = [1/2, 2/3, 3/4, 5/6];
rate_labels = {'1_2', '2_3', '3_4', '5_6'};
block_lengths = [648, 1296, 1944];

matrices = struct();

for ri = 1:numel(rates)
    rate = rates(ri);
    rate_label = rate_labels{ri};
    for bi = 1:numel(block_lengths)
        bl = block_lengths(bi);
        key = sprintf('rate%s_blk%d', rate_label, bl);
        fprintf('  exporting H: rate=%s blk=%d\n', rate_label, bl);

        H = wlan.internal.ldpcMatrix(rate, bl);
        % Convert to sparse triplet format for compact JSON export
        [rows, cols, vals] = find(H);
        matrices.(key) = struct(...
            'rate', rate, ...
            'block_length', bl, ...
            'n_rows', size(H,1), ...
            'n_cols', size(H,2), ...
            'n_info', round(bl * rate), ...
            'n_parity', size(H,1), ...
            'rows', rows.' - 1, ...  % 0-indexed
            'cols', cols.' - 1, ...  % 0-indexed
            'nnz', numel(vals));
    end
end

% Save matrices JSON
matpath = wt_sample_path('wlan_ldpc_matrices.json');
jsonOut = jsonencode(matrices);
fid = fopen(matpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('  matrices exported\n');

% Part 2: Generate golden samples for encoding and decoding
encode_samples = [];
decode_samples = [];
test_rates = [1/2, 3/4];
test_rate_labels = {'1_2', '3_4'};
test_blks = [648, 1296];

for ri = 1:numel(test_rates)
    rate = test_rates(ri);
    rate_label = test_rate_labels{ri};
    for bi = 1:numel(test_blks)
        bl = test_blks(bi);
        n_info = round(bl * rate);
        n_parity = bl - n_info;

        rng(4000 + ri*10 + bi);

        % Encode test
        info_bits = randi([0 1], n_info, 1);
        parity = wlan.internal.ldpcEncodeCore(info_bits, rate);
        codeword = [info_bits; parity];

        % Verify parity check
        H = wlan.internal.ldpcMatrix(rate, bl);
        syndrome = mod(H * double(codeword), 2);
        par_ok = sum(syndrome) == 0;

        s = struct();
        s.case_name = sprintf('encode_%s_blk%d', rate_label, bl);
        s.rate_str = rate_label;
        s.block_length = bl;
        s.n_info = n_info;
        s.n_parity = n_parity;
        s.info_bits = info_bits.';
        s.parity_bits = parity.';
        s.codeword = codeword.';
        s.parity_check_ok = par_ok;
        encode_samples = [encode_samples; s];
        fprintf('  encode sample: rate=%s blk=%d parity_ok=%d\n', rate_label, bl, par_ok);

        % Decode test - add noise and decode
        % BPSK modulate + AWGN + LLR
        snr_db = 3;
        sigma = 10^(-snr_db/20);
        bpsk = 1 - 2*double(codeword);
        rng(4100 + ri*10 + bi);
        noisy = bpsk + sigma * randn(size(bpsk));
        llr = (2 * noisy) / (sigma^2);  % LLR = 2*y/sigma^2 for AWGN

        % Decode using norm-min-sum (same as our Python implementation)
        cfg = struct();
        cfg.VecPayloadBits = n_info;
        cfg.Rate = rate;
        cfg.NumCW = 1;
        cfg.LengthLDPC = bl;
        cfg.VecShortenBits = 0;
        cfg.VecPunctureBits = 0;
        cfg.VecRepeatBits = 0;

        % R2026a renamed this internal decoder from wlanLDPCDecode to
        % ldpcDecode while retaining the same documented internal signature.
        [decoded, n_iter] = wlan.internal.ldpcDecode(llr, cfg, 'norm-min-sum', 0.75, 20, 'early');
        ber = sum(decoded ~= info_bits) / n_info;

        s2 = struct();
        s2.case_name = sprintf('decode_%s_blk%d_snr3', rate_label, bl);
        s2.rate_str = rate_label;
        s2.block_length = bl;
        s2.n_info = n_info;
        s2.snr_db = snr_db;
        s2.llr = llr.';
        s2.decoded_bits = decoded.';
        s2.num_iterations = n_iter;
        s2.ber = ber;
        decode_samples = [decode_samples; s2];
        fprintf('  decode sample: rate=%s blk=%d snr=%ddB iter=%d ber=%.4f\n', ...
            rate_label, bl, snr_db, n_iter, ber);
    end
end

% Also test 5/6 rate at 1944 (largest config)
rate = 5/6;
rate_label = '5_6';
bl = 1944;
n_info = round(bl * rate);
n_parity = bl - n_info;

rng(4099);
info_bits = randi([0 1], n_info, 1);
parity = wlan.internal.ldpcEncodeCore(info_bits, rate);
codeword = [info_bits; parity];
H = wlan.internal.ldpcMatrix(rate, bl);
syndrome = mod(H * double(codeword), 2);
par_ok = sum(syndrome) == 0;

s = struct();
s.case_name = 'encode_5_6_blk1944';
s.rate_str = rate_label;
s.block_length = bl;
s.n_info = n_info;
s.n_parity = n_parity;
s.info_bits = info_bits.';
s.parity_bits = parity.';
s.codeword = codeword.';
s.parity_check_ok = par_ok;
encode_samples = [encode_samples; s];
fprintf('  encode sample: rate=%s blk=%d parity_ok=%d\n', rate_label, bl, par_ok);

% Save samples JSON
samplepath = wt_sample_path('wlan_ldpc_samples.json');
all_samples = struct();
all_samples.encode = encode_samples;
all_samples.decode = decode_samples;
jsonOut2 = jsonencode(all_samples);
fid2 = fopen(samplepath, 'w', 'n', 'UTF-8');
fprintf(fid2, '%s', jsonOut2);
fclose(fid2);
fprintf('  %d encode + %d decode samples written\n', numel(encode_samples), numel(decode_samples));

fprintf('done\n');
