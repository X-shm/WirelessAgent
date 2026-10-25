---
name: wireless-toolbox
description: |
  注册表驱动的无线通信工具目录，覆盖 5G NR、LTE、WLAN、通用通信、无线网络和优化工作流。
  当前登记 211 个工具；调用前按 tool_registry.json 的状态、覆盖范围和 schema 选择。
user-invocable: true
---

# Wireless Toolbox

> 此文件由 `scripts/generate_registry_docs.py` 从 `tool_registry.json` 自动生成。
> 请先更新注册表，再执行 `python scripts/generate_registry_docs.py --write`；不要直接编辑本文件。

## 选择与调用规则

1. 先按产品/领域选择工具，并确认其注册 `status` 和 `coverage`。
2. 再读取 `schema` 指定的输入/输出契约；不要从工具名推测支持范围。
3. 调用前执行 `python tools/<tool>.py --help`，特别是有位置子命令的工具。
4. `pending_validation` 只表示注册表中的当前状态，不能当作标准一致性的承诺。
5. Bluetooth Toolbox 当前由 `26` 个 CLI 映射 `52` 个顶层 MATLAB 名称。`validated` 仅表示各工具 `coverage` 所述功能切片通过验证，不代表该名称的全部参数、对象方法、网络仿真或 MATLAB 完整行为均已实现；逐项完成状态和剩余缺口见 `bluetooth_capabilities.json`。

## 注册概览

| 产品/领域 | 工具数 | 注册状态分布 |
|---|---:|---|
| LTE Toolbox | 43 | `validated`: 5，`independent_validated`: 32，`partial`: 6 |
| 5G Toolbox | 58 | `validated`: 20，`independent_validated`: 38 |
| WLAN Toolbox | 18 | `validated`: 4，`independent_validated`: 5，`partial`: 9 |
| Bluetooth Toolbox | 26 | `validated`: 26 |
| Communications Toolbox | 45 | `independent_validated`: 45 |
| Wireless Network Toolbox | 11 | `independent_validated`: 11 |
| WirelessAgent Workflow | 8 | `independent_validated`: 8 |
| WirelessAgent Helper | 2 | `validated`: 2 |

## 注册工具目录

