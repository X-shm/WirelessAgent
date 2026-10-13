%% gen_samples_symbol_mod.m
% Generate golden samples for modulation tools (nrSymbolModulate).
% Output: samples JSON resolved from this script's directory.
% Run: addpath('matlab_oracle'); gen_samples_symbol_mod
mods = {'BPSK','pi/2-BPSK','QPSK','16QAM','64QAM','256QAM','1024QAM'};
% BPSK -> 1 bits/sym; QPSK -> 2; 16QAM -> 4; 64QAM -> 6; 256QAM -> 8; 1024QAM -> 10
bps = containers.Map({'BPSK','pi/2-BPSK','QPSK','16QAM','64QAM','256QAM','1024QAM'}, ...
                     {1, 1, 2, 4, 6, 8, 10});
seeds = containers.Map({'BPSK','pi/2-BPSK','QPSK','16QAM','64QAM','256QAM','1024QAM'}, ...
                       {1, 2, 3, 4, 5, 6, 7});

all_samples = [];
for m = 1:numel(mods)
    modname = mods{m};
    bits_per_sym = bps(modname);
    nbits = 8*bits_per_sym;   % 8 symbols per sample
    rng(seeds(modname));
    bits = randi([0 1], nbits, 1);
    sym = nrSymbolModulate(bits, modname);
    sample = struct();
    sample.modulation = modname;
    sample.bits = bits.';
    sample.symbols_real = real(sym.');
    sample.symbols_imag = imag(sym.');
    sample.n_symbols = numel(sym);
    all_samples = [all_samples; sample];
end

% JSON output
jsonOut = jsonencode(all_samples);
fid = fopen(wt_sample_path('symbol_mod_samples.json'),'w','n','UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('Wrote %d samples to %s\n', numel(all_samples), wt_sample_path('symbol_mod_samples.json'));
