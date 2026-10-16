# 验证说明

> 此文件由 `scripts/generate_registry_docs.py` 从 `tool_registry.json` 自动生成。
> 请先更新注册表，再执行 `python scripts/generate_registry_docs.py --write`；不要直接编辑本文件。

## 事实来源与范围

`tool_registry.json` 当前登记 `166` 个工具，且每项均引用一份 schema。注册状态分布：`validated`: 57，`independent_validated`: 109。
本文件不把注册状态扩大解释为额外的标准符合性结论；具体覆盖边界以每项 `coverage` 字段为准。
Bluetooth Toolbox 当前由 `26` 个 CLI 映射 `52` 个顶层 MATLAB 名称。`validated` 仅表示各工具 `coverage` 所述功能切片通过验证，不代表该名称的全部参数、对象方法、网络仿真或 MATLAB 完整行为均已实现；逐项完成状态和剩余缺口见 `bluetooth_capabilities.json`。

## 必跑命令

```bash
# 文档是否仍由注册表生成
python scripts/generate_registry_docs.py --check

# 全部 JSON 语法和 schema 基本结构
python scripts/check_json.py

# 已检入 MATLAB oracle 样本的哈希和结构是否未漂移
python scripts/generate_sample_manifest.py --check

# 注册表、schema 名称、脚本名、CLI flag、子命令和 --help
python scripts/check_contracts.py

# 自动发现并运行全部 validate_*.py 回归脚本
python scripts/validate_all.py

# 确定性的 PDSCH 无噪端到端收发回环（4 组配置）
python scripts/test_nr_pdsch_e2e.py --perfect-only

# Python 语法编译检查
python -m compileall -q tools scripts
```

具备 MATLAB R2026a 与 Bluetooth Toolbox 时，还可核查 52 个注册名称是否在本机真实解析：

```bash
matlab -batch "addpath('matlab_oracle'); verify_bluetooth_inventory"
```

`validate_all.py` 当前会自动发现 `142` 个专项验证器；该数量由文件系统发现，不应手工写死。

当前注册表没有 `pending_validation` 工具；所有已登记的 MATLAB 黄金样本验证器都会作为回归的一部分执行。

## 契约检查内容

`check_contracts.py` 以注册表和 `tools/*.schema.json` 交叉检查：

- 每个注册工具都有同名 schema，且 schema 指向同名 Python 脚本；
- Bluetooth Toolbox 恰好映射 52 个不同的顶层 MATLAB 名称，且每项说明覆盖边界；
- schema 的输入字段与 CLI 的 `--flag` 精确一致；
- schema 的 `subcommands` 与位置子命令及其 flag 一致；
- 每个注册工具的 `--help` 可执行；
- 由 `tool_registry.json` 生成的 README、技能文档和本验证说明未漂移；
- `tools/SKILL.md` 的 frontmatter 完整。

## 注册状态快照

| 产品/领域 | 工具数 | 注册状态分布 |
|---|---:|---|
| LTE Toolbox | 37 | `validated`: 5，`independent_validated`: 32 |
| 5G Toolbox | 48 | `validated`: 20，`independent_validated`: 28 |
| WLAN Toolbox | 9 | `validated`: 4，`independent_validated`: 5 |
| Bluetooth Toolbox | 26 | `validated`: 26 |
| Communications Toolbox | 30 | `independent_validated`: 30 |
| Wireless Network Toolbox | 6 | `independent_validated`: 6 |
| WirelessAgent Workflow | 8 | `independent_validated`: 8 |
| WirelessAgent Helper | 2 | `validated`: 2 |

## 按注册状态列出的工具

### `validated`（57）