### LTE Toolbox（43）

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
| `lte_downlink_family` | `lteBCH`<br>`lteBCHDecode`<br>`lteCFI`<br>`lteCFIDecode`<br>`lteCSIRS`<br>`lteCSIRSIndices`<br>`lteDCI`<br>`lteDCIDecode`<br>`lteDCIEncode`<br>`lteDCIInfo`<br>`lteDCIResourceAllocation`<br>`lteDLConformanceTestTool`<br>`lteDLPerfectChannelEstimate`<br>`lteDLResourceGrid`<br>`lteDLResourceGridSize`<br>`lteDLSCH`<br>`lteDLSCHDecode`<br>`lteDLSCHInfo`<br>`lteDMRS`<br>`lteDMRSIndices`<br>`lteDuplexingInfo`<br>`lteEPDCCH`<br>`lteEPDCCHDecode`<br>`lteEPDCCHDMRS`<br>`lteEPDCCHDMRSIndices`<br>`lteEPDCCHIndices`<br>`lteEPDCCHPRBS`<br>`lteEPDCCHSearch`<br>`lteEPDCCHSpace`<br>`ltePBCH`<br>`ltePBCHDecode`<br>`ltePBCHIndices`<br>`ltePBCHPRBS`<br>`ltePCFICH`<br>`ltePCFICHDecode`<br>`ltePCFICHIndices`<br>`ltePCFICHInfo`<br>`ltePCFICHPRBS`<br>`ltePDCCH`<br>`ltePDCCHDecode`<br>`ltePDCCHDeinterleave`<br>`ltePDCCHIndices`<br>`ltePDCCHInfo`<br>`ltePDCCHInterleave`<br>`ltePDCCHPRBS`<br>`ltePDCCHSearch`<br>`ltePDCCHSpace`<br>`ltePDSCH`<br>`ltePDSCHDecode`<br>`ltePHICH`<br>`ltePHICHDecode`<br>`ltePHICHDeprecode`<br>`ltePHICHIndices`<br>`ltePHICHInfo`<br>`ltePHICHPRBS`<br>`ltePHICHPrecode`<br>`ltePHICHTransmitDiversityDecode`<br>`ltePRS`<br>`ltePRSIndices` | `partial` | 独立 Python 下行 CFI、PCFICH、FDD PHICH/PDCCH 几何及基线 RE 索引、CSI-RS/PRS 与单层 PDSCH/EPDCCH DM-RS 基线序列及索引、EPDCCH 数据索引、DCI 编解码及对称带宽 DCI 长度、BCH 编解码、单端口 PBCH、PDCCH 交织和资源网格已与 MATLAB 样本对照；非对称带宽与完整多天线调度链仍为部分实现。 | `tools/lte_downlink_family.schema.json` |
| `lte_extract_resources` | `lteExtractResources` | `independent_validated` | 2-D/3-D complex grid, linear/subscript indices | `tools/lte_extract_resources.schema.json` |
| `lte_frame_offset` | `lteDLFrameOffset`<br>`lteULFrameOffset` | `independent_validated` | explicit standard reference waveform correlation core | `tools/lte_frame_offset.schema.json` |
| `lte_frequency_sync` | `lteFrequencyOffset`<br>`lteFrequencyCorrect` | `independent_validated` | CP-correlation estimate with explicit FFT/CP/sample-rate inputs | `tools/lte_frequency_sync.schema.json` |
| `lte_layer_map` | `lteLayerMap`<br>`lteLayerDemap` | `independent_validated` | one/two codewords, 1..8 layers | `tools/lte_layer_map.schema.json` |
| `lte_mcs` | `lteMCS` | `validated` | — | `tools/lte_mcs.schema.json` |
| `lte_mimo_equalizer` | `lteEqualizeMIMO`<br>`lteEqualizeULMIMO` | `independent_validated` | explicit precoder or one/two-port codebook joint MMSE equalization | `tools/lte_mimo_equalizer.schema.json` |
| `lte_misc_family` | `evaluateGUIParameter`<br>`lteMIB`<br>`lteRateMatchTurbo`<br>`lteRateRecoverTurbo`<br>`lteTransmitDiversityDecode`<br>`lteTurboDecode`<br>`lteTurboEncode`<br>`lteWarning`<br>`saLteDLConformanceTestBenchGUI`<br>`saLteNscRB`<br>`saLteParamExpand`<br>`saLteULCtrlEncode`<br>`saProgressBar`<br>`saVectorDataSource` | `partial` | 独立 Python LTE Turbo QPP 编解码、单码块速率匹配/恢复、24 位 MIB 及固定 12 子载波资源块参数已与 MATLAB 样本对照；多码块软缓冲及 GUI 未复现。 | `tools/lte_misc_family.schema.json` |
| `lte_modulation` | `lteSymbolModulate`<br>`lteSymbolDemodulate` | `validated` | — | `tools/lte_modulation.schema.json` |
| `lte_nb_family` | `lteNBDLFrameOffset`<br>`lteNBResourceGrid`<br>`lteNDLSCH`<br>`lteNDLSCHDecode`<br>`lteNPBCH`<br>`lteNPBCHDecode`<br>`lteNPBCHIndices`<br>`lteNPDCCH`<br>`lteNPDCCHDecode`<br>`lteNPDCCHIndices`<br>`lteNPDSCH`<br>`lteNPDSCHDecode`<br>`lteNPDSCHIndices`<br>`lteNPRACH`<br>`lteNPRACHDetect`<br>`lteNPRACHInfo`<br>`lteNPSS`<br>`lteNPSSIndices`<br>`lteNPUSCH`<br>`lteNPUSCHDecode`<br>`lteNPUSCHDRS`<br>`lteNPUSCHDRSIndices`<br>`lteNPUSCHIndices`<br>`lteNRS`<br>`lteNRSIndices`<br>`lteNSSS`<br>`lteNSSSIndices`<br>`lteNULSCH`<br>`lteNULSCHDecode` | `partial` | 独立 Python NB-IoT NPSS/NSSS/NRS 序列及索引、NB 资源网格、NPBCH/NPDSCH/NPDCCH 索引、FDD NPUSCH 数据/DRS 索引及 Data DRS 基线序列、基线 NPRACHInfo 已与 MATLAB 样本对照；NPRACHInfo 仅支持登记的 FDD 基线配置，其余 NB-IoT 信道编码仍为部分实现。 | `tools/lte_nb_family.schema.json` |
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
| `lte_sidelink_family` | `ltePSBCH`<br>`ltePSBCHDecode`<br>`ltePSBCHDRS`<br>`ltePSBCHDRSIndices`<br>`ltePSBCHIndices`<br>`ltePSBCHPRBS`<br>`ltePSCCH`<br>`ltePSCCHDecode`<br>`ltePSCCHDRS`<br>`ltePSCCHDRSIndices`<br>`ltePSCCHIndices`<br>`ltePSCCHPRBS`<br>`ltePSSCH`<br>`ltePSSCHDecode`<br>`ltePSSCHDRS`<br>`ltePSSCHDRSIndices`<br>`ltePSSCHIndices`<br>`ltePSSCHPRBS`<br>`ltePSSS`<br>`ltePSSSIndices`<br>`lteSCI`<br>`lteSCIDecode`<br>`lteSCIEncode`<br>`lteSCIInfo`<br>`lteSCIResourceAllocation`<br>`lteSLBCH`<br>`lteSLBCHDecode`<br>`lteSLChannelEstimatePSBCH`<br>`lteSLChannelEstimatePSCCH`<br>`lteSLChannelEstimatePSSCH`<br>`lteSLFrameOffsetPSBCH`<br>`lteSLFrameOffsetPSCCH`<br>`lteSLFrameOffsetPSSCH`<br>`lteSLMIB`<br>`lteSLResourceGrid`<br>`lteSLResourceGridSize`<br>`lteSLSCFDMADemodulate`<br>`lteSLSCFDMAInfo`<br>`lteSLSCFDMAModulate`<br>`lteSLSCH`<br>`lteSLSCHDecode`<br>`lteSSSS`<br>`lteSSSSIndices` | `partial` | 独立 Python Sidelink MIB、PSSS/SSSS、PSBCH/PSCCH/PSSCH 资源索引与物理信道编解码、SCI/SL-BCH 编解码、三类 DRS 验证配置、PRBS 及 SC-FDMA 几何已与 MATLAB 样本对照；其余估计和完整多天线链仍为部分实现。 | `tools/lte_sidelink_family.schema.json` |
| `lte_srs` | `lteSRS`<br>`lteSRSIndices` | `independent_validated` | single antenna, explicit contiguous >=6 PRBs, no ConfigIdx/hopping | `tools/lte_srs.schema.json` |
| `lte_sss` | `lteSSS` | `independent_validated` | — | `tools/lte_sss.schema.json` |
| `lte_standard_fading` | `lteFadingChannel` | `independent_validated` | EPA/EVA/ETU SISO or parallel-channel Rayleigh subset with correlated Doppler approximation | `tools/lte_standard_fading.schema.json` |
| `lte_sync_indices` | `ltePSSIndices`<br>`lteSSSIndices` | `independent_validated` | FDD subframes 0/5, normal and extended CP | `tools/lte_sync_indices.schema.json` |
| `lte_tbs` | `lteTBS` | `validated` | — | `tools/lte_tbs.schema.json` |
| `lte_ul_channel_estimate` | `lteULChannelEstimate` | `independent_validated` | single-layer PUSCH DM-RS allocated-PRB estimate | `tools/lte_ul_channel_estimate.schema.json` |
| `lte_ul_precode` | `lteULPrecode`<br>`lteULDeprecode` | `independent_validated` | PRB/subcarrier normalized block DFT and inverse | `tools/lte_ul_precode.schema.json` |
| `lte_ul_scrambling` | `lteULScramble`<br>`lteULDescramble` | `independent_validated` | transport data without UCI placeholders | `tools/lte_ul_scrambling.schema.json` |
| `lte_uplink_family` | `lteACKDecode`<br>`lteACKEncode`<br>`lteCQIDecode`<br>`lteCQIEncode`<br>`ltePUCCH1`<br>`ltePUCCH1Decode`<br>`ltePUCCH1DRS`<br>`ltePUCCH1DRSIndices`<br>`ltePUCCH1Indices`<br>`ltePUCCH2`<br>`ltePUCCH2Decode`<br>`ltePUCCH2DRS`<br>`ltePUCCH2DRSDecode`<br>`ltePUCCH2DRSIndices`<br>`ltePUCCH2Indices`<br>`ltePUCCH2PRBS`<br>`ltePUCCH3`<br>`ltePUCCH3Decode`<br>`ltePUCCH3DRS`<br>`ltePUCCH3DRSIndices`<br>`ltePUCCH3Indices`<br>`ltePUCCH3PRBS`<br>`ltePUSCH`<br>`ltePUSCHDecode`<br>`ltePUSCHDeprecode`<br>`ltePUSCHPrecode`<br>`lteRIDecode`<br>`lteRIEncode`<br>`lteSRSInfo`<br>`lteUCI3Decode`<br>`lteUCI3Encode`<br>`lteUCIDecode`<br>`lteUCIEncode`<br>`lteULChannelEstimateNPUSCH`<br>`lteULChannelEstimatePUCCH1`<br>`lteULChannelEstimatePUCCH2`<br>`lteULChannelEstimatePUCCH3`<br>`lteULFrameOffsetNPUSCH`<br>`lteULFrameOffsetPUCCH1`<br>`lteULFrameOffsetPUCCH2`<br>`lteULFrameOffsetPUCCH3`<br>`lteULPerfectChannelEstimate`<br>`lteULPMIInfo`<br>`lteULPMISelect`<br>`lteULResourceGrid`<br>`lteULResourceGridSize`<br>`lteULSCH`<br>`lteULSCHDecode`<br>`lteULSCHDeinterleave`<br>`lteULSCHInfo`<br>`lteULSCHInterleave` | `partial` | 独立 Python 上行 PUCCH2/3 PRBS、PUCCH1/2/3 数据/DRS 索引及 DRS 序列、ACK/RI/CQI 短块编解码、UCI/UCI3 全合法长度编码和 1..11 位软解码、SRS 小区子帧调度、无 UCI 的 UL-SCH 交织及 61 个 PUSCH MIMO 码本已与 MATLAB 样本对照；完整 PUSCH 传输处理和多层复用仍为部分实现。 | `tools/lte_uplink_family.schema.json` |
| `lte_waveform_family` | `lte3DChannel`<br>`lteDownlinkRMCGenerator`<br>`lteHSTChannel`<br>`lteMovingChannel`<br>`ltePRACH`<br>`ltePRACHDetect`<br>`ltePRACHInfo`<br>`lteRMCDL`<br>`lteRMCDLTool`<br>`lteRMCUL`<br>`lteRMCULTool`<br>`lteTestModel`<br>`lteTestModelGenerator`<br>`lteTestModelTool`<br>`lteThroughputAnalyzer`<br>`lteUplinkRMCGenerator` | `partial` | 独立 Python 已提供基线 FDD PRACHInfo 几何、FDD/TDD RMC 与 E-TM 预设及显式抽头 FIR、参考相关和吞吐率计算；PRACHInfo 仅支持登记的标准带宽/格式基线配置，完整 3D/HST 随机信道和图形界面仍不支持。 | `tools/lte_waveform_family.schema.json` |

