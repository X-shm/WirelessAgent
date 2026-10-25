% PUCCH format 1/2/3 reference sequences including format 2 ACK variants.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 25 50]
    for cellid = [0 37]
        for sf = [0 3]
            for cp = {'Normal','Extended'}
                ue = struct('NULRB',nrb,'NCellID',cellid,'NSubframe',sf, ...
                    'CyclicPrefixUL',cp{1});
                for resourceidx = [0 5]
                    chs = struct('ResourceIdx',resourceidx);
                    for format = 1:3
                        if format == 2
                            acks = {[],0,1,[0;1]};
                        else
                            acks = {[]};
                        end
                        for a = 1:numel(acks)
                            ack = acks{a};
                            if format == 2
                                [seq,info] = ltePUCCH2DRS(ue,chs,ack);
                            else
                                [seq,info] = feval(sprintf('ltePUCCH%dDRS',format),ue,chs);
                            end
                            records{end+1} = struct('entry',sprintf('ltePUCCH%dDRS',format), ...
                                'nrb',nrb,'ncellid',cellid,'nsubframe',sf, ...
                                'cyclic_prefix',cp{1},'resource_idx',resourceidx, ...
                                'ack',ack(:).','real',real(seq(:)).', ...
                                'imag',imag(seq(:)).','info',makeJsonSafe(info)); %#ok<AGROW>
                        end
                    end
                end
            end
        end
    end
end
output = fullfile(root,'samples','lte_pucch_drs.json');
fid = fopen(output,'w');
assert(fid > 0);
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
fprintf('cases %d\n',numel(records));

function value = makeJsonSafe(value)
    if isstruct(value)
        fields = fieldnames(value);
        for index = 1:numel(value)
            for field = 1:numel(fields)
                key = fields{field};
                value(index).(key) = makeJsonSafe(value(index).(key));
            end
        end
    elseif iscell(value)
        for index = 1:numel(value)
            value{index} = makeJsonSafe(value{index});
        end
    elseif isnumeric(value) && ~isreal(value)
        value = struct('real',real(value),'imag',imag(value));
    end
end
