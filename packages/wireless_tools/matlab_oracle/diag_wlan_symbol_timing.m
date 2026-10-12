function diag_wlan_symbol_timing
% Instrument wlanSymbolTimingEstimate internals to compare against the Python
% reimplementation. Results written to diag_out.txt.

    script_dir = fileparts(mfilename('fullpath'));
    addpath(script_dir);
    out = fullfile(script_dir, 'diag_out.txt');
    fid = fopen(out, 'w');
    samples = jsondecode(fileread(fullfile(script_dir, 'samples', 'wlan_symbol_timing.json')));

    for key = {'timing_clean_cbw20','timing_delay_cbw20','timing_cbw40'}
        s = samples.(key{1});
        x = s.waveform_real + 1j*s.waveform_imag;
        chanbw = s.chanbw; threshold = s.threshold;

        fprintf(fid, '\n===== %s =====\n', key{1});
        fprintf(fid, '  Ns=%d  chanbw=%s  threshold=%g\n', size(x,1), chanbw, threshold);

        LLTF = wlan.internal.legacyLTF(chanbw,1);
        L = size(LLTF,1);
        fs = 1e6*wlan.internal.cbwStr2Num(chanbw);
        deltaCSD = round(200e-9*fs);
        fprintf(fid, '  L(L-LTF)=%d  deltaCSD=%d\n', L, deltaCSD);

        corr = filter(conj(flipud(LLTF(:,1))),1,x);
        M = sum(abs(corr(L:end,:)).^2,2);
        [Mmax, nInitial] = max(M);
        nInitial0 = nInitial - 1;   % 0-based
        fprintf(fid, '  max(M)=%.9f  at nInitial=%d (0-based)\n', Mmax, nInitial0);

        nplate = sum(M >= Mmax*(1-1e-12));
        fprintf(fid, '  samples where M==Mmax (plateau width) = %d\n', nplate);

        if (nInitial + deltaCSD) > length(M)
            idx = find(M(nInitial:end) >= threshold*Mmax,1,'last');
        else
            idx = find(M(nInitial:nInitial+deltaCSD) >= threshold*Mmax,1,'last');
        end
        nMax = nInitial + (idx-1);
        fprintf(fid, '  idx=%d  nMax=%d  startOffset=nMax-L-1=%d\n', idx, nMax, nMax-L-1);
        fprintf(fid, '  golden start_offset = %d\n', s.start_offset);

        % Python-equivalent naive start = nInitial - L
        fprintf(fid, '  naive nInitial - L = %d\n', nInitial0 - L);
    end
    fclose(fid);
    fprintf('Wrote %s\n', out);
end
