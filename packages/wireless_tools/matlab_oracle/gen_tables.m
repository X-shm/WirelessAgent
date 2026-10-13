%% gen_tables.m
% Extract FULL bit->symbol mapping tables from MATLAB nrSymbolModulate.
% This is the ground-truth oracle for the Python tool. Output: tables JSON.
mods = {'BPSK','pi/2-BPSK','QPSK','16QAM','64QAM','256QAM','1024QAM'};
bps = containers.Map({'BPSK','pi/2-BPSK','QPSK','16QAM','64QAM','256QAM','1024QAM'}, ...
                     {1, 1, 2, 4, 6, 8, 10});

all_tables = {};
for m = 1:numel(mods)
    modname = mods{m};
    nbits_per_sym = bps(modname);
    n_sym = 2^nbits_per_sym;

    if strcmp(modname, 'pi/2-BPSK')
        % pi/2-BPSK is position-dependent. Extract base mapping at position 0
        % by feeding 4x repetition and reading first symbol of each 4-block.
        pats = [0; 1];  % base bit values
        base = zeros(2,1); base_im = zeros(2,1);
        for p = 1:2
            bits = repmat(pats(p), 8, 1);
            sym = nrSymbolModulate(bits, modname);
            base(p) = real(sym(1));
            base_im(p) = imag(sym(1));
        end
        % Also extract the rotation sequence by feeding an 8-symbol stream
        bits = zeros(8,1);
        sym0 = nrSymbolModulate(bits, modname);
        bits = ones(8,1);
        sym1 = nrSymbolModulate(bits, modname);
        tbl = struct();
        tbl.modulation = modname;
        tbl.n_symbols = 2;
        tbl.base_real = base';
        tbl.base_imag = base_im';
        tbl.stream0_real = real(sym0.');
        tbl.stream0_imag = imag(sym0.');
        tbl.stream1_real = real(sym1.');
        tbl.stream1_imag = imag(sym1.');
        all_tables = [all_tables; tbl];
        continue;
    end

    % Enumerate ALL bit patterns, msb first, symbol-major ordering
    bits = zeros(n_sym * nbits_per_sym, 1);
    for s = 0:n_sym-1
        for k = 0:nbits_per_sym-1
            bits(s*nbits_per_sym + k + 1) = bitand(bitshift(s, -(nbits_per_sym-1-k)), 1);
        end
    end
    sym = nrSymbolModulate(bits, modname);
    tbl = struct();
    tbl.modulation = modname;
    tbl.n_symbols = n_sym;
    tbl.bits = bits.';
    tbl.symbols_real = real(sym.');
    tbl.symbols_imag = imag(sym.');
    all_tables = [all_tables; tbl];
end

jsonOut = jsonencode(all_tables);
outpath = wt_sample_path('mod_tables.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('Wrote %d tables to matlab_oracle/samples/mod_tables.json\n', numel(all_tables));
