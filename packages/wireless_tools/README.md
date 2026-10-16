# Wireless Toolbox

> 此文件由 `scripts/generate_registry_docs.py` 从 `tool_registry.json` 自动生成。
> 请先更新注册表，再执行 `python scripts/generate_registry_docs.py --write`；不要直接编辑本文件。

## 项目范围

当前注册 `176` 个 Python CLI 工具、`176` 份 schema。状态分布：`validated`: 57，`independent_validated`: 109，`pending_validation`: 10。
工具名称、产品归属、标准源函数、状态、覆盖范围和 schema 路径均以 `tool_registry.json` 为唯一事实来源。
Bluetooth Toolbox 当前由 `26` 个 CLI 映射 `52` 个顶层 MATLAB 名称。`validated` 仅表示各工具 `coverage` 所述功能切片通过验证，不代表该名称的全部参数、对象方法、网络仿真或 MATLAB 完整行为均已实现；逐项完成状态和剩余缺口见 `bluetooth_capabilities.json`。

## 工具概览

| 产品/领域 | 工具数 | 注册状态分布 |
|---|---:|---|
| LTE Toolbox | 37 | `validated`: 5，`independent_validated`: 32 |
| 5G Toolbox | 58 | `validated`: 20，`independent_validated`: 28，`pending_validation`: 10 |
| WLAN Toolbox | 9 | `validated`: 4，`independent_validated`: 5 |
| Bluetooth Toolbox | 26 | `validated`: 26 |
| Communications Toolbox | 30 | `independent_validated`: 30 |
| Wireless Network Toolbox | 6 | `independent_validated`: 6 |
| WirelessAgent Workflow | 8 | `independent_validated`: 8 |
| WirelessAgent Helper | 2 | `validated`: 2 |

## 使用方式

所有工具均以 JSON 输出。先查看实际 CLI，再按对应 schema 提供参数：

```bash
python tools/nr_pdsch.py --help
python tools/nr_modulation.py --mod QPSK --bits 1,1,0,1
python tools/wlan_bcc.py --bits 1,1,0,1,0,0,0,1 --rate 1/2 --decode
```

工具的完整输入/输出契约位于 `tools/<tool>.schema.json`。位置子命令（例如 `wireless_utils` 与 `nr_dci`）由 schema 的 `subcommands` 字段描述。

## 验证

验证流程、契约检查范围与当前注册状态清单见 [VALIDATION.md](VALIDATION.md)。

```bash
python scripts/generate_registry_docs.py --check
python scripts/check_contracts.py
python scripts/validate_all.py
```

## 注册工具清单

