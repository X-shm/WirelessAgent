% Baseline single-antenna PUCCH format 1/2/3 data and DRS allocations.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 25 50]
    for cellid = [0 37]
        for sf = [0 3]
            for cp = {'Normal','Extended'}
                ue = struct('NULRB',nrb,'NCellID',cellid,'NSubframe',sf, ...
                    'CyclicPrefixUL',cp{1});
                for resourceidx = [0 5 17]
                    chs = struct('ResourceIdx',resourceidx);
                    for format = 1:3
                        for drs = [false true]
                            name = sprintf('ltePUCCH%d%sIndices',format, ...
                                repmat('DRS',1,drs));
                            indices = feval(name,ue,chs,{'1based','sub'});
                            records{end+1} = struct('entry',name,'nrb',nrb, ...
                                'ncellid',cellid,'nsubframe',sf,'cyclic_prefix',cp{1}, ...
                                'resource_idx',resourceidx, ...
                                'indices',double(indices)); %#ok<AGROW>
                        end
                    end
                end
            end
        end
    end
end
output = fullfile(root,'samples','lte_pucch_indices.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
fprintf('cases %d\n',numel(records));
