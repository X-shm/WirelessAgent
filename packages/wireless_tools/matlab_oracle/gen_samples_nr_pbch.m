function gen_samples_nr_pbch(outdir)
%gen_samples_nr_pbch — Generate PBCH encode/decode golden samples.
%
% Usage:
%   gen_samples_nr_pbch()

    if nargin < 1
        outdir = wt_sample_dir();
    end

    rng(42);

    % === PBCH Encode ===
    cases = struct();

    % Case 1: standard 864-bit PBCH, ncellid=17, v=0
    ncellid = 17; v = 0;
    cw = randi([0 1], 864, 1);
    sym = nrPBCH(cw, ncellid, v);
    cases.encode_ncellid17_v0 = struct(...
        'ncellid', ncellid, 'v', v, ...
        'cw', cw(:)', ...
        'sym_real', real(sym(:))', 'sym_imag', imag(sym(:))');

    % Case 2: different v (v=3)
    v = 3;
    sym = nrPBCH(cw, ncellid, v);
    cases.encode_ncellid17_v3 = struct(...
        'ncellid', ncellid, 'v', v, ...
        'cw', cw(:)', ...
        'sym_real', real(sym(:))', 'sym_imag', imag(sym(:))');

    % Case 3: different ncellid (ncellid=500, v=7)
    ncellid = 500; v = 7;
    cw2 = randi([0 1], 864, 1);
    sym = nrPBCH(cw2, ncellid, v);
    cases.encode_ncellid500_v7 = struct(...
        'ncellid', ncellid, 'v', v, ...
        'cw', cw2(:)', ...
        'sym_real', real(sym(:))', 'sym_imag', imag(sym(:))');

    % Case 4: short codeword (40 bits) for CLI example compatibility
    ncellid = 17; v = 0;
    cw_short = randi([0 1], 40, 1);
    sym_short = nrPBCH(cw_short, ncellid, v);
    cases.encode_short_40bit = struct(...
        'ncellid', ncellid, 'v', v, ...
        'cw', cw_short(:)', ...
        'sym_real', real(sym_short(:))', 'sym_imag', imag(sym_short(:))');

    % === PBCH Decode (soft bits) ===
    % Case 5: decode perfect symbols (no noise), ncellid=17, v=0
    ncellid = 17; v = 0;
    cw3 = randi([0 1], 864, 1);
    sym_tx = nrPBCH(cw3, ncellid, v);
    soft_bits = nrPBCHDecode(sym_tx, ncellid, v);
    cases.decode_perfect_ncellid17_v0 = struct(...
        'ncellid', ncellid, 'v', v, 'nvar', 1e-10, ...
        'sym_real', real(sym_tx(:))', 'sym_imag', imag(sym_tx(:))', ...
        'soft_bits', soft_bits(:)');

    % Case 6: decode with noise
    nVar = 0.1;
    noise = sqrt(nVar/2) * (randn(size(sym_tx)) + 1j*randn(size(sym_tx)));
    sym_rx = sym_tx + noise;
    soft_bits_noisy = nrPBCHDecode(sym_rx, ncellid, v, nVar);
    cases.decode_noisy_nvar01 = struct(...
        'ncellid', ncellid, 'v', v, 'nvar', nVar, ...
        'sym_real', real(sym_rx(:))', 'sym_imag', imag(sym_rx(:))', ...
        'soft_bits', soft_bits_noisy(:)');

    % Write JSON
    outfile = fullfile(outdir, 'nr_pbch.json');
    fid = fopen(outfile, 'w');
    fprintf(fid, '%s', jsonencode(cases));
    fclose(fid);
    fprintf('Wrote %s (%d cases)\n', outfile, length(fieldnames(cases)));
end
