% Golden samples for nrLayerMap
fprintf('start\n');
samples = [];
% 单码字映射到 1/2/4 层, 用固定数据避免 randi 崩溃
for nl = [1, 2, 4]
    n_sym = 12;
    in = (1:n_sym).' + 1j*((1:n_sym).' * 0.5);
    out = nrLayerMap(in, nl);
    s = struct();
    s.nLayers = nl;
    s.n_symbols = n_sym;
    s.in_real = real(in).';
    s.in_imag = imag(in).';
    s.out_real = real(out).';
    s.out_imag = imag(out).';
    s.out_rows = size(out,1);
    s.out_cols = size(out,2);
    samples = [samples; s];
    fprintf('  nLayers=%d: %d syms -> size [%d %d]\n', nl, n_sym, size(out,1), size(out,2));
end
jsonOut = jsonencode(samples);
fid = fopen(wt_sample_path('layermap_samples.json'), 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d layermap samples\n', numel(samples));
fprintf('done\n');
