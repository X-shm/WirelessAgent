% Independent R2026a LTE downlink control scrambling cases.
root = fileparts(mfilename('fullpath'));
names = {'ltePBCHPRBS','ltePDCCHPRBS','ltePCFICHPRBS','ltePHICHPRBS'};
records = {};
for k = 1:numel(names)
    for ncellid = [0 37]
        for nsubframe = [0 4]
            enb = struct('NCellID',ncellid,'NSubframe',nsubframe);
            fn = str2func(names{k});
            [sequence,cinit] = fn(enb,32);
            [window,~] = fn(enb,[7 19]);
            [signed,~] = fn(enb,12,'signed');
            records{end+1} = struct('entry',names{k},'ncellid',ncellid,...
                'nsubframe',nsubframe,'cinit',cinit,'bits',double(sequence(:)).',...
                'window',double(window(:)).','signed',double(signed(:)).'); %#ok<AGROW>
        end
    end
end
for nsubframe = [0 4]
    enb = struct('NSubframe',nsubframe);
    chs = struct('EPDCCHNID',37);
    [sequence,cinit] = lteEPDCCHPRBS(enb,chs,32);
    records{end+1} = struct('entry','lteEPDCCHPRBS','ncellid',37,...
        'nsubframe',nsubframe,'cinit',cinit,'bits',double(sequence(:)).',...
        'window',[],'signed',[]); %#ok<AGROW>
end
output = fullfile(root,'samples','lte_control_prbs.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
