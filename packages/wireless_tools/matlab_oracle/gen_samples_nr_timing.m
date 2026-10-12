function gen_samples_nr_timing(outdir)
%gen_samples_nr_timing — Generate timing estimation golden samples.
%
% Note: MATLAB's nrTimingEstimate expects a carrier config + reference grid,
% but our simplified version takes waveforms directly. We generate samples
% using MATLAB's xcorr to match the core correlation logic.
%
% Usage:
%   gen_samples_nr_timing()

    if nargin < 1
        outdir = wt_sample_dir();
    end

    cases = struct();

    % Helper: compute timing via xcorr (same logic as nrTimingEstimate core)
    % Returns offset and magnitude curve
    function [offset, mag] = timing_core(waveform, ref_waveform)
        [T, R] = size(waveform);
        [T_ref, P] = size(ref_waveform);
        T_eff = max(T, T_ref);
        if T < T_ref
            waveform = [waveform; zeros(T_ref - T, R)];
            T = T_ref;
        end
        mag_all = zeros(T_eff, R, P);
        for r = 1:R
            for p = 1:P
                refcorr = xcorr(waveform(:,r), ref_waveform(:,p));
                % Positive delay segment (delay 0 to T_eff-1)
                % MATLAB xcorr: length = T+T_ref-1, 1-based
                % Positive delay starts at index T (1-based) = T-1 (0-based)
                seg = abs(refcorr(T : T + T_eff - 1));
                mag_all(:, r, p) = seg;
            end
        end
        % Sum across ports, then across antennas
        mag = squeeze(sum(mag_all, 3));  % [T_eff, R]
        if size(mag, 2) > 1
            mag_sum = sum(mag, 2);
        else
            mag_sum = mag;
        end
        [~, peak_idx] = max(mag_sum);
        offset = peak_idx - 1;  % 0-based
        mag = mag_sum;
    end

    % Case 1: basic 1x1, offset = 2
    ref = [1; 0.5];
    waveform = [0; 0; 1; 0.5];
    [offset, mag] = timing_core(waveform, ref);
    cases.basic_offset2 = struct(...
        'waveform_real', real(waveform), 'waveform_imag', imag(waveform), ...
        'ref_real', real(ref), 'ref_imag', imag(ref), ...
        'offset', offset, 'mag', mag');

    % Case 2: longer waveform, offset = 5
    ref = [1; 0.7; 0.3];
    waveform = zeros(10, 1);
    waveform(6:8) = ref;
    [offset, mag] = timing_core(waveform, ref);
    cases.longer_offset5 = struct(...
        'waveform_real', real(waveform), 'waveform_imag', imag(waveform), ...
        'ref_real', real(ref), 'ref_imag', imag(ref), ...
        'offset', offset, 'mag', mag);

    % Case 3: complex signal, offset = 3
    ref = [1+0.1j; 0.5-0.2j];
    waveform = zeros(8, 1);
    waveform(4:5) = ref;
    [offset, mag] = timing_core(waveform, ref);
    cases.complex_offset3 = struct(...
        'waveform_real', real(waveform), 'waveform_imag', imag(waveform), ...
        'ref_real', real(ref), 'ref_imag', imag(ref), ...
        'offset', offset, 'mag', mag);

    % Case 4: 2 receive antennas, 1 port
    ref = [1; 0.6];
    waveform = zeros(7, 2);
    waveform(3:4, 1) = ref;
    waveform(3:4, 2) = 0.8 * ref;
    [offset, mag] = timing_core(waveform, ref);
    cases.multi_rx_2ant = struct(...
        'waveform_real', real(waveform), 'waveform_imag', imag(waveform), ...
        'ref_real', real(ref), 'ref_imag', imag(ref), ...
        'offset', offset, 'mag', mag);

    % Case 5: ref longer than waveform (T < T_ref)
    ref = [1; 0.8; 0.5; 0.3];
    waveform = [0; 1; 0.8];
    [offset, mag] = timing_core(waveform, ref);
    cases.ref_longer = struct(...
        'waveform_real', real(waveform), 'waveform_imag', imag(waveform), ...
        'ref_real', real(ref), 'ref_imag', imag(ref), ...
        'offset', offset, 'mag', mag);

    % Write JSON
    outfile = fullfile(outdir, 'nr_timing_estimate.json');
    fid = fopen(outfile, 'w');
    fprintf(fid, '%s', jsonencode(cases));
    fclose(fid);
    fprintf('Wrote %s (%d cases)\n', outfile, length(fieldnames(cases)));
end
