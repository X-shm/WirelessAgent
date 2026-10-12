%% gen_samples_nr_pending.m
% Deterministic MATLAB golden samples for the currently implemented NR subset.
% Requires 5G Toolbox. Generated JSON files are checked into
% matlab_oracle/samples and consumed only by their matching validators.

sample_dir = wt_sample_dir();

required_functions = {'nrPDSCHDMRS', 'nrPDSCHDMRSIndices', 'nrCSIRS', ...
    'nrDCIEncode', 'nrPDCCHPRBS', 'nrPDCCH'};
for ii = 1:numel(required_functions)
    if exist(required_functions{ii}, 'file') ~= 2
        error('wireless_toolbox:Missing5GToolbox', ...
            'Missing %s. Run this generator in MATLAB with 5G Toolbox installed.', ...
            required_functions{ii});
    end
end

generate_dmrs_samples(sample_dir);
generate_csi_rs_samples(sample_dir);
generate_dci_samples(sample_dir);
generate_pdcch_samples(sample_dir);
fprintf('NR pending-validation sample generation completed.\n');

function generate_dmrs_samples(sample_dir)
    cases = [ ...
        struct('name','type1_one_symbol','ncellid',42,'nscid',0,'nslot',1,'nsym',2,'nprb',5,'config_type',1,'nsymbols',1); ...
        struct('name','type2_one_symbol','ncellid',1007,'nscid',1,'nslot',7,'nsym',2,'nprb',3,'config_type',2,'nsymbols',1); ...
        struct('name','type1_nscid1','ncellid',512,'nscid',1,'nslot',2,'nsym',2,'nprb',2,'config_type',1,'nsymbols',1) ...
    ];
    samples = repmat(struct( ...
        'case_name','', 'ncellid',0, 'nscid',0, 'nslot',0, 'nsym',0, ...
        'nprb',0, 'config_type',0, 'nsymbols',0, ...
        'subcarrier_locations',[], 'sym_real',[], 'sym_imag',[]), 1, numel(cases));
    for ii = 1:numel(cases)
        c = cases(ii);
        carrier = nrCarrierConfig;
        carrier.NCellID = c.ncellid;
        carrier.NSizeGrid = c.nprb;
        carrier.NSlot = c.nslot;

        pdsch = nrPDSCHConfig;
        pdsch.NSizeBWP = c.nprb;
        pdsch.NStartBWP = 0;
        pdsch.PRBSet = 0:c.nprb-1;
        pdsch.PRBSetType = 'PRB';
        pdsch.NumLayers = 1;
        pdsch.MappingType = 'A';
        pdsch.SymbolAllocation = [0 14];

        dmrs = nrPDSCHDMRSConfig;
        dmrs.DMRSConfigurationType = c.config_type;
        dmrs.DMRSLength = 1;
        dmrs.DMRSTypeAPosition = 2;
        dmrs.DMRSAdditionalPosition = 0;
        dmrs.DMRSPortSet = 0;
        dmrs.NIDNSCID = c.ncellid;
        dmrs.NSCID = c.nscid;
        pdsch.DMRS = dmrs;

        sym = nrPDSCHDMRS(carrier, pdsch);
        ind = nrPDSCHDMRSIndices(carrier, pdsch, 'IndexStyle', 'subscript');
        locations = sort(unique(mod(double(ind(:,1))-1, 12))).';

        samples(ii).case_name = c.name;
        samples(ii).ncellid = c.ncellid;
        samples(ii).nscid = c.nscid;
        samples(ii).nslot = c.nslot;
        samples(ii).nsym = c.nsym;
        samples(ii).nprb = c.nprb;
        samples(ii).config_type = c.config_type;
        samples(ii).nsymbols = c.nsymbols;
        samples(ii).subcarrier_locations = locations;
        samples(ii).sym_real = real(sym(:)).';
        samples(ii).sym_imag = imag(sym(:)).';
    end
    write_json(fullfile(sample_dir, 'nr_dmrs.json'), samples);
    fprintf('Wrote nr_dmrs.json (%d cases)\n', numel(samples));
end

