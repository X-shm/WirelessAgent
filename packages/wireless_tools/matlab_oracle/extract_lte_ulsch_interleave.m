% Data-only UL-SCH multiplexing permutation across CP and modulation.
root = fileparts(mfilename('fullpath'));
records = {};
for cp = {'Normal','Extended'}
    for shortened = [0 1]
        for modulation = {'QPSK','16QAM'}
            ue = struct('CyclicPrefixUL',cp{1},'Shortened',shortened);
            chs = struct('Modulation',modulation{1},'NLayers',1);
            cols = 12 - (strcmp(cp{1},'Extended')*2) - shortened;
            qm = 2 + 2*strcmp(modulation{1},'16QAM');
            data = (1:(cols*qm*3)).';
            output = lteULSCHInterleave(ue,chs,data);
            recovered = lteULSCHDeinterleave(ue,chs,output);
            assert(isequal(recovered,data));
            records{end+1} = struct('cp',cp{1},'shortened',shortened, ...
                'modulation',modulation{1},'data',data.', ...
                'interleaved',output.'); %#ok<AGROW>
        end
    end
end
output = fullfile(root,'samples','lte_ulsch_interleave.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
