% Exhaustive LTE uplink PUSCH codebook and inverse-reference extraction.
root = fileparts(mfilename('fullpath'));
records = {};
for antennas = [1 2 4]
    for layers = 1:antennas
        info = lteULPMIInfo(struct('NULRB',25,'NTxAnts',antennas), ...
                            struct('NLayers',layers));
        for pmi = 0:info.MaxPMI
            matrix = ltePUSCHPrecode(eye(layers),antennas,pmi);
            recovered = ltePUSCHDeprecode(matrix,layers,pmi);
            assert(max(abs(recovered(:)-reshape(eye(layers),[],1))) < 1e-9);
            records{end+1} = struct('antennas',antennas,'layers',layers, ...
                'pmi',pmi,'max_pmi',info.MaxPMI, ...
                'matrix_real',real(matrix),'matrix_imag',imag(matrix)); %#ok<AGROW>
        end
    end
end
output = fullfile(root,'samples','lte_pusch_codebook.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
runtime = fullfile(root,'..','tools','_lte_pusch_codebook.json');
fid = fopen(runtime,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
