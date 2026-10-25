function gen_samples_comm_mil188()
% Rebuild exact MIL-STD-188 QAM constellation samples with MATLAB R2026a.
root = fileparts(fileparts(mfilename('fullpath')));
orders = [16 32 64 256];
sample = struct;
for order = orders
    values = mil188qammod((0:order-1)', order);
    key = ['M' num2str(order)];
    sample.(key) = struct('real', real(values).', 'imag', imag(values).');
end
path = fullfile(root, 'matlab_oracle', 'samples', 'comm_mil188_constellations.json');
file = fopen(path, 'w');
assert(file ~= -1, 'Unable to open constellation sample file');
cleanup = onCleanup(@() fclose(file));
fwrite(file, jsonencode(sample), 'char');
end