### LTE Toolbox（37）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `evm_metrics` | `lteEVM` | `independent_validated` | — | `tools/evm_metrics.schema.json` |
| `lte_cell_rs` | `lteCellRS`<br>`lteCellRSIndices` | `independent_validated` | FDD CRS ports 0..3 with 0-based subscript indices | `tools/lte_cell_rs.schema.json` |
| `lte_cell_search` | `lteCellSearch` | `independent_validated` | grid-domain PSS/SSS correlation search | `tools/lte_cell_search.schema.json` |
| `lte_code_block` | `lteCodeBlockSegment`<br>`lteCodeBlockDesegment` | `independent_validated` | — | `tools/lte_code_block.schema.json` |
| `lte_convolutional_codec` | `lteConvolutionalEncode`<br>`lteConvolutionalDecode` | `independent_validated` | hard-decision Viterbi decode | `tools/lte_convolutional_codec.schema.json` |
| `lte_cqi_select` | `lteCQISelect` | `independent_validated` | explicit SINR lookup for wideband/single-codeword subband CQI | `tools/lte_cqi_select.schema.json` |
| `lte_crc` | `lteCRCEncode`<br>`lteCRCDecode` | `validated` | — | `tools/lte_crc.schema.json` |
| `lte_csi_codebook` | `lteCSICodebook`<br>`lteDLPrecode`<br>`lteDLDeprecode` | `independent_validated` | one/two-port standard CSI codebook and SpatialMux precode/deprecode | `tools/lte_csi_codebook.schema.json` |
| `lte_dl_channel_estimate` | `lteDLChannelEstimate` | `independent_validated` | CRS-based LS estimate for ports 0..3 with linear interpolation | `tools/lte_dl_channel_estimate.schema.json` |
| `lte_extract_resources` | `lteExtractResources` | `independent_validated` | 2-D/3-D complex grid, linear/subscript indices | `tools/lte_extract_resources.schema.json` |
| `lte_frame_offset` | `lteDLFrameOffset`<br>`lteULFrameOffset` | `independent_validated` | explicit standard reference waveform correlation core | `tools/lte_frame_offset.schema.json` |
| `lte_frequency_sync` | `lteFrequencyOffset`<br>`lteFrequencyCorrect` | `independent_validated` | CP-correlation estimate with explicit FFT/CP/sample-rate inputs | `tools/lte_frequency_sync.schema.json` |
| `lte_layer_map` | `lteLayerMap`<br>`lteLayerDemap` | `independent_validated` | one/two codewords, 1..8 layers | `tools/lte_layer_map.schema.json` |
| `lte_mcs` | `lteMCS` | `validated` | — | `tools/lte_mcs.schema.json` |
| `lte_mimo_equalizer` | `lteEqualizeMIMO`<br>`lteEqualizeULMIMO` | `independent_validated` | explicit precoder or one/two-port codebook joint MMSE equalization | `tools/lte_mimo_equalizer.schema.json` |
| `lte_modulation` | `lteSymbolModulate`<br>`lteSymbolDemodulate` | `validated` | — | `tools/lte_modulation.schema.json` |
| `lte_ofdm` | `lteOFDMInfo`<br>`lteOFDMModulate`<br>`lteOFDMDemodulate` | `validated` | — | `tools/lte_ofdm.schema.json` |
| `lte_pdsch_indices` | `ltePDSCHIndices` | `independent_validated` | FDD Release 8/9 CRS schemes with control, CRS, sync and PBCH exclusion | `tools/lte_pdsch_indices.schema.json` |
| `lte_pdsch_prbs` | `ltePDSCHPRBS` | `independent_validated` | binary/signed sequence with arbitrary zero-based segment | `tools/lte_pdsch_prbs.schema.json` |
| `lte_pmi_info` | `ltePMIInfo` | `independent_validated` | wideband/subband metadata and standard/alternative codebook bounds | `tools/lte_pmi_info.schema.json` |
| `lte_pmi_select` | `ltePMISelect` | `independent_validated` | two-port rank-1/rank-2 wideband/subband LMMSE SINR selection | `tools/lte_pmi_select.schema.json` |
| `lte_prbs` | `ltePRBS` | `independent_validated` | — | `tools/lte_prbs.schema.json` |
| `lte_pss` | `ltePSS` | `independent_validated` | — | `tools/lte_pss.schema.json` |
| `lte_pusch_dmrs` | `ltePUSCHDRS`<br>`ltePUSCHDRSIndices` | `independent_validated` | single-layer explicit PRB allocation, >=3 PRBs, no hopping/precoding | `tools/lte_pusch_dmrs.schema.json` |
| `lte_pusch_indices` | `ltePUSCHIndices` | `independent_validated` | explicit slot-wise PRB allocation, DM-RS exclusion, shortened subframe and G/Gd | `tools/lte_pusch_indices.schema.json` |
| `lte_rank_select` | `lteRISelect` | `independent_validated` | two-port rank-1/rank-2 LMMSE SINR with PMI and hysteresis | `tools/lte_rank_select.schema.json` |
| `lte_rate_match_convolutional` | `lteRateMatchConvolutional`<br>`lteRateRecoverConvolutional` | `independent_validated` | — | `tools/lte_rate_match_convolutional.schema.json` |
| `lte_resource_grid` | `lteResourceGridSize`<br>`lteResourceGrid` | `independent_validated` | grid sizing and zero-grid descriptor | `tools/lte_resource_grid.schema.json` |
| `lte_scfdma` | `lteSCFDMAInfo`<br>`lteSCFDMAModulate`<br>`lteSCFDMADemodulate` | `independent_validated` | whole-subframe grid, DFT spreading and half-subcarrier shift | `tools/lte_scfdma.schema.json` |
| `lte_srs` | `lteSRS`<br>`lteSRSIndices` | `independent_validated` | single antenna, explicit contiguous >=6 PRBs, no ConfigIdx/hopping | `tools/lte_srs.schema.json` |
| `lte_sss` | `lteSSS` | `independent_validated` | — | `tools/lte_sss.schema.json` |
| `lte_standard_fading` | `lteFadingChannel` | `independent_validated` | EPA/EVA/ETU SISO or parallel-channel Rayleigh subset with correlated Doppler approximation | `tools/lte_standard_fading.schema.json` |
| `lte_sync_indices` | `ltePSSIndices`<br>`lteSSSIndices` | `independent_validated` | FDD subframes 0/5, normal and extended CP | `tools/lte_sync_indices.schema.json` |
| `lte_tbs` | `lteTBS` | `validated` | — | `tools/lte_tbs.schema.json` |
| `lte_ul_channel_estimate` | `lteULChannelEstimate` | `independent_validated` | single-layer PUSCH DM-RS allocated-PRB estimate | `tools/lte_ul_channel_estimate.schema.json` |
| `lte_ul_precode` | `lteULPrecode`<br>`lteULDeprecode` | `independent_validated` | PRB/subcarrier normalized block DFT and inverse | `tools/lte_ul_precode.schema.json` |
| `lte_ul_scrambling` | `lteULScramble`<br>`lteULDescramble` | `independent_validated` | transport data without UCI placeholders | `tools/lte_ul_scrambling.schema.json` |

