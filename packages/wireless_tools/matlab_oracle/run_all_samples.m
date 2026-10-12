function run_all_samples()
%RUN_ALL_SAMPLES Regenerate every MATLAB-backed oracle sample in this repository.
%
% Requires R2026a with 5G Toolbox, Bluetooth Toolbox, Communications Toolbox,
% LTE Toolbox and WLAN Toolbox. The runner resolves every generator from its own directory,
% so it is safe to invoke from any MATLAB current folder.

script_dir = fileparts(mfilename('fullpath'));
addpath(script_dir);

jobs = { ...
    '5g'; ...
    'cbs'; ...
    'lte_crc'; ...
    'lte_mcs'; ...
    'lte_modulation'; ...
    'lte_ofdm'; ...
    'lte_tbs'; ...
    'wlan_bcc'; ...
    'wlan_scramble'; ...
    'wlan_ldpc'; ...
    'bluetooth_core'; ...
    'ble_l2cap'; ...
    'ble_att'; ...
    'ble_gap_data'; ...
    'ble_ll_advertising'; ...
    'ble_ll_data'; ...
    'ble_network_config'; ...
    'ble_ideal_receiver'; ...
    'ble_pcap_writer'; ...
    'bluetooth_test_waveform'; ...
    'bluetooth_frequency_hop'; ...
    'ble_cs_waveform'; ...
    'bluetooth_test_waveform_validate'; ...
    'bluetooth_classic_waveform'; ...
    'bluetooth_classic_receiver'; ...
    'bluetooth_nodes'; ...
    'ble_coded_phy'; ...
    'ble_cte_phy'; ...
    'ble_multipulse_receiver'; ...
    'bluetooth_outdoor_range'; ...
    'bluetooth_edr_waveform'; ...
    'bluetooth_edr_receiver'; ...
    'bluetooth_edr_test_waveform'};

failures = strings(0, 1);
for index = 1:size(jobs, 1)
    job = jobs{index};
    fprintf('\n=== %s ===\n', job);
    try
        run_generator(job, script_dir);
    catch cause
        failures(end + 1, 1) = string(job) + ": " + string(cause.message); %#ok<AGROW>
        fprintf(2, 'FAIL %s: %s\n', job, cause.message);
    end
end

if ~isempty(failures)
    error('wireless_toolbox:SampleGenerationFailed', ...
        'MATLAB sample regeneration failed.%s%s', newline, strjoin(failures, newline));
end

fprintf('\nAll MATLAB oracle sample generators completed.\n');
end

function run_generator(job, script_dir)
% Do not use anonymous callbacks here: invoking a script from a static
% workspace prevents legacy script generators from introducing temporaries.
switch job
    case '5g'
        run_5g_samples();
    case 'cbs'
        run(fullfile(script_dir, 'gen_samples_cbs.m'));
    case 'lte_crc'
        run(fullfile(script_dir, 'gen_samples_lte_crc.m'));
    case 'lte_mcs'
        gen_samples_lte_mcs();
    case 'lte_modulation'
        run(fullfile(script_dir, 'gen_samples_lte_modulation.m'));
    case 'lte_ofdm'
        gen_samples_lte_ofdm();
    case 'lte_tbs'
        gen_samples_lte_tbs();
    case 'wlan_bcc'
        run(fullfile(script_dir, 'gen_samples_bcc.m'));
    case 'wlan_scramble'
        run(fullfile(script_dir, 'gen_samples_scramble.m'));
    case 'wlan_ldpc'
        run(fullfile(script_dir, 'gen_samples_wlan_ldpc.m'));
    case 'bluetooth_core'
        gen_samples_bluetooth_core();
    case 'ble_l2cap'
        gen_samples_ble_l2cap();
    case 'ble_att'
        gen_samples_ble_att();
    case 'ble_gap_data'
        gen_samples_ble_gap_data();
    case 'ble_ll_advertising'
        gen_samples_ble_ll_advertising();
    case 'ble_ll_data'
        gen_samples_ble_ll_data();
    case 'ble_network_config'
        gen_samples_ble_network_config();
    case 'ble_ideal_receiver'
        gen_samples_ble_ideal_receiver();
    case 'ble_pcap_writer'
        gen_samples_ble_pcap_writer();
    case 'bluetooth_test_waveform'
        gen_samples_bluetooth_test_waveform();
    case 'bluetooth_frequency_hop'
        gen_samples_bluetooth_frequency_hop();
    case 'ble_cs_waveform'
        gen_samples_ble_cs_waveform();
    case 'bluetooth_test_waveform_validate'
        gen_samples_bluetooth_test_waveform_validate();
    case 'bluetooth_classic_waveform'
        gen_samples_bluetooth_classic_waveform();
    case 'bluetooth_classic_receiver'
        gen_samples_bluetooth_classic_receiver();
    case 'bluetooth_nodes'
        gen_samples_bluetooth_nodes();
    case 'ble_coded_phy'
        gen_samples_ble_coded_phy();
    case 'ble_cte_phy'
        gen_samples_ble_cte_phy();
    case 'ble_multipulse_receiver'
        gen_samples_ble_multipulse_receiver();
    case 'bluetooth_outdoor_range'
        gen_samples_bluetooth_outdoor_range();
    case 'bluetooth_edr_waveform'
        gen_samples_bluetooth_edr_waveform();
    case 'bluetooth_edr_receiver'
        gen_samples_bluetooth_edr_receiver();
    case 'bluetooth_edr_test_waveform'
        gen_samples_bluetooth_edr_test_waveform();
    otherwise
        error('wireless_toolbox:UnknownSampleGenerator', 'Unknown generator: %s', job);
end
end
