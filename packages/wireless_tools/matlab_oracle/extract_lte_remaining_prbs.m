% Independent R2026a Sidelink and PUCCH PRBS cases.
root = fileparts(mfilename('fullpath'));
records = {};
configs = {struct('NSLID',0),struct('NSLID',170)};
for k = 1:numel(configs)
    [bits,cinit] = ltePSBCHPRBS(configs{k},32);
    [signed,~] = ltePSBCHPRBS(configs{k},12,'signed');
    records{end+1} = struct('entry','ltePSBCHPRBS','config',configs{k},...
        'cinit',cinit,'bits',double(bits(:)).','signed',double(signed(:)).'); %#ok<AGROW>
end
[bits,cinit] = ltePSCCHPRBS(32);
[signed,~] = ltePSCCHPRBS(12,'signed');
records{end+1} = struct('entry','ltePSCCHPRBS','config',struct(),...
    'cinit',cinit,'bits',double(bits(:)).','signed',double(signed(:)).');
configs = {struct('NSAID',1,'NSubframePSSCH',0),...
           struct('NSAID',255,'NSubframePSSCH',9),...
           struct('SidelinkMode','V2X','NXID',12345,'NSubframePSSCH',4)};
for k = 1:numel(configs)
    [bits,cinit] = ltePSSCHPRBS(configs{k},32);
    [signed,~] = ltePSSCHPRBS(configs{k},12,'signed');
    records{end+1} = struct('entry','ltePSSCHPRBS','config',configs{k},...
        'cinit',cinit,'bits',double(bits(:)).','signed',double(signed(:)).'); %#ok<AGROW>
end
configs = {struct('NCellID',1,'NSubframe',0,'RNTI',1),...
           struct('NCellID',37,'NSubframe',4,'RNTI',100)};
for k = 1:numel(configs)
    for name = {'ltePUCCH2PRBS','ltePUCCH3PRBS'}
        fn = str2func(name{1});
        [bits,cinit] = fn(configs{k},32);
        [signed,~] = fn(configs{k},12,'signed');
        records{end+1} = struct('entry',name{1},'config',configs{k},...
            'cinit',cinit,'bits',double(bits(:)).','signed',double(signed(:)).'); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_remaining_prbs.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