### 5G Toolbox（58）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `nr_bch_codec` | `nrBCH`<br>`nrBCHDecode` | `pending_validation` | 独立 Python BCH 32 位载荷交织、Gold 扰码、CRC24C、Polar 编码与 SC(L=1) 解码，固定 864 位码字。 | `tools/nr_bch_codec.schema.json` |
| `nr_channel_estimate` | `nrChannelEstimate` | `independent_validated` | Single reference port, one normal/extended-CP slot, sparse least-squares estimate with Interpolation=off and CDMLengths=[1,1]; interpolation, CDM despreading and PRG noise estimates are not included | `tools/nr_channel_estimate.schema.json` |
| `nr_channel_models` | `nrTDLChannel`<br>`nrCDLChannel`<br>`nrHSTChannel`<br>`nrPathLoss`<br>`nrPerfectChannelEstimate`<br>`nrPhaseNoise` | `pending_validation` | 独立 Python 显式路径信道子集；不包含 MATLAB 预设 TDL/CDL/HST 配置和相位噪声多极点模型。 | `tools/nr_channel_models.schema.json` |
| `nr_channel_prbs` | `nrPBCHPRBS`<br>`nrPDSCHPRBS`<br>`nrPUSCHPRBS`<br>`nrPUCCHPRBS` | `independent_validated` | PBCH phase, PDSCH/PUSCH codeword and PUCCH base scrambling sequences; PUSCH msgA nrapid extension is not included | `tools/nr_channel_prbs.schema.json` |
| `nr_config` | `nrCarrierConfig`<br>`nrCORESETConfig`<br>`nrCSIReportConfig`<br>`nrCSIRSConfig`<br>`nrDLCarrierConfig`<br>`nrIntraCellGuardBandsConfig`<br>`nrPathLossConfig`<br>`nrPDCCHConfig`<br>`nrPDSCHConfig`<br>`nrPDSCHDMRSConfig`<br>`nrPDSCHPTRSConfig`<br>`nrPDSCHReservedConfig`<br>`nrPRACHConfig`<br>`nrPRSConfig`<br>`nrPUCCH0Config`<br>`nrPUCCH1Config`<br>`nrPUCCH2Config`<br>`nrPUCCH3Config`<br>`nrPUCCH4Config`<br>`nrPUSCHConfig`<br>`nrPUSCHDMRSConfig`<br>`nrPUSCHPTRSConfig`<br>`nrSCSCarrierConfig`<br>`nrSearchSpaceConfig`<br>`nrSRSConfig`<br>`nrULCarrierConfig`<br>`nrWavegenBWPConfig`<br>`nrWavegenCSIRSConfig`<br>`nrWavegenPDCCHConfig`<br>`nrWavegenPDSCHConfig`<br>`nrWavegenPUCCH0Config`<br>`nrWavegenPUCCH1Config`<br>`nrWavegenPUCCH2Config`<br>`nrWavegenPUCCH3Config`<br>`nrWavegenPUCCH4Config`<br>`nrWavegenPUSCHConfig`<br>`nrWavegenSRSConfig`<br>`nrWavegenSSBurstConfig` | `independent_validated` | 38 JSON configuration constructors with R2026a defaults and known-property overrides; MATLAB class validation and dependent property updates are only partially reproduced | `tools/nr_config.schema.json` |
| `nr_control_codec` | `nrDCIDecode`<br>`nrUCIEncode`<br>`nrUCIDecode` | `pending_validation` | 独立 Python 控制信息 Polar 编解码。DCI 使用 SC(L=1) 和 CRC24C；UCI 支持 12..1012 位未分段 Polar 分支及上行三角交织。 | `tools/nr_control_codec.schema.json` |
| `nr_crc` | `nrCRCEncode`<br>`nrCRCDecode` | `validated` | — | `tools/nr_crc.schema.json` |
| `nr_csi_resources` | `nrCSIMeasurementsSRS`<br>`nrCSIReportCSIRS`<br>`nrCSIRSIndices`<br>`nrCSIRSMeasurements` | `pending_validation` | 独立 Python 单端口 CSI 资源及宽带质量估计子集；CQI 为 Shannon 界近似，不等同 MATLAB 的完整码本报告。 | `tools/nr_csi_resources.schema.json` |
| `nr_csi_rs` | `nrCSIRS` | `validated` | Single-port CSI-RS sequence for contiguous RBs from RB 0 at density 0.5, 1, or 3; no resource-grid indices | `tools/nr_csi_rs.schema.json` |
| `nr_dci` | `nrDCIEncode`<br>`nrPDCCHPRBS` | `validated` | DCI encode (CRC24C calculated over 24 leading ones plus payload, then payload plus RNTI-masked CRC Polar coding and rate matching) plus PDCCH scrambling; no DCI decode | `tools/nr_dci.schema.json` |
| `nr_dmrs` | `nrPDSCHDMRS` | `validated` | Single-port PDSCH DM-RS sequence and per-PRB locations for contiguous PRBs, configuration types 1/2; no full grid indices | `tools/nr_dmrs.schema.json` |
| `nr_equalize_mmse` | `nrEqualizeMMSE` | `validated` | MMSE equalization with CSI output; SISO/SIMO/MIMO 2x2 subset | `tools/nr_equalize_mmse.schema.json` |
| `nr_evm` | `nrEVM` | `independent_validated` | Equalized-grid/reference-grid direct syntax; carrier/channel receiver-processing syntax is not included | `tools/nr_evm.schema.json` |
| `nr_grid_ops` | `nrResourceGrid`<br>`nrExtractResources` | `independent_validated` | Zero resource grid for explicit NRB/CP/ports and allplanes RE extraction with linear or subscript indices | `tools/nr_grid_ops.schema.json` |
| `nr_layer_map` | `nrLayerMap`<br>`nrLayerDemap` | `validated` | — | `tools/nr_layer_map.schema.json` |
| `nr_ldpc` | `nrLDPCEncode`<br>`nrLDPCDecode` | `validated` | — | `tools/nr_ldpc.schema.json` |
| `nr_ldpc_code_block` | `nrCodeBlockSegmentLDPC`<br>`nrCodeBlockDesegmentLDPC` | `independent_validated` | LDPC code-block segmentation with CRC24B and filler bits; BG1/BG2 | `tools/nr_ldpc_code_block.schema.json` |
| `nr_ldpc_rm` | `nrRateMatchLDPC`<br>`nrRateRecoverLDPC` | `validated` | rate match + rate recover with de-interleaving | `tools/nr_ldpc_rm.schema.json` |
| `nr_low_papr` | `nrLowPAPRS` | `independent_validated` | Type-1 low-PAPR sequence for scalar/vector u, v and alpha, including m=0, short standard phase tables and Zadoff-Chu lengths >=30; type-2 syntax is not included | `tools/nr_low_papr.schema.json` |
| `nr_mcs_tables` | `nrPDSCHMCSTables` | `validated` | PDSCH MCS tables 1-4; CQI tables are not implemented | `tools/nr_mcs_tables.schema.json` |
| `nr_modulation` | `nrSymbolModulate`<br>`nrSymbolDemodulate` | `validated` | BPSK, pi/2-BPSK, QPSK and square QAM through 1024QAM, includes soft demodulation (LLR) | `tools/nr_modulation.schema.json` |
| `nr_ofdm` | `nrOFDMModulate`<br>`nrOFDMDemodulate` | `validated` | OFDM modulation with CP, demodulation roundtrip | `tools/nr_ofdm.schema.json` |
| `nr_ofdm_info` | `nrOFDMInfo` | `independent_validated` | NR OFDM geometry with explicit windowing and zero carrier frequency; MATLAB's automatic window choice and arbitrary resampling are not included | `tools/nr_ofdm_info.schema.json` |
| `nr_oran_bfp` | `nrORANBlockCompress`<br>`nrORANBlockDecompress` | `independent_validated` | O-RAN block floating point (BFP) compression/decompression of integer IQ grids; block scaling and mu-law methods are not included | `tools/nr_oran_bfp.schema.json` |
| `nr_pbch` | `nrPBCH`<br>`nrPBCHDecode` | `validated` | PBCH bit scrambling + QPSK mapping; hard/soft decode path | `tools/nr_pbch.schema.json` |
| `nr_pbch_ref` | `nrPBCHDMRS`<br>`nrPBCHDMRSIndices`<br>`nrPBCHIndices` | `independent_validated` | PBCH DM-RS sequence and RE indices for the PBCH resource set | `tools/nr_pbch_ref.schema.json` |
| `nr_pdcch` | `nrPDCCH` | `validated` | PDCCH scrambling and QPSK modulation of an encoded DCI codeword; no CORESET or resource-grid mapping | `tools/nr_pdcch.schema.json` |
| `nr_pdcch_decode` | `nrPDCCHDecode` | `independent_validated` | Direct QPSK symbol syntax with noise variance; returns soft DCI codeword bits, without Polar DCI decode | `tools/nr_pdcch_decode.schema.json` |
| `nr_pdcch_resources` | `nrPDCCHResources`<br>`nrPDCCHSpace` | `pending_validation` | 独立 Python 单符号、非交织 CORESET 资源映射；每 CCE 为 6 REG，每 REG 为 9 数据 RE 加 3 DM-RS RE。 | `tools/nr_pdcch_resources.schema.json` |
| `nr_pdsch` | `nrPDSCH`<br>`nrDLSCH` | `validated` | end-to-end PDSCH TX/RX cascade: CRC→LDPC→RM→modulation→layer map→OFDM | `tools/nr_pdsch.schema.json` |
| `nr_pdsch_decode` | `nrPDSCHDecode` | `independent_validated` | Direct symbol syntax for one codeword and 1..4 layers, max-log LLR; two-codeword and carrier/config-object forms are not included | `tools/nr_pdsch_decode.schema.json` |
| `nr_pdsch_grid_indices` | `nrPDSCHDMRSIndices`<br>`nrPDSCHIndices` | `independent_validated` | One layer/port, explicit DM-RS symbols, carrier PRB allocation, type-1/2 CDM reservation; no PTRS, VRB interleaving, reserved RE or multiport mapping | `tools/nr_pdsch_grid_indices.schema.json` |
| `nr_pdsch_precode` | `nrPDSCHPrecode` | `independent_validated` | Matrix-valued PDSCH symbols with identical RE positions per layer, arbitrary antennas and PRG-specific complex weights; 3-D channel-estimate tensor syntax is not included | `tools/nr_pdsch_precode.schema.json` |
| `nr_perfect_timing` | `nrPerfectTimingEstimate` | `independent_validated` | Perfect timing offset and per-receive-antenna impulse-response magnitude from four-dimensional path gains and real path filters | `tools/nr_perfect_timing.schema.json` |
| `nr_polar` | `nrPolarEncode` | `validated` | Polar mother-code encoding for downlink/uplink; decoding is provided by nr_polar_decode | `tools/nr_polar.schema.json` |
| `nr_polar_decode` | `nrPolarDecode` | `independent_validated` | L=1 successive-cancellation decoding of rate-recovered Polar mother-code LLRs with optional output deinterleaving; CRC-aided list decoding L>1 is not included | `tools/nr_polar_decode.schema.json` |
| `nr_polar_rm` | `nrRateMatchPolar`<br>`nrRateRecoverPolar` | `independent_validated` | Polar rate match/recover: subblock interleave + bit selection (puncture/repeat/shorten) | `tools/nr_polar_rm.schema.json` |
| `nr_prach_family` | `nrPRACH`<br>`nrPRACHDetect`<br>`nrPRACHGrid`<br>`nrPRACHIndices`<br>`nrPRACHOFDMInfo`<br>`nrPRACHOFDMModulate` | `pending_validation` | 独立 Python 单个 PRACH 时频机会处理；支持 139/839 点 Zadoff-Chu 序列，显式物理根序号及循环移位。 | `tools/nr_prach_family.schema.json` |
| `nr_prbs` | `nrPRBS` | `validated` | Gold code PRBS generator, cinit init, binary/signed output | `tools/nr_prbs.schema.json` |
| `nr_prg_info` | `nrPRGInfo` | `independent_validated` | PRG sizes 2 or 4 and wideband, with NStartGrid/NSizeGrid carrier geometry | `tools/nr_prg_info.schema.json` |
| `nr_prs` | `nrPRS`<br>`nrPRSIndices` | `independent_validated` | Single active PRS resource in a normal-CP carrier slot; comb sizes 2/4/6/12, resource RB and symbol allocation, sequence ID and slot; resource-set periodicity, repetitions, muting and multiple resources are not included | `tools/nr_prs.schema.json` |
| `nr_pss` | `nrPSS`<br>`nrPSSIndices` | `validated` | PSS m-sequence generation + RE indices | `tools/nr_pss.schema.json` |
| `nr_ptrs_family` | `nrPDSCHPTRS`<br>`nrPDSCHPTRSIndices`<br>`nrPUSCHPTRS`<br>`nrPUSCHPTRSIndices` | `pending_validation` | 独立 Python 单端口、无变换预编码 PT-RS 子集；需要显式给出 RB、DM-RS 符号与时频密度。 | `tools/nr_ptrs_family.schema.json` |
| `nr_pucch_family` | `nrPUCCH`<br>`nrPUCCH0`<br>`nrPUCCH1`<br>`nrPUCCH2`<br>`nrPUCCH3`<br>`nrPUCCH4`<br>`nrPUCCHDecode`<br>`nrPUCCHDMRS`<br>`nrPUCCHDMRSIndices`<br>`nrPUCCHHoppingInfo`<br>`nrPUCCHIndices` | `pending_validation` | 独立 Python 单 RB PUCCH 0..4 基本调制、资源、DM-RS 与无噪声解调子集；不覆盖完整频跳、码本和 UCI 编码。 | `tools/nr_pucch_family.schema.json` |
| `nr_pusch` | `nrPUSCH`<br>`nrPUSCHDecode` | `independent_validated` | PUSCH scramble + modulation + layer map; optional DFT-s-OFDM transform precoding | `tools/nr_pusch.schema.json` |
| `nr_pusch_codebook` | `nrPUSCHCodebook` | `independent_validated` | All 4542 valid R2026a layer/port/TPMI/transform/codebook-type combinations for 1, 2, 4 and 8 ports; R2026b three-port addition is not included | `tools/nr_pusch_codebook.schema.json` |
| `nr_pusch_ref` | `nrPUSCHDMRS`<br>`nrPUSCHDMRSIndices`<br>`nrPUSCHIndices` | `independent_validated` | PUSCH DM-RS sequence and data RE indices for one BWP allocation | `tools/nr_pusch_ref.schema.json` |
| `nr_pusch_scrambling` | `nrPUSCHScramble`<br>`nrPUSCHDescramble` | `independent_validated` | Single-codeword binary bits or soft LLRs, including q=0/1; no UCI X/Y placeholders or msgA nrapid | `tools/nr_pusch_scrambling.schema.json` |
| `nr_sch_info` | `nrDLSCHInfo`<br>`nrULSCHInfo` | `independent_validated` | Scalar TBS/TCR coding dimensions; UL-SCH UCI multiplexing and two-codeword forms are not included | `tools/nr_sch_info.schema.json` |
| `nr_sch_transport` | `nrDLSCHDecoder`<br>`nrULSCH`<br>`nrULSCHDecoder`<br>`nrULSCHDemultiplex`<br>`nrULSCHMultiplex` | `pending_validation` | 独立 Python 单 LDPC 码块共享信道子集；复用现有 CRC/LDPC 并显式处理 filler、速率匹配。UCI 复用仅支持显式插入位置。 | `tools/nr_sch_transport.schema.json` |
| `nr_srs` | `nrSRS`<br>`nrSRSIndices` | `independent_validated` | Zadoff-Chu SRS sequence and comb-based resource indices | `tools/nr_srs.schema.json` |
| `nr_ssb_measurements` | `nrSSBMeasurements` | `independent_validated` | 240x4 SSB grid, per-Rx RSRP/RSSI/RSRQ, optional PBCH DM-RS contribution; phase-correction option is not included | `tools/nr_ssb_measurements.schema.json` |
| `nr_sss` | `nrSSS`<br>`nrSSSIndices` | `validated` | SSS dual m-sequence generation + RE indices | `tools/nr_sss.schema.json` |
| `nr_tables` | `nrCQITables`<br>`nrPUSCHMCSTables` | `independent_validated` | Four CQI tables and five default PUSCH MCS tables from R2026a; PUSCHMCSTables property-dependent variants are not included | `tools/nr_tables.schema.json` |
| `nr_tbs` | `nrTBS` | `validated` | Transport block size determination per TS 38.214 | `tools/nr_tbs.schema.json` |
| `nr_timing_estimate` | `nrTimingEstimate` | `validated` | cross-correlation timing estimate; direct waveform pair or built-in NR reference grid | `tools/nr_timing_estimate.schema.json` |
| `nr_transform` | `nrTransformPrecode`<br>`nrTransformDeprecode` | `independent_validated` | Unitary 12×MRB DFT/IFFT per column, all integer MRB and row counts divisible by 12×MRB | `tools/nr_transform.schema.json` |
| `nr_waveform_io` | `nrWaveformAnalyzer`<br>`nrWaveformGenerator` | `pending_validation` | 独立 Python 单 numerology 资源网格 OFDM 波形生成和分析子集；分析器返回资源网格、PAPR 与频谱。 | `tools/nr_waveform_io.schema.json` |

