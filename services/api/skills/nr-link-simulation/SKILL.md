---
name: nr-link-simulation
description: |
  5G 链路级 BER 仿真实验：调制 → AWGN 加噪 → 解调 → 算误码率。
  当用户要做「链路仿真 / BER 仿真 / 误码率仿真」但未给参数时触发，用默认小规模参数跑演示。
user-invocable: true
---

# 5G 链路仿真实验（调制 → 加噪 → 解调 → BER）

用户要做链路仿真但没给参数时，用下面默认参数跑一个演示，并告知用户可改参数重跑。

## 默认参数
- 调制：QPSK；信道：AWGN；SNR：10 dB；比特数：64

## 流程（依次调用工具，共 4 步）
1. **调制**：调 `nr_modulation`，args `{"mod":"QPSK","bits":"<64 个 0/1，逗号分隔>"}`。记下输出的 `symbols_real` 与 `symbols_imag`（原始比特也记下，供第 4 步用）。
2. **加噪**：调 `awgn`，args 的 `signal` 用复数 JSON 对象 `{"real":<symbols_real 数组>,"imag":<symbols_imag 数组>}`，`snr`=10，`signal_power`="measured"。记下输出的 `signal_real` 与 `signal_imag`。
3. **解调**：调 `nr_modulation`，args `{"mod":"QPSK","inverse":true,"symbols":"<复数数组>"}`。复数数组由第 2 步的 `signal_real`/`signal_imag` 按位合成，格式 `[re0+im0j, re1+im1j, ...]`（例：signal_real=[0.5,0.6]、signal_imag=[0.1,0.2] → symbols="[0.5+0.1j,0.6+0.2j]"）。记下输出的 `bits`。
4. **算误码率**：调 `biterr`，args `{"x":"<原始比特>","y":"<解调比特>"}`。记下 `num_errors` 与 `error_ratio`。

## 输出
- 报告：调制方式、SNR、比特数、误码数、误码率。
- 最后加一句："以上为默认参数（QPSK / AWGN / SNR=10dB / 64 比特）的演示结果，可指定调制、SNR、比特数重跑。"

## 注意
- 比特数默认 64，是为了让中间复数数组足够短、便于精确传递；若用户要求更大规模，提醒"大数据量会降低串联精度"。
- 不要用 LLM 心算替代工具结果；每一步的数值必须来自工具返回。
