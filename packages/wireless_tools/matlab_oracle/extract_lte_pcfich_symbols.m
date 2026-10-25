% Independent R2026a single-port PCFICH symbols and soft decoder cases.
root = fileparts(mfilename('fullpath'));
records = {};
for ncellid = [0 37]
    for nsubframe = [0 4]
        enb = struct('NCellID',ncellid,'NSubframe',nsubframe,'CellRefP',1);
        for cfi = 1:3
            cw = lteCFI(struct('CFI',cfi));
            symbols = ltePCFICH(enb,cw);
            soft = ltePCFICHDecode(enb,symbols);
            records{end+1} = struct('ncellid',ncellid,...
                'nsubframe',nsubframe,'cfi',cfi,'coded',double(cw(:)).',...
                'real',real(symbols(:)).','imag',imag(symbols(:)).',...
                'soft',double(soft(:)).'); %#ok<AGROW>
        end
    end
end
output = fullfile(root,'samples','lte_pcfich_symbols.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