### WLAN Toolbox（9）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `wlan_bcc` | `wlanBCCEncode`<br>`wlanBCCDecode` | `validated` | — | `tools/wlan_bcc.schema.json` |
| `wlan_cfo_estimate` | `wlanFineCFOEstimate`<br>`wlanCoarseCFOEstimate` | `independent_validated` | L-STF coarse and L-LTF fine carrier frequency offset estimates | `tools/wlan_cfo_estimate.schema.json` |
| `wlan_constellation` | `wlanConstellationMap`<br>`wlanConstellationDemap` | `independent_validated` | IEEE 802.11 constellation map/demap BPSK..4096QAM, Gray and hard/soft demap | `tools/wlan_constellation.schema.json` |
| `wlan_golay` | `wlanGolaySequence` | `independent_validated` | 802.11ad Golay complementary Ga/Gb pairs, lengths 32/64/128 | `tools/wlan_golay.schema.json` |
| `wlan_ldpc` | `wlanLDPCDecode`<br>`wlanLDPCEncode` | `validated` | — | `tools/wlan_ldpc.schema.json` |
| `wlan_ofdm_info` | `wlanNonHTOFDMInfo` | `independent_validated` | Non-HT OFDM parameters for L-LTF/L-SIG/NonHT-Data at 20/40 MHz | `tools/wlan_ofdm_info.schema.json` |
| `wlan_packet_detect` | `wlanPacketDetect` | `independent_validated` | Schmidl-Cox L-STF autocorrelation packet detect with offset and decision metric | `tools/wlan_packet_detect.schema.json` |
| `wlan_scramble` | `wlanScramble`<br>`wlanDescramble` | `validated` | — | `tools/wlan_scramble.schema.json` |
| `wlan_symbol_timing` | `wlanSymbolTimingEstimate` | `validated` | L-LTF cross-correlation timing with CSD-aware multi-bandwidth L-LTF generation | `tools/wlan_symbol_timing.schema.json` |

