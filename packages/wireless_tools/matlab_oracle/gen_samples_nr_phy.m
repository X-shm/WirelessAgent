%% gen_samples_nr_phy.m — 每个工具独立 JSON，try-catch 隔离
out_dir = wt_sample_dir();

%% 1. PRBS
try
    r = struct();
    for ci = [0, 1, 100, 12345]
        for n = [10, 100, 1000]
            seq = nrPRBS(ci, n);
            r.(sprintf('cinit%d_n%d', ci, n)) = struct('cinit', ci, 'n', n, 'seq', double(seq.'));
        end
    end
    seq2 = nrPRBS(100, [50 20]);
    r.cinit100_offset50_len20 = struct('cinit', 100, 'offset', 50, 'n', 20, 'seq', double(seq2.'));
    write_json(fullfile(out_dir, 'nr_prbs.json'), r);
    fprintf('PRBS: OK\n');
catch e
    fprintf('PRBS: FAIL %s\n', e.message);
end

%% 2. PSS
try
    r = struct();
    for nc = [0, 1, 2, 100, 336, 504, 1007]
        sym = nrPSS(nc);
        r.(sprintf('ncellid%d', nc)) = struct('ncellid', nc, 'sym', sym.');
    end
    i1 = double(nrPSSIndices().');
    r.indices_1based = struct('indices', i1);
    i0 = double(nrPSSIndices('IndexBase', '0based').');
    r.indices_0based = struct('indices', i0);
    write_json(fullfile(out_dir, 'nr_pss.json'), r);
    fprintf('PSS: OK\n');
catch e
    fprintf('PSS: FAIL %s\n', e.message);
end

%% 3. SSS
try
    r = struct();
    for nc = [0, 1, 2, 3, 100, 336, 504, 700, 1007]
        sym = nrSSS(nc);
        r.(sprintf('ncellid%d', nc)) = struct('ncellid', nc, 'sym', sym.');
    end
    i1 = double(nrSSSIndices().');
    r.indices_1based = struct('indices', i1);
    write_json(fullfile(out_dir, 'nr_sss.json'), r);
    fprintf('SSS: OK\n');
catch e
    fprintf('SSS: FAIL %s\n', e.message);
end

%% 4. TBS
try
    r = struct();
    cfgs = {'QPSK',1,25,154,0.5; '16QAM',1,50,154,0.5; '64QAM',2,100,156,0.5; 'QPSK',1,1,120,0.12; '256QAM',4,200,154,0.6; 'QPSK',1,25,154,0.308; '1024QAM',1,100,156,0.4; '64QAM',1,51,154,0.601};
    for i = 1:size(cfgs,1)
        m = cfgs{i,1}; L = cfgs{i,2}; P = cfgs{i,3}; RE = cfgs{i,4}; T = cfgs{i,5};
        t = nrTBS(m, L, P, RE, T, 0, 1.0);
        r.(sprintf('case%d', i)) = struct('modulation', m, 'nlayers', L, 'nPRB', P, 'NREPerPRB', RE, 'tcr', T, 'xOh', 0, 'tbScaling', 1.0, 'tbs', t);
    end
    write_json(fullfile(out_dir, 'nr_tbs.json'), r);
    fprintf('TBS: OK\n');
catch e
    fprintf('TBS: FAIL %s\n', e.message);
end

%% 5. MCS Tables
try
    r = struct();
    mt = nrPDSCHMCSTables();
    names = fieldnames(mt);
    for i = 1:numel(names)
        tbl = mt.(names{i});
        n = height(tbl);
        mcs_idx = zeros(n,1); qm = zeros(n,1); tcr = zeros(n,1); se = zeros(n,1);
        mod_str = cell(n,1);
        for j = 1:n
            mcs_idx(j) = tbl.MCSIndex(j);
            mod_str{ j} = char(tbl.Modulation(j));
            qm(j) = tbl.Qm(j);
            tcr(j) = tbl.TargetCodeRate(j);
            se(j) = tbl.SpectralEfficiency(j);
        end
        r.(names{i}) = struct(...
            'mcs_index', mcs_idx', ...
            'modulation', mod_str', ...
            'qm', qm', ...
            'target_code_rate', tcr', ...
            'spectral_efficiency', se');
    end
    write_json(fullfile(out_dir, 'nr_mcs_tables.json'), r);
    fprintf('MCS: OK\n');
catch e
    fprintf('MCS: FAIL %s\n', e.message);
end

fprintf('\nDone.\n');

function write_json(path, data)
    fid = fopen(path, 'w', 'n', 'UTF-8');
    fprintf(fid, '%s', jsonencode(data));
    fclose(fid);
end
