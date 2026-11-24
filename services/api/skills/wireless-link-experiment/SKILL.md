---
name: wireless-link-experiment
description: |
  无线链路评估与优化实验流程：算容量 → 诊断链路 → 推荐 MCS/TBS → 闭环校验。
  当用户要做无线链路仿真、评估或优化实验时触发。
user-invocable: true
---

# 无线链路评估与优化实验

按下面闭环执行，用工具结果说话，**不要用 LLM 心算替代工具数值**。

## 1. 明确场景
先确认关键输入：SNR、带宽、调制、PRB 数、层数、目标 BLER，以及已知的 BER / EVM / 频偏 / 时偏。
缺参数就向用户确认，不要猜。

## 2. 算链路容量（基准）
调 `link_capacity`（`snr_db` + `bandwidth_hz`，可选 `channel`），得到香农容量作为上限基准。

## 3. 诊断链路
把 SNR / EVM / BER / 频偏 / 时偏喂给 `radio_link_diagnosis`，得到故障原因与建议动作。

## 4. 优化 MCS / TBS
用 `link_adaptation_optimizer`（`snr_db`、`nprb`、`table`、`layers`、`margin_db`）推荐保守的 MCS/TBS。

## 5. 闭环校验
用 `closed_loop_validator` 对比优化前后的 KPI，确认改进是否达标。

## 输出要求
- 每一步给出「工具名 + 关键输入 + 结果」。
- 数值引用工具返回，不手算覆盖。
- 中文作答，公式用 Unicode，dB 保留一位小数。
