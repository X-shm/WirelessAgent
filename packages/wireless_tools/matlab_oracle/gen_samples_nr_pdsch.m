%% gen_samples_nr_pdsch.m
% Golden samples for nr_pdsch end-to-end chain.
% Simplified: single code block, single layer, no scrambling.
% Chain: CRC24A -> LDPC -> rate match -> modulation -> layer map -> OFDM
fprintf('start nr_pdsch sample generation\n');

samples = [];

% Test configurations
configs = {
    struct('name', 'bg1_qpsk_zc2', 'bgn', 1, 'zc', 2, 'mod', 'QPSK', 'nfft', 128, 'n_sc', 12);
    struct('name', 'bg1_16qam_zc4', 'bgn', 1, 'zc', 4, 'mod', '16QAM', 'nfft', 128, 'n_sc', 12);
    struct('name', 'bg2_qpsk_zc8', 'bgn', 2, 'zc', 8, 'mod', 'QPSK', 'nfft', 256, 'n_sc', 24);
    struct('name', 'bg1_64qam_zc16', 'bgn', 1, 'zc', 16, 'mod', '64QAM', 'nfft', 256, 'n_sc', 48);
};

for ci = 1:numel(configs)
    cfg = configs{ci};
    name = cfg.name;
    bgn = cfg.bgn;
    zc = cfg.zc;
    mod_str = cfg.mod;
    nfft = cfg.nfft;
    n_sc = cfg.n_sc;

    % Compute info bits count
    if bgn == 1
        nsys = 22;
        ncw = 66;
    else
        nsys = 10;
        ncw = 50;
    end
    n_info = nsys * zc;  % info bits for LDPC
    n_crc = 24;  % CRC24A
    n_tb = n_info - n_crc;  % transport block size

    rng(5000 + ci);
    tb_bits = randi([0 1], n_tb, 1);

    % Step 1: CRC attachment (CRC24A)
    crc_bits = nrCRCEncode(tb_bits, '24A');  % includes data + CRC
    fprintf('  %s: TB=%d bits, after CRC=%d bits\n', name, n_tb, numel(crc_bits));

    % Step 2: LDPC encode
    codeword = nrLDPCEncode(crc_bits, bgn);
    fprintf('  %s: LDPC codeword = %d bits (punctured)\n', name, numel(codeword));

    % Step 3: Rate match
    % Calculate output length: n_sc * Qm (bits per symbol), single layer
    switch mod_str
        case 'QPSK'
            Qm = 2;
        case '16QAM'
            Qm = 4;
        case '64QAM'
            Qm = 6;
        case '256QAM'
            Qm = 8;
        case '1024QAM'
            Qm = 10;
        otherwise
            Qm = 2;
    end

    % Use 1 OFDM symbol, all REs carry PDSCH (no DMRS etc.)
    n_symbols = 1;
    outlen = n_sc * n_symbols * Qm;

    rm_bits = nrRateMatchLDPC(codeword, outlen, 0, mod_str, 1);
    fprintf('  %s: rate matched = %d bits (target %d)\n', name, numel(rm_bits), outlen);

    % Step 4: Modulation
    symbols = nrSymbolModulate(rm_bits, mod_str);
    fprintf('  %s: %d modulation symbols\n', name, numel(symbols));

    % Step 5: Layer mapping (1 layer = identity)
    layered = nrLayerMap(symbols, 1);
    % layered is (n_symbols_per_layer, 1) column vector

    % Step 6: OFDM waveform (note: we use our own nr_ofdm.py for this step,
    % as MATLAB's nrOFDMModulate includes windowing and phase compensation
    % that our simplified tool doesn't have. OFDM is separately validated.)

    % Build sample - we provide everything up to and including layered symbols
    s = struct();
    s.case_name = name;
    s.bgn = bgn;
    s.zc = zc;
    s.modulation = mod_str;
    s.nfft = nfft;
    s.n_sc = n_sc;
    s.n_symbols = n_symbols;
    s.tb_bits = tb_bits.';
    s.tb_len = n_tb;
    s.crc_bits = crc_bits.';
    s.ldpc_codeword = codeword.';
    s.rm_bits = rm_bits.';
    s.symbols_real = real(symbols.');
    s.symbols_imag = imag(symbols.');
    s.layered_real = real(layered.');
    s.layered_imag = imag(layered.');
    s.outlen = outlen;

    samples = [samples; s];
    fprintf('  sample %s done\n\n', name);
end

% Save samples JSON
samplepath = wt_sample_path('nr_pdsch_samples.json');
jsonOut = jsonencode(samples);
fid = fopen(samplepath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('%d samples written\n', numel(samples));
fprintf('done\n');

%% Helper - not used
function val = helper_get_qm(mod_str)
    switch mod_str
        case 'QPSK'
            val = 2;
        case '16QAM'
            val = 4;
        case '64QAM'
            val = 6;
        case '256QAM'
            val = 8;
        case '1024QAM'
            val = 10;
        otherwise
            val = 2;
    end
end
