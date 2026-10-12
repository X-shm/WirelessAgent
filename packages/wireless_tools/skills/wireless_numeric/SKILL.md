---
name: wireless_numeric
description: |
  无线通信数值核验技能：把习题/问答中的调制、误码率、信道容量、SNR 换算、信道编码、TBS、
  OFDM 等数值计算，转发到 MATLAB golden sample 校验过的 wireless-toolbox 原脚本。
  当用户提到 BER/误码率、EbN0/SNR 换算、Q 函数、香农容量、QAM/PSK 星座、CRC/LDPC/Polar/
  Hamming/卷积码、TBS/MCS、OFDM 参数、AWGN/衰落 等需要精确数值时触发。
  不替代原脚本：本 skill 只做意图路由与 CLI 转发。
user-invocable: true
---

# Wireless Numeric — 数值核验包

把「要算准的数字」交给 `wireless-toolbox/tools/*.py`（MATLAB 校验、CLI JSON 输出）。
**不要用 LLM 心算替代工具结果**；工具输出即权威数值。

## 运行方式

```bash
# 列出本包工具与调用提示
python skills/wireless_numeric/dispatcher.py list

# 转发调用（原脚本参数原样透传）
python skills/wireless_numeric/dispatcher.py run <tool> --flag value ...

# 查看某工具完整参数
python skills/wireless_numeric/dispatcher.py help <tool>
```

路径约定：以上命令在 **wireless-toolbox 仓库根目录** 执行；也可在任意目录用绝对路径调 `dispatcher.py`（内部自动定位 `tools/`）。

## 路由表（意图 → 工具）

| 问题类型 | 工具 | 示例 |
|---|---|---|
| Q(x) / 互补误差 | `q_function` | `run q_function --mode qfunc --values 0,1,2` |
| AWGN 理论 BER | `ber_awgn` | `run ber_awgn --ebno_db 0,5,10 --modulation qpsk` |
| 衰落信道 BER | `ber_fading` | `run ber_fading --ebno_db 0,10 --fading Rayleigh` |
| Eb/No ↔ Es/No ↔ SNR | `convert_snr` | `run convert_snr --x 10 --input_mode ebno --output_mode esno --bits_per_symbol 2` |
| 香农/MIMO 容量 | `link_capacity` | `run link_capacity --snr_db 10 --bandwidth_hz 1e6` |
| QAM/PSK/PAM 星座 | `qam_modulation` / `psk_modulation` / `pam_modulation` | `run qam_modulation --mode modulate --order 16 --values 0,1,1,0` |
| 5G 调制 / LLR | `nr_modulation` | `run nr_modulation --mod QPSK --bits 1,1,0,1` |
| 误比特/符号统计 | `biterr` / `symerr` | `run biterr --x 1,0,1,1 --y 1,1,1,0` |
| 加噪 / 衰落仿真 | `awgn` / `fading_channel` | `run awgn --signal '[1,1,1,1]' --snr 10` |
| CRC | `nr_crc` | `run nr_crc --poly 16 --bits 1,0,1,1` |
| LDPC / Polar | `nr_ldpc` / `nr_polar` | `run nr_ldpc --mode encode --bgn 1 --zc 16 --bits 1,0,1,1` |
| Hamming / 卷积码 | `hamming_code` / `convolutional_codec` | `run hamming_code --mode encode --m 3 --bits 1,0,1,1` |
| 5G TBS | `nr_tbs` | `run nr_tbs --modulation QPSK --nlayers 1 --nprb 50 --nre-per-prb 12 --tcr 0.5` |
| LTE TBS / MCS | `lte_tbs` / `lte_mcs` | `run lte_mcs --imcs 17 --table PDSCH` |
| OFDM / CP | `ofdm_modulation` / `lte_ofdm` / `nr_ofdm` | `run lte_ofdm --mode info --nrb 50 --cp Normal` |

## 解题流程

1. **识别**考点 → 对照路由表选 1 个工具（一般一步一工具；链路题按 编码→调制→信道→统计 串联）。
2. **调用** `dispatcher.py run ...`，拿到 JSON。
3. **作答**时：公式推导写步骤；**数值部分引用工具结果**（写明工具名），不要手算覆盖。
4. 单位与有效数字：dB/dm 一位小数，比特/整数精确；Eb/No 与 SNR 必须经 `convert_snr` 统一后再比。

## 边界

- 本包只覆盖「数值核验」；标准条文解释、论文检索不在这里。
- 超出 PACK 的工具（LTE 全栈、蓝牙、网络优化）不要猜参数乱调——先向用户确认或走后续技能包。
- 禁止在本 skill 内新写算法；缺功能就报「工具缺失」，回到 wireless-toolbox 补脚本 + golden sample。

## 输出格式

- 禁用 LaTeX；公式用 Unicode：Q(x)、√、×、·、≤、η、γ、Es/N0。
- 数值结果优先贴 JSON 关键字段，再用一句中文解读。
