% Golden samples for nrCRCDecode (error check)
fprintf('start\n');
polys = {'6','11','16','24A','24B','24C'};
samples = [];
rng(6001);
for p = 1:numel(polys)
    poly = polys{p};
    % 生成随机数据, encode 后再 decode (应该 err=0)
    n = 20;
    data = randi([0 1], n, 1);
    enc = nrCRCEncode(data, poly);
    [dec_data, err] = nrCRCDecode(enc, poly);
    s = struct();
    s.poly = poly;
    s.input_bits = data';
    s.encoded_bits = enc';
    s.decoded_data = dec_data';
    s.crc_error = err;
    samples = [samples; s];
    fprintf('  %s: decode err=%d (data match=%d)\n', poly, err, isequal(dec_data, data));
end
jsonOut = jsonencode(samples);
fid = fopen(wt_sample_path('crc_decode_samples.json'), 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonOut);
fclose(fid);
fprintf('wrote %d crc_decode samples\n', numel(samples));
fprintf('done\n');
