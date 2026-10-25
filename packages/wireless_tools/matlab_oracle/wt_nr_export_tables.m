function wt_nr_export_tables(output_path)
% Export the two static NR lookup-table families during development.
payload = struct();
payload.matlab_release = version('-release');
payload.cqi = jsondecode(jsonencode(nrCQITables));
payload.pusch = jsondecode(jsonencode(nrPUSCHMCSTables));
fid = fopen(output_path,'w');
if fid < 0
    error('Cannot write %s',output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s',jsonencode(payload));
end
