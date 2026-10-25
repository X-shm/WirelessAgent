% BCH transport coding, partial receive decode, and single-port PBCH.
root = fileparts(mfilename('fullpath'));
records = {};
for cp = {'Normal','Extended'}
    for ports = [1 2 4]
        enb = struct('CellRefP',ports,'CyclicPrefix',cp{1},'NCellID',37);
        bits = mod((0:23)*7+ports,2).';
        coded = lteBCH(enb,bits);
        [decoded,detected] = lteBCHDecode(enb,2*double(coded)-1);
        assert(isequal(decoded,bits) && detected==ports);
        record = struct('cp',cp{1},'ports',ports,'bits',bits.', ...
            'coded',coded.','detected',detected);
        if ports==1
            symbols = ltePBCH(enb,coded);
            [soft,decoded_symbols,nfmod4,trblk,detected_ports] = ...
                ltePBCHDecode(enb,symbols);
            assert(isequal(trblk,bits) && detected_ports==1);
            record.pbch_real = real(symbols(:)).';
            record.pbch_imag = imag(symbols(:)).';
            record.pbch_soft = soft(:).';
            record.pbch_decoded_real = real(decoded_symbols(:)).';
            record.pbch_decoded_imag = imag(decoded_symbols(:)).';
            record.nfmod4 = nfmod4;
        end
        records{end+1} = record; %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_bch.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
