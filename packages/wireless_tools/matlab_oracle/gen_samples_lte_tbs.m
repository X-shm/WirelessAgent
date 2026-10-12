function gen_samples_lte_tbs()
% Generate golden tables + samples for lte_tbs (lteTBS, TS 36.213 Table 7.1.7.2.1-1).
% Outputs: lte_tbs_tables.json (full 4-layer tables), lte_tbs_samples.json.
% The base table lives in MATLAB's compiled mwltelibrary, so dump it here.

% --- Full tables: rows = NPRB (1..110), cols = ITBS (0..37) ---
T = cell(4, 1);
for L = 1:4
    tab = zeros(110, 38);
    for n = 1:110
        if L == 1
            tab(n, :) = lteTBS(n).';
        else
            tab(n, :) = lteTBS(n, 0:37, L).';
        end
    end
    T{L} = tab;
end

tblOut = struct('nprb', 1:110, 'itbs', 0:37, ...
    'tbs1', T{1}, 'tbs2', T{2}, 'tbs3', T{3}, 'tbs4', T{4});
fid = fopen(wt_sample_path('lte_tbs_tables.json'), 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonencode(tblOut));
fclose(fid);
fprintf('Wrote lte_tbs_tables.json\n');

% --- Golden samples ---
samples = {};
samples{end+1} = mk('nprb', 1, [], 1, T{1}(1, :));
samples{end+1} = mk('nprb', 50, [], 1, T{1}(50, :));
samples{end+1} = mk('nprb', 110, [], 1, T{1}(110, :));
samples{end+1} = mk('nprb_itbs', 1, [0 5 10 20 30 37], 1, T{1}(1, [1 6 11 21 31 38]));
samples{end+1} = mk('nprb_itbs', 6, 0:37, 1, T{1}(6, :));
samples{end+1} = mk('nprb_itbs', 55, [1 17 26], 1, T{1}(55, [2 18 27]));
for L = 2:4
    samples{end+1} = mk('nprb_itbs_layer', 1, 0:37, L, T{L}(1, :));
    samples{end+1} = mk('nprb_itbs_layer', 25, [0 13 26 30 33 37], L, T{L}(25, [1 14 27 31 34 38]));
    samples{end+1} = mk('nprb_itbs_layer', 100, [5 15 28 35], L, T{L}(100, [6 16 29 36]));
end
samples{end+1} = mk('dtx', 10, -1, 1, 0);

rng(7);
for k = 1:12
    L = randi(4);
    nprb = randi(110);
    if L == 1 && k == 12
        itbs = -1;                    % DTX in random flow
    else
        itbs = sort(randperm(38, randi(6) + 1) - 1);
    end
    t = lteTBS(nprb, itbs, L);
    samples{end+1} = mk('rand', nprb, itbs, L, t);
end
samples = cat(2, samples{:});

fid = fopen(wt_sample_path('lte_tbs_samples.json'), 'w', 'n', 'UTF-8');
fprintf(fid, '%s', jsonencode(samples));
fclose(fid);
fprintf('Wrote lte_tbs_samples.json (%d samples)\n', numel(samples));
end

function s = mk(type, nprb, itbs, layer, tbs)
s = struct();
s.type = type;
s.nprb = nprb;
s.smnlayer = layer;
s.itbs = itbs;
s.tbs = tbs(:).';
end