`ble_angle_estimate`, `ble_att`, `ble_channel_selection`, `ble_cs_waveform`, `ble_cte_iq_sample`, `ble_gap_data`, `ble_ideal_receiver`, `ble_l2cap`, `ble_ll_advertising`, `ble_ll_data`, `ble_network_config`, `ble_packet_decode_status`, `ble_pcap_writer`, `ble_position_estimate`, `ble_waveform`, `bluetooth_classic_config`, `bluetooth_classic_receiver`, `bluetooth_classic_waveform`, `bluetooth_classic_whitening`, `bluetooth_frequency_hop`, `bluetooth_nodes`, `bluetooth_packet_duration`, `bluetooth_path_loss`, `bluetooth_range`, `bluetooth_session`, `bluetooth_test_waveform`, `bluetooth_test_waveform_validate`, `lte_crc`, `lte_mcs`, `lte_modulation`, `lte_ofdm`, `lte_tbs`, `nr_crc`, `nr_csi_rs`, `nr_dci`, `nr_dmrs`, `nr_equalize_mmse`, `nr_layer_map`, `nr_ldpc`, `nr_ldpc_rm`, `nr_mcs_tables`, `nr_modulation`, `nr_ofdm`, `nr_pbch`, `nr_pdcch`, `nr_pdsch`, `nr_polar`, `nr_prbs`, `nr_pss`, `nr_sss`, `nr_tbs`, `nr_timing_estimate`, `wireless_utils`, `wlan_bcc`, `wlan_ldpc`, `wlan_scramble`, `wlan_symbol_timing`。

### `independent_validated`（109）

`awgn`, `bch_code`, `ber_awgn`, `ber_coding`, `ber_fading`, `binary_symmetric_channel`, `bit_int_conversion`, `biterr`, `closed_loop_validator`, `convert_snr`, `convolutional_codec`, `dpsk_modulation`, `evm_metrics`, `fading_channel`, `frequency_offset`, `fsk_modulation`, `hamming_code`, `interleaver`, `link_adaptation_optimizer`, `link_capacity`, `lte_cell_rs`, `lte_cell_search`, `lte_code_block`, `lte_convolutional_codec`, `lte_cqi_select`, `lte_csi_codebook`, `lte_dl_channel_estimate`, `lte_extract_resources`, `lte_frame_offset`, `lte_frequency_sync`, `lte_layer_map`, `lte_mimo_equalizer`, `lte_pdsch_indices`, `lte_pdsch_prbs`, `lte_pmi_info`, `lte_pmi_select`, `lte_prbs`, `lte_pss`, `lte_pusch_dmrs`, `lte_pusch_indices`, `lte_rank_select`, `lte_rate_match_convolutional`, `lte_resource_grid`, `lte_scfdma`, `lte_srs`, `lte_sss`, `lte_standard_fading`, `lte_sync_indices`, `lte_ul_channel_estimate`, `lte_ul_precode`, `lte_ul_scrambling`, `node_mobility_constant_velocity`, `node_mobility_random_walk`, `node_mobility_random_waypoint`, `node_position_grid`, `node_position_random`, `nr_channel_estimate`, `nr_channel_prbs`, `nr_config`, `nr_evm`, `nr_grid_ops`, `nr_ldpc_code_block`, `nr_low_papr`, `nr_ofdm_info`, `nr_oran_bfp`, `nr_pbch_ref`, `nr_pdcch_decode`, `nr_pdsch_decode`, `nr_pdsch_grid_indices`, `nr_pdsch_precode`, `nr_perfect_timing`, `nr_polar_decode`, `nr_polar_rm`, `nr_prg_info`, `nr_prs`, `nr_pusch`, `nr_pusch_codebook`, `nr_pusch_ref`, `nr_pusch_scrambling`, `nr_sch_info`, `nr_srs`, `nr_ssb_measurements`, `nr_tables`, `nr_transform`, `ofdm_channel_estimate`, `ofdm_channel_response`, `ofdm_equalizer`, `ofdm_modulation`, `pam_modulation`, `policy_decision_validator`, `psk_modulation`, `q_function`, `qam_modulation`, `qos_policy_builder`, `radio_link_diagnosis`, `rectangular_pulse`, `reed_solomon_code`, `resource_allocation_optimizer`, `signal_timing_estimate`, `symerr`, `traffic_steering_optimizer`, `white_gaussian_noise`, `wireless_packet`, `wlan_cfo_estimate`, `wlan_constellation`, `wlan_golay`, `wlan_ofdm_info`, `wlan_packet_detect`, `zadoff_chu_seq`。

## 变更流程

1. 先在 `tool_registry.json` 新增或修改工具的产品、状态、覆盖范围、源函数和 schema 路径。
2. 同步新增/修改 `tools/<name>.schema.json` 和实际 CLI。
3. 执行 `python scripts/generate_registry_docs.py --write`。
4. 依次运行文档检查、契约检查、专项验证和全量验证。
