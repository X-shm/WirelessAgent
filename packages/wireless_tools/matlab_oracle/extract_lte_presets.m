% Finite R2026a LTE RMC and E-TM preset configurations.
root = fileparts(mfilename('fullpath'));
downlink = arrayfun(@(n)sprintf('R.%d',n),[0:14 25:28 43:45 48 50 51], ...
    'UniformOutput',false);
downlink = [downlink {'R.31-3A','R.31-4','R.45-1','R.68-1','R.105', ...
    'R.12-9RB','R.6-27RB','R.11-45RB'}];
uplink = {'A1-1','A1-2','A1-3','A1-4','A1-5','A2-1','A2-2','A2-3', ...
    'A3-1','A3-2','A3-3','A3-4','A3-5','A3-6','A3-7', ...
    'A4-1','A4-2','A4-3','A4-4','A4-5','A4-6','A4-7','A4-8', ...
    'A5-1','A5-2','A5-3','A5-4','A5-5','A5-6','A5-7', ...
    'A7-1','A7-2','A7-3','A7-4','A7-5','A7-6', ...
    'A8-1','A8-2','A8-3','A8-4','A8-5','A8-6', ...
    'A11-1','A3-2-9RB','A4-3-9RB'};
models = {'1.1','1.2','2','2a','2b','3.1','3.1a','3.1b','3.2','3.3'};
bandwidths = {'1.4MHz','3MHz','5MHz','10MHz','15MHz','20MHz', ...
    '9RB','11RB','27RB','45RB','64RB','91RB'};
records = {};
errors = {};
for mode = {'FDD','TDD'}
    duplex = mode{1};
    for j = 1:numel(downlink)
        try
            cfg = lteRMCDL(downlink{j},duplex,10);
            records{end+1} = struct('entry','lteRMCDL','name',downlink{j}, ...
                'duplex',duplex,'config',cfg); %#ok<AGROW>
        catch me
            errors{end+1} = struct('entry','lteRMCDL','name',downlink{j}, ...
                'duplex',duplex,'message',me.message); %#ok<AGROW>
        end
    end
    for j = 1:numel(uplink)
        try
            cfg = lteRMCUL(uplink{j},duplex,10);
            records{end+1} = struct('entry','lteRMCUL','name',uplink{j}, ...
                'duplex',duplex,'config',cfg); %#ok<AGROW>
        catch me
            errors{end+1} = struct('entry','lteRMCUL','name',uplink{j}, ...
                'duplex',duplex,'message',me.message); %#ok<AGROW>
        end
    end
    for j = 1:numel(models)
        for k = 1:numel(bandwidths)
            cellid = 1;
            if contains(bandwidths{k},'RB')
                cellid = 10;
            end
            try
                cfg = lteTestModel(models{j},bandwidths{k},cellid,duplex);
                records{end+1} = struct('entry','lteTestModel','name',models{j}, ...
                    'bandwidth',bandwidths{k},'duplex',duplex, ...
                    'ncellid',cellid,'config',cfg); %#ok<AGROW>
            catch me
                errors{end+1} = struct('entry','lteTestModel','name',models{j}, ...
                    'bandwidth',bandwidths{k},'duplex',duplex, ...
                    'message',me.message); %#ok<AGROW>
            end
        end
    end
end
output = fullfile(root,'samples','lte_presets.json');
for j = 1:numel(records)
    records{j}.config = makeJsonSafe(records{j}.config);
end
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(struct('records',{records},'errors',{errors})));
fclose(fid);
disp(output);
fprintf('records %d errors %d\n',numel(records),numel(errors));

function value = makeJsonSafe(value)
    if isstruct(value)
        fields = fieldnames(value);
        for index = 1:numel(value)
            for field = 1:numel(fields)
                key = fields{field};
                value(index).(key) = makeJsonSafe(value(index).(key));
            end
        end
    elseif iscell(value)
        for index = 1:numel(value)
            value{index} = makeJsonSafe(value{index});
        end
    elseif isnumeric(value) && ~isreal(value)
        value = struct('real',real(value),'imag',imag(value));
    end
end
