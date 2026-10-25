% Extract PDCCH quadruplet interleaver and inverse permutations.
root = fileparts(mfilename('fullpath'));
records = {};
for reg = [9 10 17 37 113 225]
    for cellid = [0 1 37 503]
        enb = struct('NCellID',cellid);
        data = (1:(4*reg)).';
        forward = ltePDCCHInterleave(enb,data);
        inverse = ltePDCCHDeinterleave(enb,forward);
        assert(isequal(inverse,data));
        records{end+1} = struct('reg',reg,'ncellid',cellid, ...
            'forward',double(forward(:)).'); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_pdcch_interleave.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
