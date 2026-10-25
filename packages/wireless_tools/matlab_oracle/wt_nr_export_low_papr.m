function wt_nr_export_low_papr(output_path)
% Capture the short type-1 low-PAPR phase tables for standalone runtime use.
payload = struct();
payload.matlab_release = version('-release');
for m = [6 12 18 24]
    phases = zeros(30,m);
    for u = 0:29
        sequence = nrLowPAPRS(u,0,0,m);
        phases(u+1,:) = round(angle(sequence(:).')*4/pi);
    end
    payload.(sprintf('m%d',m)) = phases;
end
fid = fopen(output_path,'w');
if fid < 0
    error('Cannot write %s',output_path);
end
cleanup = onCleanup(@() fclose(fid));
fprintf(fid,'%s',jsonencode(payload));
end
