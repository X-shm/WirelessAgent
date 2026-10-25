% Independent R2026a NB-IoT grid shapes for Python validation.
root = fileparts(mfilename('fullpath'));
cases = {struct('NBRefP',1), struct('NBRefP',2),...
         struct('NBULSubcarrierSpacing','15kHz'),...
         struct('NBULSubcarrierSpacing','3.75kHz')};
records = cell(1,numel(cases));
for k = 1:numel(cases)
    grid = lteNBResourceGrid(cases{k});
    records{k} = struct('config',cases{k},...
                        'shape',[size(grid,1),size(grid,2),size(grid,3)]);
end
output = fullfile(root,'samples','lte_nb_grid.json');
fid = fopen(output,'w');
fprintf(fid,'%s',jsonencode(records));
fclose(fid);
disp(output);
