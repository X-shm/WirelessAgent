function gen_samples_lte_ofdm()
% Generate golden samples for lte_ofdm (lteOFDMInfo / lteOFDMModulate / lteOFDMDemodulate).
% Outputs: lte_ofdm_info_table.json (compiled-lib info for all NRB x CP),
%          lte_ofdm_samples.json (golden modulate/demodulate/info cases).
% Complex arrays are split into _real/_imag (jsonencode cannot carry complex).

% --- Full info table from compiled lteOFDMInfo ---
infoTab = {};
for cps = {'Normal', 'Extended'}
    for nrb = 6:110
        enb = struct('NDLRB', nrb, 'CyclicPrefix', cps{1});
        info = lteOFDMInfo(enb);
        infoTab{end+1} = struct('nrb', nrb, 'cp', cps{1}, ...
            'nfft', double(info.Nfft), 'windowing', double(info.Windowing), ...
            'samplingrate', double(info.SamplingRate), ...
            'cplengths', double(info.CyclicPrefixLengths));
    end
end
infoTab = cat(2, infoTab{:});
writeJSON('lte_ofdm_info_table.json', infoTab);
fprintf('Wrote lte_ofdm_info_table.json (%d entries)\n', numel(infoTab));

% --- Golden samples ---
samples = {};
samples{end+1} = mkInfo(6, 'Normal');
samples{end+1} = mkInfo(50, 'Normal');
samples{end+1} = mkInfo(100, 'Extended');

% modulate 6RB normal, 1 antenna, default windowing
rng(1);
enb = struct('NDLRB', 6, 'CyclicPrefix', 'Normal');
g = makeGrid(enb, 1);
wf = lteOFDMModulate(enb, g);
samples{end+1} = mkMod(enb, g, wf, [], 1);
% modulate 6RB normal, explicit windowing 8
wf2 = lteOFDMModulate(enb, g, 8);
samples{end+1} = mkMod(enb, g, wf2, 8, 1);
% modulate 15RB extended, 2 antennas, windowing 16
rng(2);
enb2 = struct('NDLRB', 15, 'CyclicPrefix', 'Extended');
g2 = makeGrid(enb2, 2);
wf3 = lteOFDMModulate(enb2, g2, 16);
samples{end+1} = mkMod(enb2, g2, wf3, 16, 1);
% modulate 6RB normal, 2 subframes (concatenation behavior)
rng(3);
g5 = makeGrid(enb, 1, 2);
wf6 = lteOFDMModulate(enb, g5);
samples{end+1} = mkMod(enb, g5, wf6, [], 2);
% demodulate 6RB normal, default cpFraction 0.55 (round trip of windowed signal)
rng(4);
g3 = makeGrid(enb, 1);
wf4 = lteOFDMModulate(enb, g3);
rg = lteOFDMDemodulate(enb, wf4);
samples{end+1} = mkDemod(enb, wf4, rg, []);
% demodulate 15RB extended, cpFraction 0.5 (clean windowing-0 waveform)
rng(5);
enb4 = struct('NDLRB', 15, 'CyclicPrefix', 'Extended');
g4 = makeGrid(enb4, 1);
wf5 = lteOFDMModulate(enb4, g4, 0);
rg2 = lteOFDMDemodulate(enb4, wf5, 0.5);
samples{end+1} = mkDemod(enb4, wf5, rg2, 0.5);

samples = cat(2, samples{:});
writeJSON('lte_ofdm_samples.json', samples);
fprintf('Wrote lte_ofdm_samples.json (%d samples)\n', numel(samples));
end

function s = mkInfo(nrb, cp)
enb = struct('NDLRB', nrb, 'CyclicPrefix', cp);
info = lteOFDMInfo(enb);
s = base(nrb, cp);
s.mode = 'info';
s.nfft = double(info.Nfft);
s.windowing = double(info.Windowing);
s.samplingrate = double(info.SamplingRate);
s.cplengths = double(info.CyclicPrefixLengths);
end

function s = mkMod(enb, grid, wf, windowing, nSubframes)
s = base(enb.NDLRB, enb.CyclicPrefix);
s.mode = 'modulate';
s.windowing = windowing;
s.subframes = nSubframes;
s.grid_real = real(grid); s.grid_imag = imag(grid);
s.waveform_real = real(wf); s.waveform_imag = imag(wf);
end

function s = mkDemod(enb, wf, rg, cpfraction)
s = base(enb.NDLRB, enb.CyclicPrefix);
s.mode = 'demodulate';
s.cpfraction = cpfraction;
s.waveform_real = real(wf); s.waveform_imag = imag(wf);
s.regrid_real = real(rg); s.regrid_imag = imag(rg);
end

function s = base(nrb, cp)
s = struct('mode', [], 'nrb', nrb, 'cp', cp, 'nfft', [], 'windowing', [], ...
    'samplingrate', [], 'cplengths', [], 'subframes', [], 'cpfraction', [], ...
    'grid_real', [], 'grid_imag', [], 'waveform_real', [], 'waveform_imag', [], ...
    'regrid_real', [], 'regrid_imag', []);
end

function g = makeGrid(enb, nAnts, nSubframes)
if nargin < 3, nSubframes = 1; end
nSC = enb.NDLRB * 12;
if strcmpi(enb.CyclicPrefix, 'Normal'), nSym = 14; else nSym = 12; end
bits = randi([0 1], nSC * nSym * nSubframes * nAnts * 2, 1);
sym = lteSymbolModulate(bits, 'QPSK');
g = reshape(sym, nSC, nSym * nSubframes, nAnts);
end

function writeJSON(fn, obj)
fid = fopen(wt_sample_path(fn), 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonencode(obj));
fclose(fid);
end
