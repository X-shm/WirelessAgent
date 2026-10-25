% EPDCCH data RE locations for localized/distributed baseline cells.
root = fileparts(mfilename('fullpath'));
records = {};
errors = {};
for nrb = [6 25 50]
    for cellid = [0 37]
        for sf = [0 4]
            for prb = {0,[2;3]}
                for cfi = [1 2 3]
                    enb = struct('NDLRB',nrb,'NCellID',cellid, ...
                        'NSubframe',sf,'CellRefP',1,'CyclicPrefix','Normal', ...
                        'CFI',cfi);
                    for type = {'Localized','Distributed'}
                        chs = struct('EPDCCHPRBSet',prb{1},'RNTI',1, ...
                            'EPDCCHType',type{1},'EPDCCHECCE',0, ...
                            'EPDCCHNID',0);
                        try
                            [indices,info] = lteEPDCCHIndices(enb,chs,{'1based','sub'});
                            records{end+1} = struct('nrb',nrb,'ncellid',cellid, ...
                                'nsubframe',sf,'prb_set',prb{1}(:).', ...
                                'cfi',cfi,'epdcch_type',type{1}, ...
                                'indices',double(indices),'info',info); %#ok<AGROW>
                        catch me
                            errors{end+1} = struct('nrb',nrb,'ncellid',cellid, ...
                                'nsubframe',sf,'prb_set',prb{1}(:).', ...
                                'cfi',cfi,'epdcch_type',type{1}, ...
                                'message',me.message); %#ok<AGROW>
                        end
                    end
                end
            end
        end
    end
end
output = fullfile(root,'samples','lte_epdcch_indices.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(struct('records',{records},'errors',{errors})));
fclose(fid);
disp(output);
fprintf('records %d errors %d\n',numel(records),numel(errors));
