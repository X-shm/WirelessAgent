function wt_nr_export_configs(output_path)
% Export constructor defaults once during development. Runtime uses JSON only.
root = fileparts(fileparts(mfilename('fullpath')));
signatures = jsondecode(fileread(fullfile(root,'references','5g_function_signatures.json')));
names = fieldnames(signatures);
defaults = struct();
failures = struct();
for i = 1:numel(names)
    name = names{i};
    if ~endsWith(name,'Config')
        continue;
    end
    try
        defaults.(name) = jsondecode(jsonencode(feval(name)));
    catch exception
        failures.(name) = exception.message;
    end
end
payload = struct('matlab_release',version('-release'),'defaults',defaults,'failures',failures);
fid = fopen(output_path,'w');
if fid < 0
    error('Cannot write %s',output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s',jsonencode(payload));
fprintf('Exported %d config defaults; %d failed\n',numel(fieldnames(defaults)),numel(fieldnames(failures)));
end
