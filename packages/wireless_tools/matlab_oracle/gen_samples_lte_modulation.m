%% gen_samples_lte_modulation.m
% Generate golden samples for lte_modulation (lteSymbolModulate / lteSymbolDemodulate).
% Output: lte_mod_tables.json (full constellation mapping) + lte_modulation_samples.json (random samples).
% Run: matlab -batch "run('gen_samples_lte_modulation.m')"
mods = {'BPSK','QPSK','16QAM','64QAM','256QAM','1024QAM'};
bpsMap = containers.Map(mods, {1,2,4,6,8,10});

tables = {};
samples = {};
for m = 1:numel(mods)
    modname = mods{m};
    bps = bpsMap(modname);
    M = 2^bps;

    % Full constellation table: every bit pattern -> symbol (TS 36.211 mapping)
    for i = 0:M-1
        bs = dec2bin(i, bps);
        bits = bs - '0';                    % 1 x bps
        sym = lteSymbolModulate(bits.', modname); % column input
        tables{end+1} = struct( ...
            'modulation', modname, ...
            'bits', bits, ...
            'symbols_real', real(sym.'), ...
            'symbols_imag', imag(sym.'));
    end

    % Random samples for validation (16 symbols each)
    rng(m);
    nbits = 16*bps;
    rbits = randi([0 1], nbits, 1);
    rsym = lteSymbolModulate(rbits, modname);
    samples{end+1} = struct( ...
        'modulation', modname, ...
        'bits', rbits.', ...
        'symbols_real', real(rsym.'), ...
        'symbols_imag', imag(rsym.'));
end

% Write tables + samples
jsonTables = jsonencode(tables);
fid = fopen(wt_sample_path('lte_mod_tables.json'),'w','n','UTF-8');
fprintf(fid, '%s', jsonTables);
fclose(fid);

jsonSamples = jsonencode(samples);
fid = fopen(wt_sample_path('lte_modulation_samples.json'),'w','n','UTF-8');
fprintf(fid, '%s', jsonSamples);
fclose(fid);

fprintf('Wrote lte_mod_tables.json (%d table rows) and lte_modulation_samples.json (%d sample groups)\n', ...
    numel(tables), numel(samples));
