# 转换状态与批次规划

## 本机 R2026a 盘点

按工具箱顶层公开入口文件统计：

| 产品 | 顶层入口数 | 当前已验证工具 |
|---|---:|---:|
| Communications Toolbox | 180 | 30 个工具（覆盖 54 个入口） |
| LTE Toolbox | 273 | 37 个工具（覆盖 61 个入口） |
| Wireless Network Toolbox | 10 | 6 个工具（覆盖 6 个入口） |
| 5G Toolbox | 未整体盘点 | 1 个工具（覆盖 2 个入口） |
| WirelessAgent 组合工作流 | — | 8 个工作流工具 |

入口数不等于最终工具数：互为正反向的函数会合并成一个工具，GUI、内部辅助函数和强状态对象不会机械地逐文件转换。

## 已完成

| OpenClaw 工具 | MATLAB 官方函数 | 验证结果 |
|---|---|---:|
| `lte_crc` | `lteCRCEncode`, `lteCRCDecode` | 20/20 |
| `lte_mcs` | `lteMCS` | 7/7 |
| `lte_modulation` | `lteSymbolModulate`, `lteSymbolDemodulate` | 6/6 |
| `lte_ofdm` | `lteOFDMInfo`, `lteOFDMModulate`, `lteOFDMDemodulate` | 10/10（另含 210 条信息表） |
| `lte_tbs` | `lteTBS` | 28/28 |

以下工具使用标准公式、公开 M 文件逻辑与独立性质测试验证：

