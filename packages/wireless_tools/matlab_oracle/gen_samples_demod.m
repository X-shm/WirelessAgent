% Golden samples for nrSymbolDemodulate (hard decision)
fprintf('start\n');
mods = {'BPSK','QPSK','16QAM','64QAM'};
samples = [];
rng(5001);
for m = 1:numel(mods)
    mod = mods{m};
    % 生成随机符号: 先调制再解调, 验证闭环
    switch mod
        case 'BPSK', bits = randi([0 1], 8, 1);
        case 'QPSK', bits = randi([0 1], 16, 1);
        case '16QAM', bits = randi([0 1], 32, 1);
        case '64QAM', bits = randi([0 1], 48, 1);
    end
    syms = nrSymbolModulate(bits, mod);
    dec = nrSymbolDemodulate(syms, mod, 'DecisionType','hard');
    s = struct();
    s.modulation = mod;
    s.bits = bits';
    s.symbols_real = real(syms)';
    s.symbols_imag = imag(syms)';
    s.decoded_bits = dec';
    samples = [samples; s];
    fprintf('  %s: %d bits, %d syms, decode_err=%d\n', mod, numel(bits), numel(syms), sum(dec~=bits));
end
jsonOut = jsonencode(samples);
fid = fopen(wt_sample_path('demod_samples.json'), 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d demod samples\n', numel(samples));
fprintf('done\n');