### Bluetooth Toolbox（26）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `ble_angle_estimate` | `bleAngleEstimate`<br>`bleAngleEstimateConfig` | `validated` | ULA MUSIC broadside-angle estimate with 0.1-degree scan plus serializable ULA/custom-array configuration and derived element positions; URA/custom-array MUSIC estimation remains excluded | `tools/ble_angle_estimate.schema.json` |
| `ble_att` | `bleATTPDUConfig`<br>`bleATTPDU`<br>`bleATTPDUDecode` | `validated` | All 25 documented ATT opcodes, configuration defaults, byte encoding and structured decoding status | `tools/ble_att.schema.json` |
| `ble_channel_selection` | `bleChannelSelection` | `validated` | CSA #1 and #2 for connection/periodic events, plus sequential isochronous subevent selection with explicit state | `tools/ble_channel_selection.schema.json` |
| `ble_cs_waveform` | `bleCSWaveform` | `validated` | CS step modes 0..3 with explicit reproducible access-address, optional-sequence, and tone-extension randomness; MATLAB DRBG lookup distribution not reproduced | `tools/ble_cs_waveform.schema.json` |
| `ble_cte_iq_sample` | `bleCTEIQSample` | `validated` | LE1M/LE2M CTE Gaussian matched filtering, reference/slot sampling, DC removal and frequency-offset compensation | `tools/ble_cte_iq_sample.schema.json` |
| `ble_gap_data` | `bleGAPDataBlockConfig`<br>`bleGAPDataBlock`<br>`bleGAPDataBlockDecode` | `validated` | All six supported GAP AD types, configuration defaults, byte encoding and structured decoding status | `tools/ble_gap_data.schema.json` |
| `ble_ideal_receiver` | `bleIdealReceiver` | `validated` | All four LE PHY modes, noiseless GFSK pulse spans 1..4, coded hard Viterbi recovery, dewhitening, LE CTE bit trimming/IQ sampling, and inline/NPZ inputs; noisy-channel and frequency-offset behavior excluded | `tools/ble_ideal_receiver.schema.json` |
| `ble_l2cap` | `bleL2CAPFrameConfig`<br>`bleL2CAPFrame`<br>`bleL2CAPFrameDecode` | `validated` | All eight LE signaling command encoders, fixed CID B-frames, single-segment dynamic CID LE-frames, matching decoders and structured status values | `tools/ble_l2cap.schema.json` |
| `ble_ll_advertising` | `bleLLAdvertisingChannelPDUConfig`<br>`bleLLAdvertisingChannelPDU`<br>`bleLLAdvertisingChannelPDUDecode` | `validated` | Seven legacy advertising PDU types, configuration validation, CRC24, encoding and structured decoding status | `tools/ble_ll_advertising.schema.json` |
| `ble_ll_data` | `bleLLControlPDUConfig`<br>`bleLLDataChannelPDUConfig`<br>`bleLLDataChannelPDU`<br>`bleLLDataChannelPDUDecode` | `validated` | Data and six control opcode PDUs, configuration validation, CRC24, encoding and structured decoding status | `tools/ble_ll_data.schema.json` |
| `ble_network_config` | `bleCSConfig`<br>`bluetoothLEBIGConfig`<br>`bluetoothLECISConfig`<br>`bluetoothLEConnectionConfig`<br>`bluetoothLEGAPConfig`<br>`bluetoothLEPeriodicAdvConfig`<br>`bluetoothMeshFriendshipConfig`<br>`bluetoothMeshProfileConfig` | `validated` | Public constructor defaults and core property validation for eight LE/CS/mesh configurations; node associations and MATLAB object methods excluded | `tools/ble_network_config.schema.json` |
| `ble_packet_decode_status` | `blePacketDecodeStatus` | `validated` | Complete R2026a enum name/code lookup and equality comparison | `tools/ble_packet_decode_status.schema.json` |
| `ble_pcap_writer` | `blePCAPWriter` | `validated` | PCAP 2.4 and PCAPNG capture creation for DLT 251/256 with endian selection, packet/interface/file comments, multiple packets and microsecond timestamps; node callbacks excluded | `tools/ble_pcap_writer.schema.json` |
| `ble_position_estimate` | `blePositionEstimate` | `validated` | 2-D and 3-D angulation, lateration, and distance-angle localization | `tools/ble_position_estimate.schema.json` |
| `ble_waveform` | `bleWaveformGenerator` | `validated` | All four LE PHY modes with coded FEC/S=8/S=2 mapping, whitening and GMSK pulse spans 1..4; ConnectionCTE and LE1M-only ConnectionlessCTE generation supported | `tools/ble_waveform.schema.json` |
| `bluetooth_classic_config` | `bluetoothConnectionConfig`<br>`bluetoothPhyConfig`<br>`bluetoothWaveformConfig`<br>`bluetoothRFPHYTestConfig`<br>`bluetoothTestWaveformConfig` | `validated` | Serializable constructor defaults and core property validation for connection, PHY, waveform, test-waveform and RF-PHY test configurations; advanced MATLAB object methods are excluded | `tools/bluetooth_classic_config.schema.json` |
| `bluetooth_classic_receiver` | `bluetoothIdealReceiver` | `validated` | BR/EDR2M/EDR3M ideal receiver with GFSK/DPSK hard demodulation, HEC/CRC checks, systematic FEC recovery and inline/NPZ inputs; noisy-channel correction excluded | `tools/bluetooth_classic_receiver.schema.json` |
| `bluetooth_classic_waveform` | `bluetoothWaveformGenerator` | `validated` | BR GFSK and EDR2M/EDR3M DPSK packet access code, HEC, CRC, FEC, raised-cosine pulse shaping and slot padding; 16 EDR packet samples checked against MATLAB | `tools/bluetooth_classic_waveform.schema.json` |
| `bluetooth_classic_whitening` | `bluetoothWhiten` | `validated` | x^7+x^4+1 whitening/dewhitening with explicit serializable state and arbitrary nonzero 7-bit initial conditions | `tools/bluetooth_classic_whitening.schema.json` |
| `bluetooth_frequency_hop` | `bluetoothFrequencyHop` | `validated` | All eleven hopping sequence types, 79-channel register bank and AFH remapping | `tools/bluetooth_frequency_hop.schema.json` |
| `bluetooth_nodes` | `bluetoothNode`<br>`bluetoothLENode` | `validated` | Classic/LE node constructors and public RF properties; persistent object methods, event subscriptions and deterministic traffic simulation are provided by bluetooth_session, while complete link-layer protocol simulation remains in progress | `tools/bluetooth_nodes.schema.json` |
| `bluetooth_packet_duration` | `bluetoothPacketDuration` | `validated` | BR, EDR2M, EDR3M, LE1M, LE2M, LE500K and LE125K packet duration for every documented packet type | `tools/bluetooth_packet_duration.schema.json` |
| `bluetooth_path_loss` | `bluetoothPathLoss`<br>`bluetoothPathLossConfig` | `validated` | Outdoor two-ray and Industrial log-normal propagation with scalar/vector RF parameters; deterministic zero-shadowing results match R2026a, while callers can supply shadow_fading_db for reproducible stochastic scenarios | `tools/bluetooth_path_loss.schema.json` |
| `bluetooth_range` | `bluetoothRange`<br>`bluetoothRangeConfig` | `validated` | Outdoor two-ray, Industrial, Home and Office link-budget range inversion with receiver-sensitivity or received-power inputs, including MATLAB-compatible shadow-fading bounds | `tools/bluetooth_range.schema.json` |
| `bluetooth_test_waveform` | `bluetoothTestWaveform` | `validated` | BR/EDR2M/EDR3M and all four LE PHY RF-test waveforms with PRBS9/15 and six repeated patterns, including LE1M/LE2M ConnectionCTE; EDR test lengths and sampled waveforms checked against MATLAB | `tools/bluetooth_test_waveform.schema.json` |
| `bluetooth_test_waveform_validate` | `bluetoothTestWaveformValidate` | `validated` | LE1M/LE2M access-address and CRC verdicts for Blocking, C/I, Intermodulation and PER report integrity plus LE125K/LE500K C/I and PER branches; Modulation characteristics and Carrier frequency offset/drift measurements; CTE IQ coherency and dynamic-range measurement fields; inline/NPZ inputs | `tools/bluetooth_test_waveform_validate.schema.json` |

