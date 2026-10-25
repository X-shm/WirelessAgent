% Baseline PDSCH and EPDCCH DM-RS values/positions for one layer.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 25 50]
    for cellid = [0 37]
        for sf = [0 4]
            enb = struct('NDLRB',nrb,'NCellID',cellid, ...
                'NSubframe',sf,'CellRefP',1,'CyclicPrefix','Normal');
            for prb = {0,[2;3]}
                for rnti = [1 65535]
                    chs = struct('PRBSet',prb{1},'RNTI',rnti);
                    values = lteDMRS(enb,chs);
                    indices = lteDMRSIndices(enb,chs,{'1based','sub'});
                    records{end+1} = struct('entry','lteDMRS', ...
                        'nrb',nrb,'ncellid',cellid,'nsubframe',sf, ...
                        'prb_set',prb{1}(:).','rnti',rnti, ...
                        'real',real(values(:)).','imag',imag(values(:)).', ...
                        'indices',double(indices)); %#ok<AGROW>
                end
                for nid = [0 37]
                    chs = struct('EPDCCHPRBSet',prb{1},'RNTI',1, ...
                        'EPDCCHType','Localized','EPDCCHECCE',0, ...
                        'EPDCCHNID',nid);
                    values = lteEPDCCHDMRS(enb,chs);
                    indices = lteEPDCCHDMRSIndices(enb,chs,{'1based','sub'});
                    records{end+1} = struct('entry','lteEPDCCHDMRS', ...
                        'nrb',nrb,'ncellid',cellid,'nsubframe',sf, ...
                        'prb_set',prb{1}(:).','epdcch_nid',nid, ...
                        'real',real(values(:)).','imag',imag(values(:)).', ...
                        'indices',double(indices)); %#ok<AGROW>
                end
            end
        end
    end
end
output = fullfile(root,'samples','lte_dmrs.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
fprintf('cases %d\n',numel(records));
