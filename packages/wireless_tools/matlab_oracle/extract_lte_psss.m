% Independent R2026a primary sidelink synchronization sequences/indices.
root = fileparts(mfilename('fullpath'));
records = {};
for nslid = [0 167 168 335]
    values = ltePSSS(struct('NSLID',nslid));
    records{end+1} = struct('kind','sequence','nslid',nslid,...
        'real',real(values(:)).','imag',imag(values(:)).'); %#ok<AGROW>
end
for nrb = [6 50]
    for cp = {'Normal','Extended'}
        ue = struct('NSLRB',nrb,'CyclicPrefixSL',cp{1});
        positions = ltePSSSIndices(ue,{'1based','sub'});
        records{end+1} = struct('kind','indices','nrb',nrb,...
            'cyclic_prefix',cp{1},'indices',double(positions)); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_psss.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
