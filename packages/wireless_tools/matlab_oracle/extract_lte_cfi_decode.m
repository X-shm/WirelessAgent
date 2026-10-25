% Independent R2026a soft CFI decoder cases.
root = fileparts(mfilename('fullpath'));
records = {};
for cfi = 1:3
    cw = double(lteCFI(struct('CFI',cfi)));
    for count = [8 32 48]
        repeated = repmat(cw,ceil(count/32),1);
        soft = repeated(1:count) + 0.35*sin((1:count)'*0.7);
        records{end+1} = struct('soft',soft.','decoded',...
            lteCFIDecode(soft)); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_cfi_decode.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
