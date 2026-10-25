% Independent R2026a resource-grid geometry for all three LTE links.
root = fileparts(mfilename('fullpath'));
names = {'DL','UL','SL'};
records = {};
for link = 1:numel(names)
    for nrb = [6 50]
        for cp = {'Normal','Extended'}
            for ports = [1 2]
                config = struct();
                if strcmp(names{link},'DL')
                    config.NDLRB = nrb;
                    config.CellRefP = ports;
                    config.CyclicPrefix = cp{1};
                elseif strcmp(names{link},'UL')
                    config.NULRB = nrb;
                    config.CyclicPrefixUL = cp{1};
                else
                    config.NSLRB = nrb;
                    config.CyclicPrefixSL = cp{1};
                end
                sizeFn = str2func(['lte' names{link} 'ResourceGridSize']);
                gridFn = str2func(['lte' names{link} 'ResourceGrid']);
                shape = sizeFn(config,ports);
                grid = gridFn(config,ports);
                records{end+1} = struct('link',names{link},'nrb',nrb,...
                    'cyclic_prefix',cp{1},'ports',ports,'shape',shape,...
                    'grid_shape',[size(grid,1),size(grid,2),size(grid,3)],...
                    'all_zero',all(grid(:)==0)); %#ok<AGROW>
            end
        end
    end
end
output = fullfile(root,'samples','lte_grid_sizes.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
