# OpenClaw 无线网络优化闭环

> 更新日期：2026-09-17。此流程面向 LTE/5G 优化的确定性分析与策略验收。已登记工具、输入 flag 和覆盖边界以 `tool_registry.json` 及各 `tools/<name>.schema.json` 为准；这些命令不会直接修改基站、核心网或无线设备。

本工作流把已转换的标准数值工具组合为可审计、可回滚的优化流程。所有阶段输出 JSON，后续阶段应保留前一阶段的输入依据和随机种子。

下列数值工具使用 schema 中定义的直接 flag（例如 `--snr_db`）；`{baseDir}` 应替换为本仓库根目录。对于任何随机信道或噪声场景，必须显式固定并记录随机种子。

```text
原始波形/测量
  → 同步：lte_frequency_sync + lte_frame_offset
  → 信道/KPI：lte_*_channel_estimate + evm_metrics + biterr
  → 诊断：radio_link_diagnosis
  → 无线反馈：lte_rank_select + lte_cqi_select
  → 决策：link_adaptation_optimizer + resource_allocation_optimizer
  → 策略：traffic_steering_optimizer + qos_policy_builder
  → 仿真：lte_standard_fading + lte_mimo_equalizer
  → 验收：policy_decision_validator + closed_loop_validator
```

## 1. 诊断

```powershell
python "{baseDir}/tools/radio_link_diagnosis.py" --snr_db 8 --evm_percent 12 --ber 0.003 --frequency_offset_hz 1800
```

优先处理同步类问题，再调整 MCS/PRB。频偏或定时未收敛时，不应把全部误码归因于覆盖不足。

## 2. 链路自适应

```powershell
python "{baseDir}/tools/link_adaptation_optimizer.py" --snr_db 15 --nprb 25 --margin_db 2 --bler_target 0.1
```

SNR 门限属于保守启发式，ITBS、调制和 TBS 来自已验证的 LTE 官方表。现场部署应使用 BLER 外环继续修正 `margin_db`。

## 3. 多用户资源分配

```powershell
python "{baseDir}/tools/resource_allocation_optimizer.py" --users '[{"id":"u1","snr_db":15,"demand_kbps":5000,"priority":2},{"id":"u2","snr_db":5,"demand_kbps":2000,"priority":1}]' --total_prbs 25
```

输出包含每用户 PRB、MCS、TBS、预计 kbps 和需求满足状态。策略修改前应记录旧分配，便于回滚。

## 4. 场景验证

使用 `lte_standard_fading` 生成 EPA/EVA/ETU 场景，并用相同随机种子比较优化前后。MIMO 场景可继续调用 `lte_mimo_equalizer`，理论上界使用 `link_capacity`。

在多接入场景中，先用 `traffic_steering_optimizer` 形成容量/时延可行的分流建议，再用 `qos_policy_builder` 生成 QoS Data 草案。5QI 模板是工程建议，正式策略仍应结合项目的 TS 23.203/29.512 RAG 依据审查。

## 5. 验收和回滚

```powershell
python "{baseDir}/tools/closed_loop_validator.py" --before '{"throughput":10,"ber":0.01,"latency_ms":30}' --after '{"throughput":12,"ber":0.001,"latency_ms":25}' --constraints '{"ber":{"max":0.002},"latency_ms":{"max":30}}'
```

只有 `accepted=true` 且 `rollback_recommended=false` 才进入下一轮。工具不会直接修改基站或核心网参数；实际变更应由外部执行层完成并保留审批记录。

## 6. Bluetooth 不复用 LTE 决策器

Bluetooth 的波形、PDU、范围与会话能力可作为独立短距链路工作流的测量层，但不得把本流程的 LTE MCS、PRB 或 5QI 映射直接用于 BLE/Classic。当前可使用 `bluetooth_test_waveform_validate`、`bluetooth_path_loss`、`bluetooth_range` 和 `bluetooth_session` 形成可追溯输入；完整协议状态机、ISO、Mesh 和设备级闭环尚未交付。Bluetooth 的逐项能力与限制见 `bluetooth_capabilities.json`。
