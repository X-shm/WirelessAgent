% PDCCH DCI CRC, tail-biting encoding and rate matching oracle.
root = fileparts(mfilename('fullpath'));
records = {};
for format = 0:3
    for rnti = [0 1 4660]
        ue = struct('PDCCHFormat',format,'RNTI',rnti);
        bits = mod((0:31)*7+format+rnti,2).';
        [coded,mcrc] = lteDCIEncode(ue,bits);
        crc_bits = lteCRCEncode(bits,'16',rnti);
        conv = lteConvolutionalEncode(crc_bits);
        matched = lteRateMatchConvolutional(conv,length(coded));
        assert(isequal(matched,coded));
        [decoded,crc_rnti,decoded_mcrc] = lteDCIDecode(length(bits), ...
            2*double(coded)-1);
        assert(isequal(decoded,bits) && crc_rnti==rnti && decoded_mcrc==mcrc);
        records{end+1} = struct('format',format,'rnti',rnti, ...
            'bits',bits.','coded',coded.','mcrc',mcrc, ...
            'conv',conv.','crc_rnti',crc_rnti); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_dci_coding.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
