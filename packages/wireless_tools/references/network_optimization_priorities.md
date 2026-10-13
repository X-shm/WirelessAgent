# WirelessAgent 网络优化转换优先级

> 更新日期：2026-09-17。工具数量、验证状态和覆盖范围以 `tool_registry.json` 为准；本文件只定义面向 LTE/5G 网络优化闭环的优先级，不能把 Bluetooth 的名称映射或已验证切片扩大为完整协议仿真结论。

## 项目定位

本工具包服务于 OpenClaw 驱动的 WirelessAgent，而不是单纯复刻 MATLAB API。项目已有两套 3GPP RAG/Graph RAG 语料：

- TS 23.203：PCC、QoS 控制、门控、承载绑定、使用监控；
- TS 29.512：SM Policy Decision、QoS Data、Traffic Control Data、Usage Monitoring、QoS Monitoring 和策略触发器。

因此转换目标应形成以下闭环：

```text
无线测量/仿真 → 同步与信道诊断 → KPI 计算 → MCS/资源/QoS 决策 → 波形或策略验证
```

MATLAB Communications/LTE/Wireless Network Toolbox 主要补足物理层测量、链路仿真和资源验证；TS 23.203/29.512 RAG 负责策略依据与协议字段。二者需要在高层 Workflow/Skill 中组合，不能只靠逐函数转换完成网络优化。调用时以每个 `tools/<name>.schema.json` 的直接 CLI flag 为准，所有工具输出均为 JSON。

## P0：直接进入优化闭环

### 已完成

| 能力 | 工具 |
|---|---|
| 噪声、SNR、BER/SER | `awgn`, `convert_snr`, `biterr`, `symerr`, `ber_awgn` |
| 同步与时延 | `lte_frequency_sync`, `signal_timing_estimate`, `frequency_offset` |
| 信道估计与均衡 | `ofdm_channel_estimate`, `ofdm_equalizer`, `fading_channel` |
| 信号质量 KPI | `evm_metrics` |
| 链路自适应基础 | `lte_mcs`, `lte_tbs`, `lte_modulation`, `lte_ofdm` |
| 资源与参考序列 | `lte_resource_grid`, `lte_prbs`, `lte_pss`, `lte_sss` |
| LTE 标准测量导频 | `lte_cell_rs`, `lte_dl_channel_estimate` |
| LTE 上行导频与信道估计 | `lte_pusch_dmrs`, `lte_ul_channel_estimate` |
| LTE SRS 探测导频 | `lte_srs`（显式连续 PRB 单天线子集） |
| LTE 上行波形与扰码 | `lte_scfdma`, `lte_ul_scrambling` |
| LTE 帧偏移估计 | `lte_frame_offset` |
| LTE 共享信道资源占用 | `lte_pdsch_indices`, `lte_pusch_indices` |
| LTE PMI/CSI 与 2Tx 预编码 | `lte_pmi_info`, `lte_pmi_select`, `lte_csi_codebook` |
| LTE 上行 DFT 预编码 | `lte_ul_precode` |
| LTE 联合 MIMO 均衡 | `lte_mimo_equalizer` |
| LTE 多径覆盖仿真 | `lte_standard_fading`, `ofdm_channel_response` |
| 理论性能基线 | `ber_fading`, `link_capacity` |
| 优化闭环工作流 | `radio_link_diagnosis`, `link_adaptation_optimizer`, `resource_allocation_optimizer`, `closed_loop_validator` |
| RI/CQI 链路反馈 | `lte_rank_select`, `lte_cqi_select` |
| 多接入与 QoS 策略 | `traffic_steering_optimizer`, `qos_policy_builder`, `policy_decision_validator` |
| 小区搜索与资源抽取 | `lte_sync_indices`, `lte_cell_search`, `lte_extract_resources` |
| 场景几何与移动 | 节点位置及三类移动轨迹工具 |

### 下一批优先转换