### Communications Toolbox（30）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `awgn` | `awgn` | `independent_validated` | — | `tools/awgn.schema.json` |
| `bch_code` | `bchenc`<br>`bchdec`<br>`bchgenpoly`<br>`bchnumerr` | `independent_validated` | primitive narrow-sense binary BCH, m=2..8 | `tools/bch_code.schema.json` |
| `ber_awgn` | `berawgn` | `independent_validated` | BPSK/QPSK, square QAM, PAM, PSK, binary DPSK/orthogonal FSK | `tools/ber_awgn.schema.json` |
| `ber_coding` | `bercoding` | `independent_validated` | BPSK convolutional distance-spectrum, binary block and Hamming hard/soft bounds | `tools/ber_coding.schema.json` |
| `ber_fading` | `berfading` | `independent_validated` | coherent BPSK/QPSK, Rayleigh/Rician and MRC diversity | `tools/ber_fading.schema.json` |
| `binary_symmetric_channel` | `bsc` | `independent_validated` | — | `tools/binary_symmetric_channel.schema.json` |
| `bit_int_conversion` | `bit2int`<br>`int2bit` | `independent_validated` | — | `tools/bit_int_conversion.schema.json` |
| `biterr` | `biterr` | `independent_validated` | — | `tools/biterr.schema.json` |
| `convert_snr` | `convertSNR` | `independent_validated` | — | `tools/convert_snr.schema.json` |
| `convolutional_codec` | `convenc`<br>`vitdec`<br>`poly2trellis` | `independent_validated` | rate-1/N, hard Viterbi, encoder puncture | `tools/convolutional_codec.schema.json` |
| `dpsk_modulation` | `dpskmod`<br>`dpskdemod` | `independent_validated` | — | `tools/dpsk_modulation.schema.json` |
| `fading_channel` | `stdchan` | `independent_validated` | memoryless/block flat Rayleigh and Rician subset | `tools/fading_channel.schema.json` |
| `frequency_offset` | `frequencyOffset` | `independent_validated` | — | `tools/frequency_offset.schema.json` |
| `fsk_modulation` | `fskmod`<br>`fskdemod` | `independent_validated` | baseband waveform, noncoherent hard demodulation | `tools/fsk_modulation.schema.json` |
| `hamming_code` | `hammgen`<br>`encode`<br>`decode` | `independent_validated` | systematic-position binary Hamming mode | `tools/hamming_code.schema.json` |
| `interleaver` | `matintrlv`<br>`matdeintrlv`<br>`randintrlv`<br>`randdeintrlv`<br>`intrlv`<br>`deintrlv` | `independent_validated` | — | `tools/interleaver.schema.json` |
| `ofdm_channel_estimate` | `ofdmChannelEstimate` | `independent_validated` | pilot-aided LS with linear frequency/time interpolation | `tools/ofdm_channel_estimate.schema.json` |
| `ofdm_channel_response` | `ofdmChannelResponse` | `independent_validated` | static/slow-varying path-gain averaging, MIMO and active subcarriers | `tools/ofdm_channel_response.schema.json` |
| `ofdm_equalizer` | `ofdmEqualize`<br>`lteEqualizeZF`<br>`lteEqualizeMMSE` | `independent_validated` | per-RE SISO/MIMO ZF and MMSE | `tools/ofdm_equalizer.schema.json` |
| `ofdm_modulation` | `ofdmmod`<br>`ofdmdemod` | `independent_validated` | 1x sampling, nulls and pilots | `tools/ofdm_modulation.schema.json` |
| `pam_modulation` | `pammod`<br>`pamdemod` | `independent_validated` | — | `tools/pam_modulation.schema.json` |
| `psk_modulation` | `pskmod`<br>`pskdemod` | `independent_validated` | — | `tools/psk_modulation.schema.json` |
| `q_function` | `qfunc`<br>`qfuncinv` | `independent_validated` | — | `tools/q_function.schema.json` |
| `qam_modulation` | `qammod`<br>`qamdemod` | `independent_validated` | square power-of-two QAM | `tools/qam_modulation.schema.json` |
| `rectangular_pulse` | `rectpulse` | `independent_validated` | — | `tools/rectangular_pulse.schema.json` |
| `reed_solomon_code` | `rsenc`<br>`rsdec`<br>`rsgenpoly`<br>`rsgenpolycoeffs` | `independent_validated` | GF(2^m), m=2..8, shortened systematic narrow-sense codes | `tools/reed_solomon_code.schema.json` |
| `signal_timing_estimate` | `timingEstimate`<br>`channelDelay` | `independent_validated` | reference correlation and perfect channel delay modes | `tools/signal_timing_estimate.schema.json` |
| `symerr` | `symerr` | `independent_validated` | — | `tools/symerr.schema.json` |
| `white_gaussian_noise` | `wgn` | `independent_validated` | — | `tools/white_gaussian_noise.schema.json` |
| `zadoff_chu_seq` | `zadoffChuSeq` | `independent_validated` | — | `tools/zadoff_chu_seq.schema.json` |