### 5G Toolbox（58）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `nr_bch_codec` | `nrBCH`<br>`nrBCHDecode` | `independent_validated` | 独立 Python BCH 32 位载荷交织、Gold 扰码、CRC24C、Polar 编码与 SC(L=1) 解码，固定 864 位码字。 | `tools/nr_bch_codec.schema.json` |
| `nr_channel_estimate` | `nrChannelEstimate` | `independent_validated` | Single reference port, one normal/extended-CP slot, sparse least-squares estimate with Interpolation=off and CDMLengths=[1,1]; interpolation, CDM despreading and PRG noise estimates are not included | `tools/nr_channel_estimate.schema.json` |
| `nr_channel_models` | `nrTDLChannel`<br>`nrCDLChannel`<br>`nrHSTChannel`<br>`nrPathLoss`<br>`nrPerfectChannelEstimate`<br>`nrPhaseNoise` | `independent_validated` | 独立 Python 显式路径信道子集；不包含 MATLAB 预设 TDL/CDL/HST 配置和相位噪声多极点模型。 | `tools/nr_channel_models.schema.json` |
| `nr_channel_prbs` | `nrPBCHPRBS`<br>`nrPDSCHPRBS`<br>`nrPUSCHPRBS`<br>`nrPUCCHPRBS` | `independent_validated` | PBCH phase, PDSCH/PUSCH codeword and PUCCH base scrambling sequences; PUSCH msgA nrapid extension is not included | `tools/nr_channel_prbs.schema.json` |
| `nr_config` | `nrCarrierConfig`<br>`nrCORESETConfig`<br>`nrCSIReportConfig`<br>`nrCSIRSConfig`<br>`nrDLCarrierConfig`<br>`nrIntraCellGuardBandsConfig`<br>`nrPathLossConfig`<br>`nrPDCCHConfig`<br>`nrPDSCHConfig`<br>`nrPDSCHDMRSConfig`<br>`nrPDSCHPTRSConfig`<br>`nrPDSCHReservedConfig`<br>`nrPRACHConfig`<br>`nrPRSConfig`<br>`nrPUCCH0Config`<br>`nrPUCCH1Config`<br>`nrPUCCH2Config`<br>`nrPUCCH3Config`<br>`nrPUCCH4Config`<br>`nrPUSCHConfig`<br>`nrPUSCHDMRSConfig`<br>`nrPUSCHPTRSConfig`<br>`nrSCSCarrierConfig`<br>`nrSearchSpaceConfig`<br>`nrSRSConfig`<br>`nrULCarrierConfig`<br>`nrWavegenBWPConfig`<br>`nrWavegenCSIRSConfig`<br>`nrWavegenPDCCHConfig`<br>`nrWavegenPDSCHConfig`<br>`nrWavegenPUCCH0Config`<br>`nrWavegenPUCCH1Config`<br>`nrWavegenPUCCH2Config`<br>`nrWavegenPUCCH3Config`<br>`nrWavegenPUCCH4Config`<br>`nrWavegenPUSCHConfig`<br>`nrWavegenSRSConfig`<br>`nrWavegenSSBurstConfig` | `independent_validated` | 38 JSON configuration constructors with R2026a defaults and known-property overrides; MATLAB class validation and dependent property updates are only partially reproduced | `tools/nr_config.schema.json` |
| `nr_control_codec` | `nrDCIDecode`<br>`nrUCIEncode`<br>`nrUCIDecode` | `independent_validated` | 独立 Python 控制信息 Polar 编解码。DCI 使用 SC(L=1) 和 CRC24C；UCI 支持 12..1012 位未分段 Polar 分支及上行三角交织。 | `tools/nr_control_codec.schema.json` |
| `nr_crc` | `nrCRCEncode`<br>`nrCRCDecode` | `validated` | — | `tools/nr_crc.schema.json` |
| `nr_csi_resources` | `nrCSIMeasurementsSRS`<br>`nrCSIReportCSIRS`<br>`nrCSIRSIndices`<br>`nrCSIRSMeasurements` | `independent_validated` | 独立 Python 单端口 CSI 资源及宽带质量估计子集；CQI 为 Shannon 界近似，不等同 MATLAB 的完整码本报告。 | `tools/nr_csi_resources.schema.json` |
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
| `nr_pdcch_resources` | `nrPDCCHResources`<br>`nrPDCCHSpace` | `independent_validated` | 独立 Python 单符号、非交织 CORESET 资源映射；每 CCE 为 6 REG，每 REG 为 9 数据 RE 加 3 DM-RS RE。 | `tools/nr_pdcch_resources.schema.json` |
| `nr_pdsch` | `nrPDSCH`<br>`nrDLSCH` | `validated` | end-to-end PDSCH TX/RX cascade: CRC→LDPC→RM→modulation→layer map→OFDM | `tools/nr_pdsch.schema.json` |
| `nr_pdsch_decode` | `nrPDSCHDecode` | `independent_validated` | Direct symbol syntax for one codeword and 1..4 layers, max-log LLR; two-codeword and carrier/config-object forms are not included | `tools/nr_pdsch_decode.schema.json` |
| `nr_pdsch_grid_indices` | `nrPDSCHDMRSIndices`<br>`nrPDSCHIndices` | `independent_validated` | One layer/port, explicit DM-RS symbols, carrier PRB allocation, type-1/2 CDM reservation; no PTRS, VRB interleaving, reserved RE or multiport mapping | `tools/nr_pdsch_grid_indices.schema.json` |
| `nr_pdsch_precode` | `nrPDSCHPrecode` | `independent_validated` | Matrix-valued PDSCH symbols with identical RE positions per layer, arbitrary antennas and PRG-specific complex weights; 3-D channel-estimate tensor syntax is not included | `tools/nr_pdsch_precode.schema.json` |
| `nr_perfect_timing` | `nrPerfectTimingEstimate` | `independent_validated` | Perfect timing offset and per-receive-antenna impulse-response magnitude from four-dimensional path gains and real path filters | `tools/nr_perfect_timing.schema.json` |
| `nr_polar` | `nrPolarEncode` | `validated` | Polar mother-code encoding for downlink/uplink; decoding is provided by nr_polar_decode | `tools/nr_polar.schema.json` |
| `nr_polar_decode` | `nrPolarDecode` | `independent_validated` | L=1 successive-cancellation decoding of rate-recovered Polar mother-code LLRs with optional output deinterleaving; CRC-aided list decoding L>1 is not included | `tools/nr_polar_decode.schema.json` |
| `nr_polar_rm` | `nrRateMatchPolar`<br>`nrRateRecoverPolar` | `independent_validated` | Polar rate match/recover: subblock interleave + bit selection (puncture/repeat/shorten) | `tools/nr_polar_rm.schema.json` |
| `nr_prach_family` | `nrPRACH`<br>`nrPRACHDetect`<br>`nrPRACHGrid`<br>`nrPRACHIndices`<br>`nrPRACHOFDMInfo`<br>`nrPRACHOFDMModulate` | `independent_validated` | 独立 Python 单个 PRACH 时频机会处理；支持 139/839 点 Zadoff-Chu 序列，显式物理根序号及循环移位。 | `tools/nr_prach_family.schema.json` |
| `nr_prbs` | `nrPRBS` | `validated` | Gold code PRBS generator, cinit init, binary/signed output | `tools/nr_prbs.schema.json` |
| `nr_prg_info` | `nrPRGInfo` | `independent_validated` | PRG sizes 2 or 4 and wideband, with NStartGrid/NSizeGrid carrier geometry | `tools/nr_prg_info.schema.json` |
| `nr_prs` | `nrPRS`<br>`nrPRSIndices` | `independent_validated` | Single active PRS resource in a normal-CP carrier slot; comb sizes 2/4/6/12, resource RB and symbol allocation, sequence ID and slot; resource-set periodicity, repetitions, muting and multiple resources are not included | `tools/nr_prs.schema.json` |
| `nr_pss` | `nrPSS`<br>`nrPSSIndices` | `validated` | PSS m-sequence generation + RE indices | `tools/nr_pss.schema.json` |
| `nr_ptrs_family` | `nrPDSCHPTRS`<br>`nrPDSCHPTRSIndices`<br>`nrPUSCHPTRS`<br>`nrPUSCHPTRSIndices` | `independent_validated` | 独立 Python 单端口、无变换预编码 PT-RS 子集；需要显式给出 RB、DM-RS 符号与时频密度。 | `tools/nr_ptrs_family.schema.json` |
| `nr_pucch_family` | `nrPUCCH`<br>`nrPUCCH0`<br>`nrPUCCH1`<br>`nrPUCCH2`<br>`nrPUCCH3`<br>`nrPUCCH4`<br>`nrPUCCHDecode`<br>`nrPUCCHDMRS`<br>`nrPUCCHDMRSIndices`<br>`nrPUCCHHoppingInfo`<br>`nrPUCCHIndices` | `independent_validated` | 独立 Python 单 RB PUCCH 0..4 基本调制、资源、DM-RS 与无噪声解调子集；格式 1 支持单时隙循环移位跳变和 1/2 位调制，不覆盖完整频跳、码本和 UCI 编码。 | `tools/nr_pucch_family.schema.json` |
| `nr_pusch` | `nrPUSCH`<br>`nrPUSCHDecode` | `independent_validated` | PUSCH scramble + modulation + layer map; optional DFT-s-OFDM transform precoding | `tools/nr_pusch.schema.json` |
| `nr_pusch_codebook` | `nrPUSCHCodebook` | `independent_validated` | All 4542 valid R2026a layer/port/TPMI/transform/codebook-type combinations for 1, 2, 4 and 8 ports; R2026b three-port addition is not included | `tools/nr_pusch_codebook.schema.json` |
| `nr_pusch_ref` | `nrPUSCHDMRS`<br>`nrPUSCHDMRSIndices`<br>`nrPUSCHIndices` | `independent_validated` | PUSCH DM-RS sequence and data RE indices for one BWP allocation | `tools/nr_pusch_ref.schema.json` |
| `nr_pusch_scrambling` | `nrPUSCHScramble`<br>`nrPUSCHDescramble` | `independent_validated` | Single-codeword binary bits or soft LLRs, including q=0/1; no UCI X/Y placeholders or msgA nrapid | `tools/nr_pusch_scrambling.schema.json` |
| `nr_sch_info` | `nrDLSCHInfo`<br>`nrULSCHInfo` | `independent_validated` | Scalar TBS/TCR coding dimensions; UL-SCH UCI multiplexing and two-codeword forms are not included | `tools/nr_sch_info.schema.json` |
| `nr_sch_transport` | `nrDLSCHDecoder`<br>`nrULSCH`<br>`nrULSCHDecoder`<br>`nrULSCHDemultiplex`<br>`nrULSCHMultiplex` | `independent_validated` | 独立 Python 单 LDPC 码块共享信道子集；复用现有 CRC/LDPC 并显式处理 filler、速率匹配。UCI 复用仅支持显式插入位置。 | `tools/nr_sch_transport.schema.json` |
| `nr_srs` | `nrSRS`<br>`nrSRSIndices` | `independent_validated` | Zadoff-Chu SRS sequence and comb-based resource indices | `tools/nr_srs.schema.json` |
| `nr_ssb_measurements` | `nrSSBMeasurements` | `independent_validated` | 240x4 SSB grid, per-Rx RSRP/RSSI/RSRQ, optional PBCH DM-RS contribution; phase-correction option is not included | `tools/nr_ssb_measurements.schema.json` |
| `nr_sss` | `nrSSS`<br>`nrSSSIndices` | `validated` | SSS dual m-sequence generation + RE indices | `tools/nr_sss.schema.json` |
| `nr_tables` | `nrCQITables`<br>`nrPUSCHMCSTables` | `independent_validated` | Four CQI tables and five default PUSCH MCS tables from R2026a; PUSCHMCSTables property-dependent variants are not included | `tools/nr_tables.schema.json` |
| `nr_tbs` | `nrTBS` | `validated` | Transport block size determination per TS 38.214 | `tools/nr_tbs.schema.json` |
| `nr_timing_estimate` | `nrTimingEstimate` | `validated` | cross-correlation timing estimate; direct waveform pair or built-in NR reference grid | `tools/nr_timing_estimate.schema.json` |
| `nr_transform` | `nrTransformPrecode`<br>`nrTransformDeprecode` | `independent_validated` | Unitary 12×MRB DFT/IFFT per column, all integer MRB and row counts divisible by 12×MRB | `tools/nr_transform.schema.json` |
| `nr_waveform_io` | `nrWaveformAnalyzer`<br>`nrWaveformGenerator` | `independent_validated` | 独立 Python 单 numerology 资源网格 OFDM 波形生成和分析子集；分析器返回资源网格、PAPR 与频谱。 | `tools/nr_waveform_io.schema.json` |

