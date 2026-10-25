%% Reproducible MATLAB R2026a Update 3 samples for selected NR subsets.
% The Python tools never invoke MATLAB; this script is an optional oracle.

sample_dir = wt_sample_dir();
samples = struct();
samples.matlab_release = version('-release');

bch_cases = repmat(struct('payload', [], 'sfn', 0, 'hrf', 0, ...
    'lssb', 0, 'idxoffset', 0, 'ncellid', 0, 'codeword', []), 1, 2);
bch_cases(1).payload = mod((0:23)', 2);
bch_cases(1).sfn = 42;
bch_cases(1).hrf = 1;
bch_cases(1).lssb = 4;
bch_cases(1).idxoffset = 17;
bch_cases(1).ncellid = 321;
bch_cases(2).payload = mod((1:24)', 2);
bch_cases(2).sfn = 1023;
bch_cases(2).hrf = 0;
bch_cases(2).lssb = 64;
bch_cases(2).idxoffset = 37;
bch_cases(2).ncellid = 1007;
for ii = 1:numel(bch_cases)
    c = bch_cases(ii);
    bch_cases(ii).codeword = nrBCH(c.payload, c.sfn, c.hrf, ...
        c.lssb, c.idxoffset, c.ncellid);
end
samples.bch = bch_cases;

uci_cases = repmat(struct('payload', [], 'e', 0, 'codeword', []), 1, 2);
uci_cases(1).payload = mod((0:11)', 2);
uci_cases(1).e = 108;
uci_cases(2).payload = mod((0:19)', 2);
uci_cases(2).e = 256;
for ii = 1:numel(uci_cases)
    c = uci_cases(ii);
    uci_cases(ii).codeword = nrUCIEncode(c.payload, c.e);
end
samples.uci = uci_cases;

lossconf = nrPathLossConfig;
lossconf.Scenario = 'UMa';
bs = [0; 0; 30];
ue = [100; 0; 1.5];
frequency = 3.5e9;
[loss, sigma] = nrPathLoss(lossconf, frequency, true, bs, ue);
samples.uma_los = struct('freq_hz', frequency, 'bs', bs, 'ue', ue, ...
    'pathloss_db', loss, 'shadow_fading_std_db', sigma);

pucch_cases = repmat(struct('ack', [], 'slot', 0, ...
    'symbols_real', [], 'symbols_imag', []), 1, 3);
for ii = 1:3
    if ii == 1
        ack = 0;
    elseif ii == 2
        ack = [0; 1];
    else
        ack = [1; 0];
    end
    slot = double(ii == 3);
    pucch = nrPUCCH1(ack, 0, [0 4], 'normal', slot, 7, ...
        'neither', 0, 'disabled', 0);
    pucch_cases(ii).ack = ack;
    pucch_cases(ii).slot = slot;
    pucch_cases(ii).symbols_real = real(pucch);
    pucch_cases(ii).symbols_imag = imag(pucch);
end
samples.pucch1 = pucch_cases;

target = fullfile(sample_dir, 'nr_remaining_oracle.json');
fid = fopen(target, 'w', 'n', 'UTF-8');
if fid == -1
    error('wireless_toolbox:SampleWrite', 'Cannot open %s', target);
end
cleaner = onCleanup(@() fclose(fid));
fwrite(fid, jsonencode(samples), 'char');
fprintf('Wrote %s\n', target);
