% Capture complete cell-specific SRS period/offset schedule in both modes.
root = fileparts(mfilename('fullpath'));
records = {};
for mode = {'FDD','TDD'}
    for config = 0:15
        ue = struct('DuplexMode',mode{1},'NSubframe',0);
        chs = struct('SubframeConfig',config);
        base = lteSRSInfo(ue,chs);
        scheduled = zeros(1,10);
        for subframe = 0:9
            ue.NSubframe = subframe;
            item = lteSRSInfo(ue,chs);
            assert(isequal(base.CellPeriod,item.CellPeriod));
            assert(isequal(base.CellOffset,item.CellOffset));
            scheduled(subframe+1) = item.IsSRSSubframe;
        end
        records{end+1} = struct('mode',mode{1},'config',config, ...
            'period',base.CellPeriod,'offset',base.CellOffset, ...
            'scheduled',scheduled); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_srs_info.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