### WLAN Toolbox（18）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `wlan_bcc` | `wlanBCCEncode`<br>`wlanBCCDecode` | `validated` | — | `tools/wlan_bcc.schema.json` |
| `wlan_bit_recovery` | `wlanDMGDataBitRecover`<br>`wlanDMGHeaderBitRecover`<br>`wlanEHTDataBitRecover`<br>`wlanEHTSIGCommonBitRecover`<br>`wlanEHTSIGUserBitRecover`<br>`wlanHEDataBitRecover`<br>`wlanHESIGABitRecover`<br>`wlanHESIGBCommonBitRecover`<br>`wlanHESIGBUserBitRecover`<br>`wlanLSIGBitRecover`<br>`wlanNonHTDataBitRecover`<br>`wlanUSIGBitRecover`<br>`wlanVHTDataBitRecover`<br>`wlanVHTSIGABitRecover`<br>`wlanVHTSIGBBitRecover`<br>`wlanHTDataRecover`<br>`wlanHTSIGRecover`<br>`wlanLSIGRecover`<br>`wlanNonHTDataRecover`<br>`wlanVHTDataRecover`<br>`wlanVHTSIGARecover`<br>`wlanVHTSIGBRecover` | `partial` | 独立 Python 显式均衡符号的 Gray 硬/软解映射，可选 BCC 与扰码逆变换及 L-SIG 字段解析；未覆盖格式专用 LDPC、去交织和全信令字段校验。 | `tools/wlan_bit_recovery.schema.json` |
| `wlan_bit_routing` | `wlanBCCInterleave`<br>`wlanBCCDeinterleave`<br>`wlanStreamParse`<br>`wlanStreamDeparse`<br>`wlanSegmentParseBits`<br>`wlanSegmentDeparseBits`<br>`wlanSegmentParseSymbols`<br>`wlanSegmentDeparseSymbols` | `partial` | 独立 Python 可逆 BCC 交织、空间流和双段路由；支持 Non-HT 及单空间流 VHT 基础置换，未覆盖所有空间流旋转与标准例外。 | `tools/wlan_bit_routing.schema.json` |
| `wlan_cfo_estimate` | `wlanFineCFOEstimate`<br>`wlanCoarseCFOEstimate` | `independent_validated` | L-STF coarse and L-LTF fine carrier frequency offset estimates | `tools/wlan_cfo_estimate.schema.json` |
| `wlan_channel_waveform` | `wlanTGacChannel`<br>`wlanTGahChannel`<br>`wlanTGaxChannel`<br>`wlanTGayChannel`<br>`wlanTGnChannel`<br>`wlanWaveformAnalyzer`<br>`wlanWaveformGenerator` | `partial` | 独立 Python 显式抽头的单链路 Rayleigh/Rician 信道及 20 MHz 单流 Non-HT PPDU 生成/分析；未实现 TG 标准完整统计配置、MIMO 和 HE/EHT 波形。 | `tools/wlan_channel_waveform.schema.json` |
| `wlan_config_family` | `wlanDMGConfig`<br>`wlanEHTMUConfig`<br>`wlanEHTRecoveryConfig`<br>`wlanEHTRU`<br>`wlanEHTTBConfig`<br>`wlanEHTUser`<br>`wlanHEMUConfig`<br>`wlanHEMURU`<br>`wlanHEMUUser`<br>`wlanHERecoveryConfig`<br>`wlanHESUConfig`<br>`wlanHETBConfig`<br>`wlanHTConfig`<br>`wlanMACFrameConfig`<br>`wlanMACManagementConfig`<br>`wlanMACTriggerConfig`<br>`wlanMACTriggerUserConfig`<br>`wlanNonHTConfig`<br>`wlanS1GConfig`<br>`wlanURAConfig`<br>`wlanVHTConfig`<br>`wlanWURConfig`<br>`wlanWURSubchannel`<br>`wlan.type.ChannelCoding`<br>`wlan.type.EHTPPDUType`<br>`wlan.type.PostFECPaddingSource`<br>`wlan.type.RecoveredChannelCoding`<br>`wlan.type.SpatialMapping`<br>`wlan.type.uhrChannelCoding` | `partial` | 独立 Python 配置 JSON 描述、常用属性校验与带宽/MCS 派生；六个 wlan.type 枚举按本机 MATLAB 常量实现。未覆盖 MATLAB 配置对象的全部跨属性约束和方法。 | `tools/wlan_config_family.schema.json` |
| `wlan_constellation` | `wlanConstellationMap`<br>`wlanConstellationDemap` | `independent_validated` | IEEE 802.11 constellation map/demap BPSK..4096QAM, Gray and hard/soft demap | `tools/wlan_constellation.schema.json` |
| `wlan_golay` | `wlanGolaySequence` | `independent_validated` | 802.11ad Golay complementary Ga/Gb pairs, lengths 32/64/128 | `tools/wlan_golay.schema.json` |
| `wlan_ldpc` | — | `validated` | WLAN LDPC 编解码辅助能力；本机 R2026a 不存在 wlanLDPCEncode/wlanLDPCDecode 公开入口，不计入公开函数映射。 | `tools/wlan_ldpc.schema.json` |
| `wlan_mac_family` | `wlanAMPDUDeaggregate`<br>`wlanFieldIndices`<br>`wlanFormatDetect`<br>`wlanMACDecodeStatus`<br>`wlanMACFrame`<br>`wlanMPDUDecode` | `partial` | 独立 Python 单数据帧 MAC/FCS、A-MPDU 分隔符、MAC 状态枚举和 Non-HT/HT/VHT 字段样本索引；未覆盖所有管理/控制帧与 HE/EHT 字段。 | `tools/wlan_mac_family.schema.json` |
| `wlan_numeric_family` | `wlanAPEPLength`<br>`wlanChannelFrequency`<br>`wlanClosestReferenceSymbol`<br>`wlanHETBNDPFeedbackStatus`<br>`wlanInterpretScramblerState`<br>`wlanMSDULengths`<br>`wlanPSDULength`<br>`wlanReferenceSymbols`<br>`wlanSampleRate`<br>`wlanSpectralFlatness` | `partial` | 独立 Python 中心频率、样本率、星座、扰码带宽状态、载荷长度和频谱计算；长度与平坦度采用显式常用参数子集，未涵盖完整 PHY 配置。 | `tools/wlan_numeric_family.schema.json` |
| `wlan_ofdm_family` | `wlanDMGOFDMInfo`<br>`wlanEHTOFDMInfo`<br>`wlanHEOFDMInfo`<br>`wlanHTOFDMInfo`<br>`wlanS1GOFDMInfo`<br>`wlanVHTOFDMInfo`<br>`wlanDMGOFDMDemodulate`<br>`wlanEHTDemodulate`<br>`wlanHEDemodulate`<br>`wlanHTLTFDemodulate`<br>`wlanLLTFDemodulate`<br>`wlanNonHTOFDMDemodulate`<br>`wlanS1GDemodulate`<br>`wlanVHTDemodulate`<br>`wlanVHTLTFDemodulate` | `partial` | 独立 Python FFT/CP/采样率几何和给定子载波索引的复数 FFT 解调；字段专属导频、RU 分配和多天线解调未覆盖。 | `tools/wlan_ofdm_family.schema.json` |
| `wlan_ofdm_info` | `wlanNonHTOFDMInfo` | `independent_validated` | Non-HT OFDM parameters for L-LTF/L-SIG/NonHT-Data at 20/40 MHz | `tools/wlan_ofdm_info.schema.json` |
| `wlan_packet_detect` | `wlanPacketDetect` | `independent_validated` | Schmidl-Cox L-STF autocorrelation packet detect with offset and decision metric | `tools/wlan_packet_detect.schema.json` |
| `wlan_receiver_family` | `wlanEHTLTFChannelEstimate`<br>`wlanHELTFChannelEstimate`<br>`wlanHTLTFChannelEstimate`<br>`wlanLLTFChannelEstimate`<br>`wlanPreEHTChannelEstimate`<br>`wlanPreHEChannelEstimate`<br>`wlanVHTLTFChannelEstimate`<br>`wlanEHTDataNoiseEstimate`<br>`wlanHEDataNoiseEstimate`<br>`wlanLLTFNoiseEstimate`<br>`wlanEHTEqualize`<br>`wlanHEEqualize`<br>`wlanVHTEqualize`<br>`wlanEHTTrackPilotError`<br>`wlanHETrackPilotError`<br>`wlanVHTTrackPilotError` | `partial` | 独立 Python 显式参考符号的 SISO LS 信道/噪声估计、MMSE/ZF 均衡与公共导频相位校正；未实现完整多流、RU 和格式专用插值。 | `tools/wlan_receiver_family.schema.json` |
| `wlan_scramble` | `wlanScramble` | `validated` | wlanScramble 及同运算的 Python 解扰模式；本机 MATLAB 无单独 wlanDescramble 入口。 | `tools/wlan_scramble.schema.json` |
| `wlan_signal_fields` | `wlanLSTF`<br>`wlanHTSTF`<br>`wlanHTLTF`<br>`wlanVHTSTF`<br>`wlanVHTLTF`<br>`wlanLSIG`<br>`wlanHTSIG`<br>`wlanVHTSIGA`<br>`wlanVHTSIGB`<br>`wlanNonHTData`<br>`wlanHTData`<br>`wlanVHTData` | `partial` | 独立 Python 20 MHz 单天线 L-STF、L-SIG 和 Non-HT 数据链与 MATLAB 黄金样本一致；HT/VHT 训练字段提供本机 R2026a 静态默认波形，HT/VHT 信令和数据仍为单流子集。 | `tools/wlan_signal_fields.schema.json` |
| `wlan_symbol_timing` | `wlanSymbolTimingEstimate`<br>`wlanLLTF` | `validated` | L-LTF cross-correlation timing with CSD-aware multi-bandwidth L-LTF generation | `tools/wlan_symbol_timing.schema.json` |

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

