% SCI encoding and decoding across D2D/V2X resource formats.
root = fileparts(mfilename('fullpath'));
configs = {struct('NSLRB',50,'SidelinkMode','D2D','CyclicPrefixSL','Normal'), ...
           struct('NSLRB',25,'SidelinkMode','D2D','CyclicPrefixSL','Extended'), ...
           struct('NSLRB',50,'SidelinkMode','V2X','CyclicPrefixSL','Normal')};
records = {};
for k = 1:numel(configs)
    ue = configs{k};
    info = lteSCIInfo(ue);
    length_bits = info.Format0;
    if strcmp(ue.SidelinkMode,'V2X')
        length_bits = info.Format1;
    end
    bits = mod((0:length_bits-1)*7+k,2).';
    [coded,mcrc] = lteSCIEncode(ue,bits);
    [decoded,err,decoded_mcrc] = lteSCIDecode(length_bits,2*double(coded)-1);
    assert(isequal(decoded,bits) && err==0 && decoded_mcrc==mcrc);
    records{end+1} = struct('config',ue,'bits',bits.', ...
        'coded',coded.','mcrc',mcrc); %#ok<AGROW>
end
output = fullfile(root,'samples','lte_sci_coding.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
