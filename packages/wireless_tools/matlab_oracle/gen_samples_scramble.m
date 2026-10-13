%% gen_samples_scramble.m
% Golden samples for wlanScramble / wlanDescramble.
% IEEE 802.11 scrambler: 7-bit LFSR, polynomial x^7 + x^4 + 1.
% Scrambling and descrambling use the same operation (self-synchronous).
fprintf('start\n');

samples = [];

% Test case 1: standard seed 93 (0x5D), short sequence
seed1 = 93;
rng(3001);
bits1 = randi([0 1], 48, 1);
scr1 = wlanScramble(bits1, seed1);
desc1 = wlanScramble(scr1, seed1);  % roundtrip
s1 = struct();
s1.case_name = 'short_seed93';
s1.seed = seed1;
s1.input_len = numel(bits1);
s1.input_bits = bits1.';
s1.scrambled_bits = scr1.';
s1.roundtrip_bits = desc1.';
s1.roundtrip_errors = sum(desc1 ~= bits1);
samples = [samples; s1];
fprintf('  case1: seed=%d len=%d roundtrip_err=%d\n', seed1, numel(bits1), s1.roundtrip_errors);

% Test case 2: seed 127 (all ones), medium sequence
seed2 = 127;
rng(3002);
bits2 = randi([0 1], 120, 1);
scr2 = wlanScramble(bits2, seed2);
desc2 = wlanScramble(scr2, seed2);
s2 = struct();
s2.case_name = 'medium_seed127';
s2.seed = seed2;
s2.input_len = numel(bits2);
s2.input_bits = bits2.';
s2.scrambled_bits = scr2.';
s2.roundtrip_bits = desc2.';
s2.roundtrip_errors = sum(desc2 ~= bits2);
samples = [samples; s2];
fprintf('  case2: seed=%d len=%d roundtrip_err=%d\n', seed2, numel(bits2), s2.roundtrip_errors);

% Test case 3: seed 1, long sequence (typical PSDU length)
seed3 = 1;
rng(3003);
bits3 = randi([0 1], 500, 1);
scr3 = wlanScramble(bits3, seed3);
desc3 = wlanScramble(scr3, seed3);
s3 = struct();
s3.case_name = 'long_seed1';
s3.seed = seed3;
s3.input_len = numel(bits3);
s3.input_bits = bits3.';
s3.scrambled_bits = scr3.';
s3.roundtrip_bits = desc3.';
s3.roundtrip_errors = sum(desc3 ~= bits3);
samples = [samples; s3];
fprintf('  case3: seed=%d len=%d roundtrip_err=%d\n', seed3, numel(bits3), s3.roundtrip_errors);

% Test case 4: all-zero input (verifies LFSR output sequence)
seed4 = 93;
bits4 = zeros(64, 1);
scr4 = wlanScramble(bits4, seed4);
s4 = struct();
s4.case_name = 'allzeros_seed93';
s4.seed = seed4;
s4.input_len = numel(bits4);
s4.input_bits = bits4.';
s4.scrambled_bits = scr4.';
s4.roundtrip_bits = wlanScramble(scr4, seed4).';
s4.roundtrip_errors = sum(wlanScramble(scr4, seed4) ~= bits4);
samples = [samples; s4];
fprintf('  case4: seed=%d len=%d roundtrip_err=%d\n', seed4, numel(bits4), s4.roundtrip_errors);

% Test case 5: alternating 1010... pattern
seed5 = 63;
bits5 = repmat([1;0], 40, 1);
scr5 = wlanScramble(bits5, seed5);
s5 = struct();
s5.case_name = 'alternating_seed63';
s5.seed = seed5;
s5.input_len = numel(bits5);
s5.input_bits = bits5.';
s5.scrambled_bits = scr5.';
s5.roundtrip_bits = wlanScramble(scr5, seed5).';
s5.roundtrip_errors = sum(wlanScramble(scr5, seed5) ~= bits5);
samples = [samples; s5];
fprintf('  case5: seed=%d len=%d roundtrip_err=%d\n', seed5, numel(bits5), s5.roundtrip_errors);

% Test case 6: seed 2 (minimum non-trivial seed)
seed6 = 2;
rng(3006);
bits6 = randi([0 1], 30, 1);
scr6 = wlanScramble(bits6, seed6);
s6 = struct();
s6.case_name = 'edge_seed2';
s6.seed = seed6;
s6.input_len = numel(bits6);
s6.input_bits = bits6.';
s6.scrambled_bits = scr6.';
s6.roundtrip_bits = wlanScramble(scr6, seed6).';
s6.roundtrip_errors = sum(wlanScramble(scr6, seed6) ~= bits6);
samples = [samples; s6];
fprintf('  case6: seed=%d len=%d roundtrip_err=%d\n', seed6, numel(bits6), s6.roundtrip_errors);

jsonOut = jsonencode(samples);
outpath = wt_sample_path('scramble_samples.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d scramble samples\n', numel(samples));
fprintf('done\n');