| OpenClaw 工具 | MATLAB 函数 | 独立验证 |
|---|---|---:|
| `awgn` | `awgn` | 通过 |
| `biterr` | `biterr` | 通过 |
| `symerr` | `symerr` | 通过 |
| `convert_snr` | `convertSNR` | 通过 |
| `zadoff_chu_seq` | `zadoffChuSeq` | 通过 |
| `lte_prbs` | `ltePRBS` | 通过 |
| `lte_pss` | `ltePSS` | 通过 |
| `node_position_grid` | `nodePositionGrid` | 矩形边界形式通过 |
| `node_position_random` | `nodePositionRandom` | 矩形/圆形形式通过 |
| `node_mobility_constant_velocity` | `nodeMobilityConstantVelocity` | 无状态轨迹形式通过 |
| `qam_modulation` | `qammod`, `qamdemod` | 方形 QAM 往返通过 |
| `psk_modulation` | `pskmod`, `pskdemod` | PSK 往返通过 |
| `pam_modulation` | `pammod`, `pamdemod` | PAM 往返通过 |
| `bit_int_conversion` | `bit2int`, `int2bit` | 双向往返通过 |
| `lte_sss` | `lteSSS` | 已知向量与长度检查通过 |
| `lte_layer_map` | `lteLayerMap`, `lteLayerDemap` | 单/双码字往返通过 |
| `node_mobility_random_walk` | `nodeMobilityRandomWalk` | 无状态轨迹形式通过 |
| `node_mobility_random_waypoint` | `nodeMobilityRandomWaypoint` | 无状态轨迹形式通过 |
| `wireless_packet` | `wirelessPacket` | 字段与默认值检查通过 |
| `dpsk_modulation` | `dpskmod`, `dpskdemod` | binary/Gray 往返通过 |
| `fsk_modulation` | `fskmod`, `fskdemod` | 连续相位波形往返通过 |
| `ofdm_modulation` | `ofdmmod`, `ofdmdemod` | 空载波/导频/可变 CP 往返通过 |
| `binary_symmetric_channel` | `bsc` | p=0/1 边界通过 |
| `white_gaussian_noise` | `wgn` | 功率统计与确定性通过 |
| `frequency_offset` | `frequencyOffset` | 正负频偏往返通过 |
| `rectangular_pulse` | `rectpulse` | 样本重复检查通过 |
| `lte_convolutional_codec` | `lteConvolutionalEncode`, `lteConvolutionalDecode` | 尾咬合闭环解码通过 |
| `lte_resource_grid` | `lteResourceGridSize`, `lteResourceGrid` | 上下行尺寸公式通过 |
| `lte_code_block` | `lteCodeBlockSegment`, `lteCodeBlockDesegment` | 多码块分段、CRC24B 和反向合并通过 |
| `lte_rate_match_convolutional` | `lteRateMatchConvolutional`, `lteRateRecoverConvolutional` | 子块交织、重复与软值合并通过 |
| `convolutional_codec` | `poly2trellis`, `convenc`, `vitdec` | 可配置生成多项式编码/硬 Viterbi 往返通过 |
| `interleaver` | `matintrlv`, `matdeintrlv`, `randintrlv`, `randdeintrlv`, `intrlv`, `deintrlv` | 矩阵、随机和显式置换往返通过 |
| `hamming_code` | `hammgen`, `encode`, `decode` | (7,4) 全位置单比特纠错通过 |
| `reed_solomon_code` | `rsenc`, `rsdec`, `rsgenpoly`, `rsgenpolycoeffs` | 多种完整/缩短码、前后置校验及最大允许错误数随机纠错通过 |
| `bch_code` | `bchenc`, `bchdec`, `bchgenpoly`, `bchnumerr` | 多种本原窄义码及最大允许错误数随机纠错通过 |
| `q_function` | `qfunc`, `qfuncinv` | 已知值和双向往返通过 |
| `ber_awgn` | `berawgn` | BPSK 已知值及 QAM/FSK 性质检查通过 |
| `fading_channel` | `stdchan` | 平坦 Rayleigh/Rician 子集的功率、块衰落与确定性检查通过 |
| `signal_timing_estimate` | `timingEstimate`, `channelDelay` | 已知偏移和完美信道冲激响应峰值通过 |
| `lte_frequency_sync` | `lteFrequencyOffset`, `lteFrequencyCorrect` | 合成 CP-OFDM 频偏估计与反向校正通过 |
| `evm_metrics` | `lteEVM` | 已知 10% EVM、误差向量与 dB 指标通过 |
| `ofdm_equalizer` | `ofdmEqualize`, `lteEqualizeZF`, `lteEqualizeMMSE` | 随机 2×2 MIMO ZF/MMSE 无噪声恢复通过 |
| `ofdm_channel_estimate` | `ofdmChannelEstimate` | 常量复信道导频估计与二维插值通过 |
| `lte_cell_rs` | `lteCellRS`, `lteCellRSIndices` | 端口密度、单位模及官方端口 2 示例索引通过 |
| `lte_sync_indices` | `ltePSSIndices`, `lteSSSIndices` | FDD 子帧 0/5、Normal/Extended CP 位置检查通过 |
| `lte_cell_search` | `lteCellSearch` | NCellID 0、321、503 的 PSS/SSS 检测通过 |
| `lte_extract_resources` | `lteExtractResources` | 2D/3D 下标和 MATLAB 列优先线性索引通过 |
| `lte_dl_channel_estimate` | `lteDLChannelEstimate` | 双 CRS 端口常量复信道恢复通过 |
| `lte_pusch_dmrs` | `ltePUSCHDRS`, `ltePUSCHDRSIndices` | 单层、显式 PRB 分配、每 PRB 单位模序列与索引检查通过 |
| `lte_ul_channel_estimate` | `lteULChannelEstimate` | PUSCH DM-RS 常量复信道恢复通过 |
| `lte_ul_scrambling` | `lteULScramble`, `lteULDescramble` | 传输数据硬扰码与软值解扰往返通过 |
| `lte_scfdma` | `lteSCFDMAInfo`, `lteSCFDMAModulate`, `lteSCFDMADemodulate` | DFT 扩频及半子载波偏移波形往返通过 |
| `lte_frame_offset` | `lteDLFrameOffset`, `lteULFrameOffset` | 显式标准参考波形的已知偏移检测通过 |
| `lte_pusch_indices` | `ltePUSCHIndices` | DM-RS 排除、shortened 子帧、G/Gd 和时隙 PRB 分配检查通过 |
| `lte_pdsch_indices` | `ltePDSCHIndices` | 官方 1.4 MHz 示例索引及控制区、CRS、同步信号、PBCH 排除检查通过 |
| `lte_srs` | `lteSRS`, `lteSRSIndices` | 显式连续 PRB、transmission comb、单位模和循环移位检查通过 |
| `lte_pmi_info` | `ltePMIInfo` | 官方 R.13 示例、宽带/子带和码本限制元数据检查通过 |
| `lte_csi_codebook` | `lteCSICodebook`, `lteDLPrecode`, `lteDLDeprecode` | 1/2 端口 rank-1/rank-2 标准码本及预编码往返通过 |
| `lte_pmi_select` | `ltePMISelect` | 2Tx 合成方向信道的最优 PMI 与 LMMSE SINR 选择通过 |
| `lte_ul_precode` | `lteULPrecode`, `lteULDeprecode` | 多层分块 DFT/IDFT 往返与能量保持通过 |
| `lte_mimo_equalizer` | `lteEqualizeMIMO`, `lteEqualizeULMIMO` | 2×2 理想信道下预编码感知 MMSE 联合恢复与 CSI 检查通过 |
| `lte_pdsch_prbs` | `ltePDSCHPRBS` | 与相同 cinit 的 LTE Gold 序列逐比特一致，区段和 signed 映射通过 |
| `lte_standard_fading` | `lteFadingChannel` | EPA/EVA/ETU 标准表、确定性种子和抽头形状检查通过 |
| `ofdm_channel_response` | `ofdmChannelResponse` | 单抽头常量复信道全子载波响应检查通过 |
| `ber_fading` | `berfading` | 单分支 Rayleigh BPSK 闭式结果及 MRC 单调性通过 |
| `ber_coding` | `bercoding` | Hamming/卷积码随 Eb/No 单调下降及公开距离谱公式检查通过 |
| `lte_rank_select` | `lteRISelect` | 正交 2×2 信道选 rank 2、完全相关信道选 rank 1 通过 |
| `lte_cqi_select` | `lteCQISelect` | CQI 0/15 门限边界、宽带和子带差分饱和通过 |

