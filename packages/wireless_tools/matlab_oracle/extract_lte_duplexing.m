% Independent R2026a FDD and normal-CP TDD SSC-0 duplexing information.
root = fileparts(mfilename('fullpath'));
configs = {struct('DuplexMode','FDD'),...
           struct('DuplexMode','FDD','CyclicPrefix','Extended'),...
           struct('DuplexMode','FDD','CyclicPrefixUL','Extended')};
records = {};
for k = 1:numel(configs)
    records{end+1} = struct('config',configs{k},...
        'info',lteDuplexingInfo(configs{k})); %#ok<AGROW>
end
for tdd_config = 0:6
    for nsubframe = 0:9
        enb = struct('DuplexMode','TDD','TDDConfig',tdd_config,...
                     'SSC',0,'NSubframe',nsubframe);
        records{end+1} = struct('config',enb,...
            'info',lteDuplexingInfo(enb)); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_duplexing.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
