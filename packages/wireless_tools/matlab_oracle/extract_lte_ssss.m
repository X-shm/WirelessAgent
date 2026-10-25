% Extract all R2026a secondary sidelink sync BPSK sequences for offline use.
root = fileparts(mfilename('fullpath'));
modes = {'D2D','V2X'};
binary = zeros(2,336,62,'uint8');
records = {};
for mode_index = 1:2
    for nslid = 0:335
        values = lteSSSS(struct('NSLID',nslid,'SidelinkMode',modes{mode_index}));
        assert(numel(values) == 124 && all(imag(values) == 0));
        assert(isequal(values(1:62),values(63:124)));
        assert(all(abs(real(values)) == 1));
        binary(mode_index,nslid+1,:) = uint8(real(values(1:62)) < 0);
        if ismember(nslid,[0 1 10 167 168 335])
            records{end+1} = struct('mode',modes{mode_index},'nslid',nslid, ...
                'real',real(values(:)).'); %#ok<AGROW>
        end
    end
end
output = fullfile(root,'..','tools','_lte_ssss_binary.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(binary));
fclose(fid);
sample = fullfile(root,'samples','lte_ssss.json');
fid = fopen(sample,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
