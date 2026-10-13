% Golden samples for nrCodeBlockSegmentLDPC
fprintf('start\n');
samples = [];
rng(7001);
configs = {1, 3000; 1, 5000; 2, 3000; 2, 5000};
for c = 1:size(configs,1)
    bgn = configs{c,1};
    blklen = configs{c,2};
    blk = randi([0 1], blklen, 1);
    cbs = nrCodeBlockSegmentLDPC(blk, bgn);
    s = struct();
    s.bgn = bgn;
    s.blk_len = blklen;
    s.n_cbs = size(cbs, 2);
    s.cb_size = size(cbs, 1);
    % 存每个码块的前 10 位做校验
    s.cbs_preview = cbs(1:min(10,size(cbs,1)), :)';
    s.input_bits = blk(1:min(20,blklen))';
    samples = [samples; s];
    fprintf('  bgn=%d blklen=%d -> %d cbs of size %d\n', bgn, blklen, size(cbs,2), size(cbs,1));
end
jsonOut = jsonencode(samples);
fid = fopen(wt_sample_path('cbs_samples.json'), 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d cbs samples\n', numel(samples));
fprintf('done\n');
