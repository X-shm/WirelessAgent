function gen_samples_nr_equalize_mmse(outdir)
%gen_samples_nr_equalize_mmse — Generate MMSE equalization golden samples.
%
% Usage:
%   gen_samples_nr_equalize_mmse()

    if nargin < 1
        outdir = wt_sample_dir();
    end

    cases = struct();

    % Case 1: SISO flat channel, 2 REs, 1 antenna, 1 layer
    rxSym = [1+0j; 0.5+0.5j];  % NRE x R = 2 x 1
    Hest = zeros(2, 1, 1);      % NRE x R x P
    Hest(:,:,1) = [1; 1];       % H = 1 for both REs
    nVar = 0.01;
    [out, csi] = nrEqualizeMMSE(rxSym, Hest, nVar);
    cases.siso_flat_2re = struct(...
        'n_re', 2, 'n_rx', 1, 'n_layers', 1, 'nvar', nVar, ...
        'rx_real', real(rxSym(:,:))', 'rx_imag', imag(rxSym(:,:))', ...
        'hest_real', squeeze(real(Hest)), 'hest_imag', squeeze(imag(Hest)), ...
        'out_real', real(out)', 'out_imag', imag(out)', ...
        'csi', csi');

    % Case 2: 2x2 MIMO, 1 RE
    rxSym = [1+0.2j, 0.8-0.1j];    % 1 x 2 (1 RE, 2 antennas)
    Hest = zeros(1, 2, 2);          % 1 x 2 x 2
    Hest(1,:,1) = [1, 0.3];
    Hest(1,:,2) = [0.2, 1];
    nVar = 0.1;
    [out, csi] = nrEqualizeMMSE(rxSym, Hest, nVar);
    cases.mimo_2x2_1re = struct(...
        'n_re', 1, 'n_rx', 2, 'n_layers', 2, 'nvar', nVar, ...
        'rx_real', real(rxSym), 'rx_imag', imag(rxSym), ...
        'hest_real', squeeze(real(Hest)), 'hest_imag', squeeze(imag(Hest)), ...
        'out_real', real(out), 'out_imag', imag(out), ...
        'csi', csi);

    % Case 3: 2x1 SIMO (2 RX antennas, 1 layer), 4 REs
    nRe = 4;
    rxSym = zeros(nRe, 2);
    Hest = zeros(nRe, 2, 1);
    for k = 1:nRe
        h = [0.8 + 0.1j*k; 0.6 - 0.2j*k];
        Hest(k,:,1) = h;
        rxSym(k,:) = h * (0.7 + 0.3j);  % x = 0.7+0.3j
    end
    nVar = 0.05;
    [out, csi] = nrEqualizeMMSE(rxSym, Hest, nVar);
    cases.simo_2rx_4re = struct(...
        'n_re', nRe, 'n_rx', 2, 'n_layers', 1, 'nvar', nVar, ...
        'rx_real', real(rxSym), 'rx_imag', imag(rxSym), ...
        'hest_real', squeeze(real(Hest)), 'hest_imag', squeeze(imag(Hest)), ...
        'out_real', real(out), 'out_imag', imag(out), ...
        'csi', csi');

    % Case 4: high noise limit (nVar very large -> MMSE -> 0)
    rxSym = [1; 1];
    Hest = zeros(2,1,1);
    Hest(:,:,1) = [1; 1];
    nVar = 100;
    [out, csi] = nrEqualizeMMSE(rxSym, Hest, nVar);
    cases.high_noise = struct(...
        'n_re', 2, 'n_rx', 1, 'n_layers', 1, 'nvar', nVar, ...
        'rx_real', real(rxSym), 'rx_imag', imag(rxSym), ...
        'hest_real', squeeze(real(Hest)), 'hest_imag', squeeze(imag(Hest)), ...
        'out_real', real(out), 'out_imag', imag(out), ...
        'csi', csi);

    % Write JSON
    outfile = fullfile(outdir, 'nr_equalize_mmse.json');
    fid = fopen(outfile, 'w');
    fprintf(fid, '%s', jsonencode(cases));
    fclose(fid);
    fprintf('Wrote %s (%d cases)\n', outfile, length(fieldnames(cases)));
end
