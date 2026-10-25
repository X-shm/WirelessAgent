% Independent R2026a sidelink broadcast-channel resource positions.
root = fileparts(mfilename('fullpath'));
records = {};
for nrb = [6 50]
    for mode = {'D2D','V2X'}
        for cp = {'Normal','Extended'}
            ue = struct('NSLRB',nrb,'SidelinkMode',mode{1},...
                        'CyclicPrefixSL',cp{1});
            try
                positions = ltePSBCHIndices(ue,{'1based','sub'});
                records{end+1} = struct('nrb',nrb,'mode',mode{1},...
                    'cyclic_prefix',cp{1},'indices',double(positions)); %#ok<AGROW>
            catch
                % Extended V2X is unsupported by MATLAB.
            end
        end
    end
end
output = fullfile(root,'samples','lte_psbch_indices.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