1. 扩展 `lte_srs`：`lteSRSInfo`、ConfigIdx 调度、标准带宽表、跳频和多天线。
2. 扩展 `lte_pdsch_indices`：Port5/7-14 及非零功率/零功率 CSI-RS 避让。
3. 扩展 `lte_pusch_dmrs`：1/2 PRB 短序列、多层、跳频与预编码。
4. 扩展 `lte_ul_channel_estimate`：多层、多接收天线插值与噪声估计。
5. 扩展 `lte_ul_scrambling`：UCI 占位符和完整 PUSCH 控制信息处理。

## P1：容量、MIMO 与策略效果验证

1. 扩展 `lteCSICodebook` / `ltePMISelect`：4/8 端口、高级 CSI-RS 码本与限制位图。
2. 扩展 `lte_mimo_equalizer`：4Tx 内置码本、CDD 和逐子带 PMI。
3. 扩展 `lte_standard_fading`：MIMO 空间相关、精确 Jakes 多普勒和 TDD 连续状态。
4. 扩展 `ber_coding`：Golay、Reed-Solomon 和更多调制组合。
5. `lteDLSCH` / `lteDLSCHDecode` / `lteULSCH` / `lteULSCHDecode`：端到端吞吐验证。

## P2：高层 Workflow/Skill

这些不应机械映射为单个 MATLAB 函数，而应组合现有工具和 3GPP RAG：

1. `radio_link_diagnosis`：频偏、定时、信道、EVM、BER 联合诊断并定位主要劣化因素。
2. `link_adaptation_optimizer`：根据 SNR/BLER 目标推荐 MCS、TBS、PRB 和调制方式。
3. `qos_policy_builder`：把链路能力映射为 TS 29.512 QoS Data（5QI、MBR、GBR、PDB、PER）。
4. `traffic_steering_optimizer`：根据链路质量、时延和负载生成 UL/DL traffic steering 建议。
5. `closed_loop_validator`：对优化前后场景使用相同随机种子仿真，比较吞吐、BER/EVM、资源占用和 QoS 约束。

## P3：暂缓

- GUI、绘图器、示波器和支持包检查；
- 与当前 LTE/5G QoS 优化目标弱相关的模拟调制、DPCM、Huffman 等教学函数；
- NB-IoT、sidelink、GSM 专用入口，除非项目用例明确扩展；
- Wireless Network Simulator/Event Tracer 等强状态对象应在 P0/P1 数值工具稳定后封装为长期运行服务。`bluetooth_session` 已提供 Bluetooth 专用的 SQLite 持久化会话和事件日志；它不构成 Wireless Network Simulator/Event Tracer 的替代品。

## Bluetooth 与网络优化的接口边界

Bluetooth 已有 26 个 CLI 映射 52 个 MATLAB 顶层名称，并提供 `bluetooth_session` 用于跨 CLI 进程保存节点、配置、确定性流量和事件日志。该能力可为短距链路的波形、PDU、路径损耗、范围和 RF-PHY 测量提供可审计输入，但当前 LTE MCS/PRB 分配与 TS 23.203/29.512 策略工作流不能直接套用于 Bluetooth。

如果后续需要 Bluetooth 优化闭环，应单列协议与 KPI：以 `bluetooth_test_waveform_validate`、`bluetooth_path_loss`、`bluetooth_range` 和会话事件日志产生证据，再为 BLE/Classic 的吞吐、时延、PER、功耗和共存约束定义专用策略。完整 BLE/Classic 状态机、ISO、Mesh 和所有 MATLAB 对象方法仍是 `bluetooth_capabilities.json` 中按项管理的后续工作。

## 验收原则

每个新增工具必须至少满足：确定性样例、物理/数学性质检查、CLI JSON 调用检查、Schema 契约检查和全量回归。高层优化 Skill 还必须输出输入依据、约束、建议、预期收益和可回滚参数，不能只给无证据的调参结论。
