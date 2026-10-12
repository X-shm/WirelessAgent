# 转换状态与 R2026a 环境基线

> 更新日期：2026-09-17。工具定义、数量、状态和覆盖范围以 `tool_registry.json` 为唯一事实来源；Bluetooth 的逐项能力状态和剩余缺口以 `bluetooth_capabilities.json` 为准。本文件记录当前 MATLAB oracle 主机、源函数盘点和样本基线，不能替代上述两个事实来源。

## 当前 Oracle 环境

| 项目 | 当前值 |
|---|---|
| MATLAB | R2026a Update 3，26.1.0.3276743 |
| 5G Toolbox | 已安装，可重生 NR 样本 |
| Bluetooth Toolbox | 已安装；52 个登记的顶层名称可在本机解析 |
| Communications Toolbox | 已安装 |
| LTE Toolbox | 已安装，CRC/MCS/调制/OFDM/TBS 样本已重生 |
| WLAN Toolbox | 已安装，BCC/加扰/LDPC 样本已重生 |
| Wireless Network Toolbox | 已安装，已重新盘点函数入口 |

`references/function_inventory.json` 已由以下命令重建：

```powershell
python scripts/build_function_inventory.py --matlab_root D:\Matlab --matlab-release "R2026a Update 3 (26.1.0.3276743)"
```

当前可用的顶层入口/已映射入口为：5G `160/28`、Bluetooth `52/52`、Communications `180/54`、LTE `273/61`、WLAN `131/3`、Wireless Network `10/6`。Bluetooth 的公开名称分布在 Classic 与 BLE 两个 MATLAB 文件夹，库存生成器已合并两者。这里的“已映射入口”按 MATLAB 名称计数，不能与下节按 Python CLI 计数混用。

## 当前转换成果

| 产品/领域 | 注册 CLI 数 | 验证状态 |
|---|---:|---|
| 5G Toolbox | 17 | 17 个 `validated` |
| Bluetooth Toolbox | 26 | 26 个 `validated`；映射 52 个不同顶层 MATLAB 名称 |
| LTE Toolbox | 37 | 5 个 `validated`，32 个 `independent_validated` |
| Communications Toolbox | 30 | 30 个 `independent_validated` |
| WLAN Toolbox | 3 | 3 个 `validated` |
| Wireless Network Toolbox | 6 | 6 个 `independent_validated` |
| WirelessAgent Workflow | 8 | 8 个 `independent_validated` |
| WirelessAgent Helper | 2 | 2 个 `validated`，其中 `bluetooth_session` 是持久对象会话 |
| **合计** | **129** | **53 个 `validated`，76 个 `independent_validated`** |

状态描述的是验证证据与 `coverage` 所述功能切片，不是完整标准覆盖承诺。特别是 Bluetooth 的 52 个名称已有 CLI 映射，不表示全部 MATLAB 参数、对象方法、节点仿真、BLE/Classic 协议状态机、ISO 或 Mesh 行为已等价实现；逐项结论必须查看 `bluetooth_capabilities.json`。

## R2026a 样本基线

`matlab_oracle/run_all_samples.m` 已在当前完整 R2026a oracle 主机执行其所有 32 个生成任务，覆盖 5G、LTE、WLAN 和 Bluetooth 的现有 MATLAB 生成器。`matlab_oracle/sample_manifest.json` 当前记录 59 份 JSON：58 份标注为本次 R2026a 基线重生，`polar_sequence.json` 是固定的 3GPP 可靠性序列。

其中 Bluetooth 相关样本覆盖 Classic/EDR 与 LE 波形、理想接收、测试波形和验证、跳频、节点、PDU、配置、CTE/CS、PCAP 和路径损耗/距离的代表性切片。它们是已检入回归向量，不是所有参数组合的穷尽证明。Wireless Network 的六个工具仍采用无状态兼容子集和独立性质验证，尚无对应 MATLAB 样本生成器。

## 样本生成与核查

- 所有生成器通过 `wt_sample_dir` / `wt_sample_path` 定位 `matlab_oracle/samples`，不依赖 MATLAB 当前目录或开发机盘符；
- 在具备上述全部产品的当前环境执行 `addpath('matlab_oracle'); run_all_samples` 可重生当前 MATLAB-backed 样本；只有 5G Toolbox 时可使用 `run_5g_samples`；
- Bluetooth 映射完整性可单独核查：`addpath('matlab_oracle'); verify_bluetooth_inventory`；
- 每次样本重生后应审查 diff，使用 `python scripts/generate_sample_manifest.py --write ...` 更新哈希和 provenance，再执行全量 Python 回归；
- 开源 CI 只验证已检入样本的完整性，不假设有 MATLAB 许可证；缺少某项 Toolbox 时，不应重写或删除其他来源的样本。

## 后续转换优先级

1. 为 Bluetooth 的 `partial` 能力建立默认、边界、非法输入和组合约束的 MATLAB 对照；优先补全 Classic/LE 节点协议状态机、对象方法、ISO/Mesh 及受损/多天线接收回归，而不是把名称映射误报为行为等价。
2. 将 `nr_pdsch` 从单码块、单层、矩形 OFDM 的验证级级联推进到含 DM-RS、信道估计、均衡、资源映射和 HARQ 的明确子集。
3. 扩大 DM-RS、CSI-RS、DCI、PDCCH 的参数矩阵，并只在新样本和回归通过后扩大 `coverage`。
4. 为 Wireless Network Toolbox 的六个无状态兼容子集补充确定性 MATLAB 对照向量；若不能对应有状态 API，则保留独立验证标记和明确边界。
5. 以语义级 schema/CLI 测试、锁定依赖和可安装包替代当前部分脚本文本检查。