### Communications Toolbox（45）

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
| `comm_analog_modulation` | `ammod`<br>`amdemod`<br>`fmmod`<br>`fmdemod`<br>`pmmod`<br>`pmdemod`<br>`ssbmod`<br>`ssbdemod` | `independent_validated` | 独立 Python 实信号 AM/FM/PM/SSB 采样调制和解析信号相干解调；带限消息、无噪声回环，不实现 MATLAB 可选滤波器配置。 | `tools/comm_analog_modulation.schema.json` |
| `comm_analysis_family` | `berfit`<br>`bersync`<br>`eyediagram`<br>`scatterplot`<br>`semianalytic` | `independent_validated` | 独立 Python 单调 BER 插值、BPSK 同步误差积分、无图形界面的眼图/星座坐标及确定种子的 AWGN BER 估计；半解析估计仅支持 PSK/QAM 一采样符号。 | `tools/comm_analysis_family.schema.json` |
| `comm_crc_family` | `crcConfig`<br>`crcGenerate`<br>`crcDetect` | `independent_validated` | 独立 Python 可配置二进制多项式 CRC、初始位、输入字节和校验和反射、最终 XOR 及一帧多个校验和；不覆盖 direct_method 和 MATLAB 对象生命周期。 | `tools/comm_crc_family.schema.json` |
| `comm_cyclic_trellis` | `cyclgen`<br>`cyclpoly`<br>`gen2par`<br>`syndtable`<br>`istrellis`<br>`iscatastrophic`<br>`distspec`<br>`shift2mask`<br>`mask2shift` | `independent_validated` | 独立 Python GF(2) 循环码、系统矩阵、综合表、网格结构和有限深度距离谱；LFSR 使用明确的 Python 掩码约定，未验证与 MATLAB 全部位序一致。 | `tools/comm_cyclic_trellis.schema.json` |
| `comm_digital_modulation` | `apskmod`<br>`apskdemod`<br>`genqammod`<br>`genqamdemod`<br>`mil188qammod`<br>`mil188qamdemod`<br>`mskmod`<br>`mskdemod` | `independent_validated` | 独立 Python 自然索引同心环 APSK、任意星座最近邻 QAM、MATLAB R2026a MIL-188 完整星座查表及连续相位 MSK 无噪声切片；不覆盖所有 MATLAB 位输入与滤波选项。 | `tools/comm_digital_modulation.schema.json` |
| `comm_doppler_family` | `flatir`<br>`gaussianir`<br>`jakesir`<br>`bellir`<br>`roundedir`<br>`bigaussianir`<br>`rjakesir`<br>`ajakesir`<br>`doppler` | `independent_validated` | 独立 Python Flat/Gaussian/Jakes 闭式脉冲响应和 Bell/Rounded/BiGaussian/RJakes/AJakes 显式谱近似；返回单位能量序列及 Doppler 配置，不覆盖 MATLAB fading 对象。 | `tools/comm_doppler_family.schema.json` |
| `comm_galois_family` | `gf`<br>`gfdiv`<br>`gfsub`<br>`gflineq`<br>`gfrank`<br>`gfrepcov`<br>`gfpretty`<br>`cosets`<br>`gfcosets`<br>`gfprimck`<br>`isprimitive`<br>`gfprimdf`<br>`gfprimfd`<br>`primpoly`<br>`gftable`<br>`gftuple`<br>`gfroots`<br>`gfweight`<br>`gfminpol` | `independent_validated` | 独立 Python GF(2^m) m=2..8 算术、素域线性代数、二元陪集、原始多项式、最小多项式、根和码重；不覆盖 MATLAB gf 对象的所有数组运算和文件型 gftable 副作用。 | `tools/comm_galois_family.schema.json` |
| `comm_gsm_family` | `gsmDownlinkBurstType`<br>`gsmUplinkBurstType`<br>`gsmDownlinkConfig`<br>`gsmUplinkConfig`<br>`gsmInfo`<br>`gsmFrame`<br>`gsmCheckTimeMask` | `independent_validated` | 独立 Python GSM 配置、时隙长度、简化 GMSK 帧和包络检查；未复现标准 AB/SB 训练序列及 MATLAB 完整时间模板。 | `tools/comm_gsm_family.schema.json` |
| `comm_interleaver_family` | `algintrlv`<br>`algdeintrlv`<br>`convintrlv`<br>`convdeintrlv`<br>`muxintrlv`<br>`muxdeintrlv`<br>`helintrlv`<br>`heldeintrlv`<br>`helscanintrlv`<br>`helscandeintrlv` | `independent_validated` | 独立 Python Takeshita-Costello/Welch-Costas 代数置换、零填充移位寄存器、矩阵加复用螺旋交织和螺旋扫描；支持单列数据和显式流 state。 | `tools/comm_interleaver_family.schema.json` |
| `comm_ldpc_family` | `dvbs2ldpc`<br>`ldpcPCM`<br>`ldpcQuasiCyclicMatrix`<br>`ldpcEncoderConfig`<br>`ldpcDecoderConfig`<br>`ldpcEncode`<br>`ldpcDecode` | `independent_validated` | 独立 Python 11 个 DVB-S2 静态校验节点表、WLAN/显式矩阵、准循环展开、系统编码与 min-sum 译码；通用矩阵编码限制 2048 个校验位。 | `tools/comm_ldpc_family.schema.json` |
| `comm_legacy_numeric` | `bi2de`<br>`de2bi`<br>`hex2poly`<br>`oct2poly`<br>`noisebw`<br>`modnorm`<br>`vec2mat`<br>`randerr`<br>`randsrc`<br>`compand`<br>`quantiz`<br>`berconfint` | `independent_validated` | 独立 Python 二进制/多项式转换、等效噪声带宽、星座归一化、填充重排、指定行误差数随机图样、离散随机源、压扩、标量量化及精确二项式 BER 区间；仅覆盖 schema 和函数签名列出的数值切片。 | `tools/comm_legacy_numeric.schema.json` |
| `comm_misc_family` | `checkinp`<br>`intdump`<br>`comm_links`<br>`commlib`<br>`commprivate`<br>`comms`<br>`vita49Reader` | `independent_validated` | 独立 Python 输入默认值、积分清零、VITA 49 包头解析、库元数据和工具目录查询；GUI/Simulink 入口提供结构化无界面替代，不打开 MATLAB 图形系统。 | `tools/comm_misc_family.schema.json` |
| `comm_sequence_decode` | `mlseeq`<br>`tpcenc`<br>`tpcdec`<br>`vitdeccore` | `independent_validated` | 独立 Python 重置模式 MLSE、硬判决 Viterbi 和 BCH 分量码二维 TPC；不覆盖 MATLAB 连续模式、软判决 Chase-Pyndiah、扩展和缩短码。 | `tools/comm_sequence_decode.schema.json` |
| `comm_signal_config` | `arrayConfig`<br>`ofdmPilotConfig`<br>`ofdmPilotGrid`<br>`ofdmPrecode`<br>`iqimbal`<br>`iqimbal2coef`<br>`iqcoef2imbal`<br>`srmdelay`<br>`dpdPreprocessor` | `independent_validated` | 独立 Python 阵列位置、显式导频网格、逐子载波预编码、I/Q 失衡和补偿系数、DPD 特征；srmdelay 只计算速率因子和帧缓冲延迟，滤波器群延迟未知。 | `tools/comm_signal_config.schema.json` |
| `comm_source_coding` | `huffmandict`<br>`huffmanenco`<br>`huffmandeco`<br>`arithenco`<br>`arithdeco`<br>`lloyds`<br>`dpcmopt`<br>`dpcmenco`<br>`dpcmdeco` | `independent_validated` | 独立 Python 显式 Huffman 字典、1 起始整数符号 32 位算术编码、标量 Lloyd-Max 量化和无噪声 DPCM；不覆盖 MATLAB 全部码表格式与矩阵/流状态选项。 | `tools/comm_source_coding.schema.json` |
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

