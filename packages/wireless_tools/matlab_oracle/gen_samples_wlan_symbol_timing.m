function gen_samples_wlan_symbol_timing(outdir)
%gen_samples_wlan_symbol_timing — Generate L-LTF & symbol timing golden samples.
%
% Uses the real WLAN Toolbox functions:
%   wlan.internal.legacyLTF   — L-LTF reference waveform (exact generator used
%                               inside wlanSymbolTimingEstimate, numTx=1, CSD=0)
%   wlanLSTF / wlanLLTF       — public preamble generators for test waveforms
%   wlanSymbolTimingEstimate  — fine symbol timing estimation
%
% Golden cases:
%   lltf_<bw>        — L-LTF reference waveforms (amplitude normalization oracle)
%   timing_clean_cbw20        — exact preamble, threshold 1
%   timing_delay_cbw20        — known delay 53, zeros tail
%   timing_noisy_cbw20        — SNR 10 dB AWGN, delay 17, threshold 0.9
%   timing_csd_2rx_cbw20      — 2 tx CSD (-200ns on ant 2), 2 rx, threshold 0.8
%   timing_cbw40              — CBW40 preamble, delay 100
%   timing_short_cbw20        — Ns < L → empty outputs
%
% Usage:
%   gen_samples_wlan_symbol_timing()

    if nargin < 1
        outdir = wt_sample_dir();
    end

    cases = struct();
    rng(42);

    %% L-LTF reference waveforms (amplitude normalization oracle)
    bws = {'CBW20','CBW40','CBW80','CBW160','CBW320'};
    for i = 1:numel(bws)
        bw = bws{i};
        y = wlan.internal.legacyLTF(bw,1);
        key = ['lltf_' lower(bw)];
        cases.(key).real = real(y(:,1))';
        cases.(key).imag = imag(y(:,1))';
        cases.(key).mean_power = mean(abs(y(:,1)).^2);
        cases.(key).length = numel(y);
    end

    % Cross-check: public wlanLLTF vs internal legacyLTF (numTx=1, CSD=0)
    cfgNH = wlanNonHTConfig;
    ypub = wlanLLTF(cfgNH);
    yint = wlan.internal.legacyLTF('CBW20',1);
    cases.lltf_public_vs_internal_maxdiff = max(abs(ypub(:,1) - yint(:,1)));

    %% Symbol timing cases
    % Clean: exact L-STF + L-LTF, threshold 1 → startOffset = 0
    x = [wlanLSTF(cfgNH); wlanLLTF(cfgNH)];
    cases = add_timing_case(cases, 'timing_clean_cbw20', x, 'CBW20', 1);

    % Known delay 53 + zeros tail → startOffset = 53
    x = [zeros(53,1); wlanLSTF(cfgNH); wlanLLTF(cfgNH); zeros(40,1)];
    cases = add_timing_case(cases, 'timing_delay_cbw20', x, 'CBW20', 1);

    % Noisy: SNR 10 dB, delay 17, threshold 0.9
    sig = [zeros(17,1); wlanLSTF(cfgNH); wlanLLTF(cfgNH); zeros(60,1)];
    n = sqrt(0.05)*(randn(size(sig)) + 1i*randn(size(sig)));
    cases = add_timing_case(cases, 'timing_noisy_cbw20', sig + n, 'CBW20', 0.9);

    % CSD: 2 tx antennas (ant 2 shifted -200 ns), 2 rx antennas, delay 29,
    % threshold 0.8 → exercises the CSD refinement branch
    cfgV2 = wlanVHTConfig('ChannelBandwidth','CBW20','NumTransmitAntennas',2);
    x = [zeros(29,2); wlanLSTF(cfgV2); wlanLLTF(cfgV2); zeros(30,2)];
    cases = add_timing_case(cases, 'timing_csd_2rx_cbw20', x, 'CBW20', 0.8);

    % CBW40: gamma-rotated preamble, delay 100
    cfgV40 = wlanVHTConfig('ChannelBandwidth','CBW40');
    x = [zeros(100,1); wlanLSTF(cfgV40); wlanLLTF(cfgV40); zeros(50,1)];
    cases = add_timing_case(cases, 'timing_cbw40', x, 'CBW40', 1);

    % Short input: Ns < L → startOffset empty, metric empty
    x = complex(randn(100,1), randn(100,1));
    cases = add_timing_case(cases, 'timing_short_cbw20', x, 'CBW20', 1);

    %% Write JSON
    outfile = fullfile(outdir, 'wlan_symbol_timing.json');
    fid = fopen(outfile, 'w');
    fprintf(fid, '%s', jsonencode(cases));
    fclose(fid);
    fprintf('Wrote %s (%d cases)\n', outfile, numel(fieldnames(cases)));
end

function cases = add_timing_case(cases, key, x, chanbw, threshold)
    [startOffset, M] = wlanSymbolTimingEstimate(x, chanbw, threshold);
    cases.(key).chanbw = chanbw;
    cases.(key).threshold = threshold;
    cases.(key).waveform_real = real(x);   % Ns × Nr (column-major flat for 1 antenna)
    cases.(key).waveform_imag = imag(x);
    if isempty(startOffset)
        cases.(key).start_offset = [];
        cases.(key).metric = [];
    else
        cases.(key).start_offset = startOffset;
        cases.(key).metric = M';
    end
end
