% FDD NPRACH baseline resource configurations across formats and spacing.
root = fileparts(mfilename('fullpath'));
records = {};
for cellid = [0 37]
    for spacing = {'3.75kHz','15kHz'}
        for format = {'0','1','2'}
            ue = struct('NNCellID',cellid, ...
                'NBULSubcarrierSpacing',spacing{1},'DuplexMode','FDD');
            numsc = 12;
            if strcmp(format{1},'2')
                numsc = 36;
            end
            chs = struct('NPRACHFormat',format{1},'Periodicity',80, ...
                'SubcarrierOffset',0,'NumSubcarriers',numsc, ...
                'NRep',1,'StartTime',8,'NInit',0);
            try
                info = lteNPRACHInfo(ue,chs);
                records{end+1} = struct('cellid',cellid, ...
                    'spacing',spacing{1},'format',format{1},'info',info); %#ok<AGROW>
            catch
                % Some format/spacing combinations are not supported.
            end
        end
    end
end
assert(numel(records)>=4);
output = fullfile(root,'samples','lte_nprach_info.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
runtime = fullfile(root,'..','tools','_lte_nprach_info.json');
fid = fopen(runtime,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
