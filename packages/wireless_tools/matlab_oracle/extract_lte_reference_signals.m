% Baseline CSI-RS and PRS values/indices in FDD normal-CP subframes.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 25 50]
    for cellid = [0 37 503]
        for sf = [1 2 6]
            for refp = [1 2 4 8]
                enb = struct('NDLRB',nrb,'NCellID',cellid,'CellRefP',1, ...
                    'NSubframe',sf,'CyclicPrefix','Normal', ...
                    'CSIRSConfig',0,'CSIRefP',refp,'CSIRSPeriod','On');
                values = lteCSIRS(enb);
                positions = lteCSIRSIndices(enb,{'1based','sub'});
                records{end+1} = struct('entry','lteCSIRS','nrb',nrb, ...
                    'ncellid',cellid,'nsubframe',sf,'csi_ref_ports',refp, ...
                    'real',real(values(:)).','imag',imag(values(:)).', ...
                    'indices',double(positions)); %#ok<AGROW>
            end
        end
        for sf = [0 4 9]
            enb = struct('NDLRB',nrb,'NCellID',cellid,'CellRefP',1, ...
                'NSubframe',sf,'CyclicPrefix','Normal','NPRSRB',nrb);
            values = ltePRS(enb);
            positions = ltePRSIndices(enb,{'1based','sub'});
            records{end+1} = struct('entry','ltePRS','nrb',nrb, ...
                'ncellid',cellid,'nsubframe',sf, ...
                'real',real(values(:)).','imag',imag(values(:)).', ...
                'indices',double(positions)); %#ok<AGROW>
        end
    end
end
output = fullfile(root,'samples','lte_reference_signals.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
fprintf('cases %d\n',numel(records));