### Wireless Network Toolbox（11）

| 工具 | 注册源函数 | 注册状态 | 覆盖范围 | Schema |
|---|---|---|---|---|
| `node_mobility_constant_velocity` | `nodeMobilityConstantVelocity` | `independent_validated` | stateless trajectory form | `tools/node_mobility_constant_velocity.schema.json` |
| `node_mobility_random_walk` | `nodeMobilityRandomWalk` | `independent_validated` | stateless sampled trajectory form | `tools/node_mobility_random_walk.schema.json` |
| `node_mobility_random_waypoint` | `nodeMobilityRandomWaypoint` | `independent_validated` | stateless sampled trajectory form | `tools/node_mobility_random_waypoint.schema.json` |
| `node_position_grid` | `nodePositionGrid` | `independent_validated` | rectangular-boundary forms | `tools/node_position_grid.schema.json` |
| `node_position_random` | `nodePositionRandom` | `independent_validated` | rectangle and circle forms | `tools/node_position_random.schema.json` |
| `wireless_packet` | `wirelessPacket` | `independent_validated` | — | `tools/wireless_packet.schema.json` |
| `wnet_foundation` | `wnet.FIFOQueue`<br>`wnet.Mobility`<br>`wnet.Node`<br>`wnet.TechnologyType`<br>`wnet.Traffic` | `independent_validated` | 独立 Python FIFO 队列与技术类型常量；抽象 Mobility/Node/Traffic 提供可调用描述与验证，轨迹采用已有 Python 位置工具，不等同 MATLAB 对象继承接口。 | `tools/wnet_foundation.schema.json` |
| `wnet_logging` | `wirelessNetworkEventTracer`<br>`wirelessIQLogger` | `independent_validated` | 独立 Python 事件过滤与 IQ 数组重采样；输入输出为 JSON，不读写 MATLAB MAT 文件或实时订阅 MATLAB 节点。 | `tools/wnet_logging.schema.json` |
| `wnet_simulator` | `wirelessNetworkSimulator` | `independent_validated` | 独立 Python 节点、传输、动作调度与取消、理想或自由空间接收判定；未实现 MATLAB 自定义回调、协议栈及干扰物理层。 | `tools/wnet_simulator.schema.json` |
| `wnet_support` | `wirelessnetworkSupportPackageCheck` | `independent_validated` | Python 运行依赖与 MCP 能力检查；MATLAB 原函数只发一次支持包提示，故迁移后返回 Python 就绪信息。 | `tools/wnet_support.schema.json` |
| `wnet_traffic_models` | `networkTrafficFTP`<br>`networkTrafficOnOff`<br>`networkTrafficVideoConference`<br>`networkTrafficVoIP` | `independent_validated` | 独立 Python 可复现包时间表；含固定值和随机分布的常用属性，未复现 MATLAB 对象状态机和随机数序列逐样本一致性。 | `tools/wnet_traffic_models.schema.json` |

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

## 回归与契约检查

```bash
python scripts/generate_registry_docs.py --check
python scripts/check_contracts.py
python scripts/validate_all.py
```

详细说明见仓库根目录的 `VALIDATION.md`。
