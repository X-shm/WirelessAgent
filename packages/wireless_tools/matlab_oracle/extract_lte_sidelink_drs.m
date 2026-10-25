% Sidelink DRS symbol cases across PSBCH, PSCCH, PSSCH and D2D/V2X.
root = fileparts(mfilename('fullpath'));
records = {};
psbch = cell(1,336);
for id = 0:335
    psbch{id+1} = struct('NSLID',id);
end
pscch = {struct('NSLRB',15,'PRBSet',5,'SidelinkMode','D2D'), ...
         struct('NSLRB',50,'PRBSet',13,'SidelinkMode','D2D', ...
                'CyclicPrefixSL','Extended'), ...
         struct('NSLRB',50,'PRBSet',[5;6],'SidelinkMode','V2X')};
pssch = {struct('NSLRB',50,'PRBSet',[30;31],'SidelinkMode','D2D', ...
                'NSAID',37,'NSubframePSSCH',0), ...
         struct('NSLRB',15,'PRBSet',[3;4],'SidelinkMode','D2D', ...
                'CyclicPrefixSL','Extended','NSAID',255,'NSubframePSSCH',7), ...
         struct('NSLRB',50,'PRBSet',[30;31],'SidelinkMode','V2X', ...
                'NXID',513,'NSubframePSSCH',3)};
names = {'ltePSBCHDRS','ltePSCCHDRS','ltePSSCHDRS'};
configs = {psbch,pscch,pssch};
for e = 1:numel(names)
    for k = 1:numel(configs{e})
        ue = configs{e}{k};
        [symbols,info] = feval(names{e},ue);
        records{end+1} = struct('entry',names{e},'config',ue, ...
            'real',real(symbols(:)).','imag',imag(symbols(:)).', ...
            'info',info); %#ok<AGROW>
    end
end
output = fullfile(root,'samples','lte_sidelink_drs.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
