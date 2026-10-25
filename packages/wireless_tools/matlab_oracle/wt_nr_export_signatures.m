function wt_nr_export_signatures(outputPath)
%WT_NR_EXPORT_SIGNATURES Record short local help summaries for agent discovery.
root = fileparts(fileparts(mfilename('fullpath')));
inventory = jsondecode(fileread(fullfile(root, 'references', 'function_inventory.json')));
productKey = matlab.lang.makeValidName('5G Toolbox');
names = string({inventory.products.(productKey).functions.matlab_name});
entries = struct();
for k = 1:numel(names)
    name = names(k);
    description = string(help(char(name)));
    lines = splitlines(description);
    summary = "";
    signatures = strings(0);
    for j = 1:numel(lines)
        line = strtrim(lines(j));
        if summary == "" && startsWith(line, name + " -")
            summary = strtrim(extractAfter(line, name + " -"));
        end
        if contains(line, name + "(") && strlength(line) <= 240 && ...
                ~contains(line, 'http') && numel(signatures) < 3
            signatures(end + 1) = line; %#ok<AGROW>
        end
    end
    entries.(char(name)) = struct('summary', char(summary), ...
        'signatures', {cellstr(unique(signatures, 'stable'))});
end
fid = fopen(outputPath, 'w', 'n', 'UTF-8');
assert(fid >= 0, 'Cannot open signature output file');
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, '%s', jsonencode(entries));
end
