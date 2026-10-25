% Sidelink SC-FDMA information, modulation and demodulation oracle.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 25 50]
    for cp = {'Normal','Extended'}
        ue = struct('NSLRB',nrb,'CyclicPrefixSL',cp{1});
        info = lteSLSCFDMAInfo(ue);
        ue.Windowing = 0;
        symbols = 14 - 2*strcmp(cp{1},'Extended');
        grid = complex(zeros(12*nrb,symbols));
        grid(1,1) = 1+1i;
        grid(10,5) = -0.5+0.25i;
        [waveform,modinfo] = lteSLSCFDMAModulate(ue,grid);
        recovered = lteSLSCFDMADemodulate(ue,waveform);
        assert(max(abs(recovered(:)-grid(:))) < 1e-9);
        records{end+1} = struct('nrb',nrb,'cp',cp{1}, ...
            'info',info,'modinfo',modinfo,'waveform_length',length(waveform), ...
            'first_real',real(waveform(1:64)).', ...
            'first_imag',imag(waveform(1:64)).'); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_sl_scfdma.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
