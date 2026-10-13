%% gen_samples_polar.m
% Golden samples for nrPolarEncode. 3GPP TS 38.212 §5.3.1
fprintf('start\n');
samples = [];
rng_base = 3001;

% Downlink: nMax=9, iIL=true. Uplink: nMax=10, iIL=false.
configs = {9, true; 10, false};
params = [32, 64; 40, 80; 56, 112; 64, 128];

for c = 1:size(configs,1)
    nmax = configs{c,1};
    iil = configs{c,2};
    mode = 'DL'; if ~iil, mode = 'UL'; end
    for p = 1:size(params,1)
        K = params(p,1); E = params(p,2);
        rng(rng_base); rng_base = rng_base + 1;
        in = randi([0 1], K, 1);
        try
            enc = nrPolarEncode(in, E, nmax, iil);
            s = struct();
            s.mode = mode; s.nmax = nmax; s.iil = iil;
            s.K = K; s.E = E; s.N = numel(enc);
            s.input_bits = in';
            s.output_bits = enc';
            samples = [samples; s];
            fprintf('  %s K=%d E=%d N=%d \n', mode, K, E, numel(enc));
        catch e
            fprintf('  %s K=%d E=%d ERROR: %s\n', mode, K, E, e.message);
        end
    end
end

jsonOut = jsonencode(samples);
outpath = wt_sample_path('polar_samples.json');
fid = fopen(outpath, 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d Polar samples\n', numel(samples));
fprintf('done\n');