以下为服务网络优化闭环的组合工作流，不计入 MATLAB 官方入口覆盖率：

| 工作流工具 | 作用 | 独立验证 |
|---|---|---:|
| `link_capacity` | SISO/MIMO Shannon 上界 | 0 dB SISO 已知容量与 MIMO 增益通过 |
| `radio_link_diagnosis` | 多 KPI 根因和动作建议 | 正常/低 SNR/大频偏边界通过 |
| `link_adaptation_optimizer` | SNR → MCS/TBS | SNR 提升时 MCS/TBS 单调增加通过 |
| `resource_allocation_optimizer` | 多用户 PRB/MCS 分配 | PRB 守恒和逐用户输出通过 |
| `closed_loop_validator` | 优化前后验收/回滚 | KPI 改善、硬约束失败和回滚分支通过 |
| `traffic_steering_optimizer` | 多接入业务分流 | 容量/时延可行性、优先级和低时延选择通过 |
| `qos_policy_builder` | 业务需求到 QoS 建议 | Voice 5QI 模板、GBR 和容量可承诺性通过 |
| `policy_decision_validator` | QoS/分流策略验收 | GBR 容量、时延/PER 和回滚分支通过 |

## 建议后续批次

1. 网络优化 P0 扩展：SRS ConfigIdx/跳频/多天线，以及 PDSCH Release 10+ CSI-RS 资源避让。
2. 网络优化 P1：扩展 4/8 端口 CSI 码本、标准多径配置和 DL-SCH/UL-SCH 吞吐验证。
3. 完整排序和 Workflow 规划见 `network_optimization_priorities.md`。
4. Wireless Network 剩余入口均为模拟器、日志器、事件追踪或支持包检查，应采用状态服务/诊断工具封装。

## 验证标记

- `validated`：具有已有 MATLAB JSON 黄金样本并通过逐值回归。
- `independent_validated`：不依赖 MATLAB 许可证，使用标准公式、公开源码逻辑、已知向量或数学性质测试通过。
