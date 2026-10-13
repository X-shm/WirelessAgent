%% test_ldpc.m
% Minimal LDPC test with correct nrLDPCEncode signature.
fprintf('start\n');
try
    zc = 16;
    K = 22*zc;
    in = randi([0 1], K, 1);
    fprintf('input ready K=%d\n', K);
    out = nrLDPCEncode(in, 1);   % BG1
    fprintf('encoded, n=%d type=%s\n', numel(out), class(out));
    sys_ok = isequal(out(1:K), in);
    fprintf('systematic bits match input: %d\n', sys_ok);
    % Decode: nrLDPCDecode(LLR, bgn, maxnumiter)
    LLR = 1 - 2*double(out);
    dec = nrLDPCDecode(LLR, 1, 10);
    fprintf('decoded, err=%d\n', sum(dec ~= in));
catch e
    fprintf('ERROR: %s\n', e.message);
    fprintf('ID: %s\n', e.identifier);
    for k=1:numel(e.stack)
        fprintf('  at %s line %d\n', e.stack(k).name, e.stack(k).line);
    end
end
fprintf('done\n');