### Wireless Network Toolbox（6）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `node_mobility_constant_velocity` | `nodeMobilityConstantVelocity` | `independent_validated` | stateless trajectory form | `tools/node_mobility_constant_velocity.schema.json` |
| `node_mobility_random_walk` | `nodeMobilityRandomWalk` | `independent_validated` | stateless sampled trajectory form | `tools/node_mobility_random_walk.schema.json` |
| `node_mobility_random_waypoint` | `nodeMobilityRandomWaypoint` | `independent_validated` | stateless sampled trajectory form | `tools/node_mobility_random_waypoint.schema.json` |
| `node_position_grid` | `nodePositionGrid` | `independent_validated` | rectangular-boundary forms | `tools/node_position_grid.schema.json` |
| `node_position_random` | `nodePositionRandom` | `independent_validated` | rectangle and circle forms | `tools/node_position_random.schema.json` |
| `wireless_packet` | `wirelessPacket` | `independent_validated` | — | `tools/wireless_packet.schema.json` |

### WirelessAgent Workflow（8）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `closed_loop_validator` | — | `independent_validated` | weighted KPI comparison, hard constraints and rollback signal | `tools/closed_loop_validator.schema.json` |
| `link_adaptation_optimizer` | — | `independent_validated` | conservative SNR thresholds combined with converted LTE MCS/TBS tables | `tools/link_adaptation_optimizer.schema.json` |
| `link_capacity` | — | `independent_validated` | SISO and equal-power MIMO Shannon bound | `tools/link_capacity.schema.json` |
| `policy_decision_validator` | — | `independent_validated` | QoS rate ordering, aggregate capacity and observed KPI validation | `tools/policy_decision_validator.schema.json` |
| `qos_policy_builder` | — | `independent_validated` | 5QI-oriented service templates and GBR capacity feasibility | `tools/qos_policy_builder.schema.json` |
| `radio_link_diagnosis` | — | `independent_validated` | evidence rules over SNR/EVM/BER/BLER/frequency/timing/delay KPIs | `tools/radio_link_diagnosis.schema.json` |
| `resource_allocation_optimizer` | — | `independent_validated` | weighted marginal TBS PRB allocation | `tools/resource_allocation_optimizer.schema.json` |
| `traffic_steering_optimizer` | — | `independent_validated` | capacity/latency/quality/cost scoring with assignment hysteresis | `tools/traffic_steering_optimizer.schema.json` |

### WirelessAgent Helper（2）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `bluetooth_session` | — | `validated` | SQLite-backed pure-Python Bluetooth configuration/node objects, supported public-method dispatch, deterministic traffic simulation, snapshots and filtered event logs | `tools/bluetooth_session.schema.json` |
| `wireless_utils` | — | `validated` | AWGN noise, BER, theoretical BER, BCC interleaving, Golay sequence | `tools/wireless_utils.schema.json` |

## 参考

- 3GPP TS 36.211 / 36.212（LTE）
- 3GPP TS 38.211 / 38.212 / 38.214（5G NR）
- MATLAB 5G / LTE / Communications / WLAN Toolbox