function generate_csi_rs_samples(sample_dir)
    cases = [ ...
        struct('name','density_one','nid',10,'nslot',2,'nsym',5,'nprb',4,'density',1,'row',2,'density_name','one'); ...
        struct('name','density_three','nid',100,'nslot',1,'nsym',7,'nprb',3,'density',3,'row',1,'density_name','three'); ...
        struct('name','density_half_even_rbs','nid',512,'nslot',3,'nsym',9,'nprb',6,'density',0,'row',2,'density_name','dot5even') ...
    ];
    samples = repmat(struct( ...
        'case_name','', 'nid',0, 'nslot',0, 'nsym',0, 'nprb',0, ...
        'density',0, 'rb_indices',[], 'sym_real',[], 'sym_imag',[]), 1, numel(cases));
    for ii = 1:numel(cases)
        c = cases(ii);
        carrier = nrCarrierConfig;
        carrier.NSizeGrid = c.nprb;
        carrier.NSlot = c.nslot;

        csirs = nrCSIRSConfig;
        csirs.CSIRSType = 'nzp';
        csirs.RowNumber = c.row;
        csirs.Density = c.density_name;
        csirs.SymbolLocations = c.nsym;
        csirs.SubcarrierLocations = 0;
        csirs.NumRB = c.nprb;
        csirs.RBOffset = 0;
        csirs.NID = c.nid;
        csirs.CSIRSPeriod = 'on';
        sym = nrCSIRS(carrier, csirs);

        samples(ii).case_name = c.name;
        samples(ii).nid = c.nid;
        samples(ii).nslot = c.nslot;
        samples(ii).nsym = c.nsym;
        samples(ii).nprb = c.nprb;
        samples(ii).density = c.density;
        if c.density == 0
            samples(ii).rb_indices = 0:2:c.nprb-1;
        else
            samples(ii).rb_indices = 0:c.nprb-1;
        end
        samples(ii).sym_real = real(sym(:)).';
        samples(ii).sym_imag = imag(sym(:)).';
    end
    write_json(fullfile(sample_dir, 'nr_csi_rs.json'), samples);
    fprintf('Wrote nr_csi_rs.json (%d cases)\n', numel(samples));
end

function generate_dci_samples(sample_dir)
    cases = [ ...
        struct('name','short_payload','k',12,'rnti',4660,'edci',108,'n_id',42); ...
        struct('name','medium_payload','k',32,'rnti',100,'edci',240,'n_id',2048) ...
    ];
    samples = repmat(struct( ...
        'case_name','', 'rnti',0, 'edci',0, 'n_id',0, ...
        'dci_bits',[], 'codeword',[], 'scrambled_codeword',[]), 1, numel(cases));
    for ii = 1:numel(cases)
        c = cases(ii);
        dci_bits = mod((0:c.k-1)' * (2*ii+1) + ii, 2);
        codeword = nrDCIEncode(dci_bits, c.rnti, c.edci);
        scramble = nrPDCCHPRBS(c.n_id, c.rnti, c.edci);

        samples(ii).case_name = c.name;
        samples(ii).rnti = c.rnti;
        samples(ii).edci = c.edci;
        samples(ii).n_id = c.n_id;
        samples(ii).dci_bits = double(dci_bits.');
        samples(ii).codeword = double(codeword(:).');
        samples(ii).scrambled_codeword = double(xor(logical(codeword(:)), logical(scramble(:))).');
    end
    write_json(fullfile(sample_dir, 'nr_dci.json'), samples);
    fprintf('Wrote nr_dci.json (%d cases)\n', numel(samples));
end

function generate_pdcch_samples(sample_dir)
    cases = [ ...
        struct('name','cell_id_scrambling','n_id',123,'n_rnti',0,'length',120); ...
        struct('name','dmrs_id_scrambling','n_id',2048,'n_rnti',321,'length',240) ...
    ];
    samples = repmat(struct( ...
        'case_name','', 'n_id',0, 'n_rnti',0, 'codeword',[], ...
        'sym_real',[], 'sym_imag',[]), 1, numel(cases));
    for ii = 1:numel(cases)
        c = cases(ii);
        codeword = mod((0:c.length-1)' * (2*ii+3) + 1, 2);
        sym = nrPDCCH(codeword, c.n_id, c.n_rnti);

        samples(ii).case_name = c.name;
        samples(ii).n_id = c.n_id;
        samples(ii).n_rnti = c.n_rnti;
        samples(ii).codeword = double(codeword.');
        samples(ii).sym_real = real(sym(:)).';
        samples(ii).sym_imag = imag(sym(:)).';
    end
    write_json(fullfile(sample_dir, 'nr_pdcch.json'), samples);
    fprintf('Wrote nr_pdcch.json (%d cases)\n', numel(samples));
end

function write_json(path, data)
    fid = fopen(path, 'w', 'n', 'UTF-8');
    if fid == -1
        error('wireless_toolbox:SampleWrite', 'Cannot open %s for writing.', path);
    end
    cleaner = onCleanup(@() fclose(fid));
    fprintf(fid, '%s', jsonencode(data));
end
