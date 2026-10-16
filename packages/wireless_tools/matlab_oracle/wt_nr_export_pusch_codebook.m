function wt_nr_export_pusch_codebook(output_path)
% Export the finite R2026a PUSCH codebook for independent runtime lookup.
types = {'codebook1_ng1n4n1','codebook1_ng1n2n2','codebook2','codebook3','codebook4'};
records = {};
for nports = [1 2 4 8]
    if nports == 1
        max_tpmi = 0;
    elseif nports == 2
        max_tpmi = 5;
    elseif nports == 4
        max_tpmi = 27;
    else
        max_tpmi = 304;
    end
    if nports == 8
        current_types = types;
    else
        current_types = {'default'};
    end
    for nlayers = 1:nports
        for transform = 0:1
            for type_index = 1:numel(current_types)
                current_type = current_types{type_index};
                for tpmi = 0:max_tpmi
                    try
                        if nports == 8
                            w = nrPUSCHCodebook(nlayers,nports,tpmi,logical(transform),current_type);
                        else
                            w = nrPUSCHCodebook(nlayers,nports,tpmi,logical(transform));
                        end
                        entry = struct('n_layers',nlayers,'n_ports',nports,...
                            'tpmi',tpmi,'transform_precode',logical(transform),...
                            'codebook_type',current_type,'real',real(w),'imag',imag(w));
                        records{end+1} = entry; %#ok<AGROW>
                    catch
                        % Invalid standardized combinations are omitted.
                    end
                end
            end
        end
    end
end
payload = struct('matlab_release',version('-release'),'entries',{records});
fid = fopen(output_path,'w');
if fid < 0
    error('Cannot write %s',output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s',jsonencode(payload));
fprintf('Exported %d valid PUSCH codebook matrices\n',numel(records));
end
