# SkillOpt 候选业务问题草案

状态：**待业务审核**。这些问法由仓库内工作流和工具契约整理，不是用户日志、真实客户提问或已获批准的验收题。不得直接写入 `approved.jsonl`，也不得用于宣称真实用户效果。来源为 `references/network_optimization_workflow.md`、`references/network_optimization_priorities.md` 和相应的 `tools/*.schema.json`。

逐题技术与产品适配性预审见 [26 题预审报告](SkillOpt_26题预审报告.md)。其中 11 题建议修改、4 题暂缓；预审不代表业务批准。

| 编号 | 待审问题 | 候选工具 | 来源与审核重点 |
|---|---|---|---|
| D01 | 某 LTE 链路测得 SNR 8 dB、EVM 12%、BER 0.003、频偏 1800 Hz。请判断主要劣化因素，并说明排查的优先顺序。 | `radio_link_diagnosis` | 网络优化工作流；核对诊断结论是否符合产品的解释口径。 |
| D02 | 链路 SNR 为 15 dB，可用 25 个 PRB，预留 2 dB 裕量，目标 BLER 为 0.1。请给出链路自适应建议。 | `link_adaptation_optimizer` | 网络优化工作流；确认推荐的参数和适用范围。 |
| D03 | 两个用户分别有 SNR 15 dB、需求 5000 kbps、优先级 2，和 SNR 5 dB、需求 2000 kbps、优先级 1；共有 25 个 PRB。怎样分配资源，各自需求能否满足？ | `resource_allocation_optimizer` | 网络优化工作流；确认公平性、优先级和需求满足的判断口径。 |
| D04 | 调整前吞吐 10、BER 0.01、时延 30 ms；调整后吞吐 12、BER 0.001、时延 25 ms。约束为 BER 不超过 0.002、时延不超过 30 ms。此次调整是否应验收，是否建议回滚？ | `closed_loop_validator` | 网络优化工作流；补充吞吐单位及业务验收标准。 |
| D05 | 5G NR 下行使用 QPSK、单层、40 个 PRB、每 PRB 132 个 RE、目标码率 0.48。该资源分配的传输块大小是多少比特？ | `nr_tbs` | `nr_tbs` 工具契约；确认资源参数与实际业务场景一致。 |
| D06 | 5G NR 的 QAM256 MCS 表中，索引 17 对应什么调制阶数、目标码率和频谱效率？ | `nr_mcs_tables` | `nr_mcs_tables` 工具契约；核对所用 MCS 表是否符合项目配置。 |
| D07 | 在 Industrial 环境，蓝牙设备相距 2 米和 15 米，暂不考虑随机阴影衰落。两处的路径损耗各是多少？ | `bluetooth_path_loss` | `bluetooth_path_loss` 工具契约；核对模型、环境参数和输出单位。 |
| D08 | 我想估算蓝牙链路的覆盖距离。 | 暂不调用工具，先询问条件 | 信息不足类问题；明确需要的环境、功率、接收灵敏度等参数，避免凭空假定。 |
| D09 | 把这个 BLE Link Layer 数据包 `D6BE898E4009AB8967452301020106A8F1DF`（时间戳 0 微秒）保存为 PCAPNG 文件，并告诉我生成的文件位置。 | `ble_pcap_writer` | `ble_pcap_writer` 工具契约；验证文件路径受数据目录限制，用户是否有取回文件的流程。 |
| D10 | 5G NR 的 QAM64 MCS 表中，索引 9 的调制方式和目标码率是什么？ | `nr_mcs_tables` | 5G Toolbox；确认所用 MCS 表。 |
| D11 | LTE PDSCH 的 MCS 索引 5 对应什么调制方式和 TBS 索引？ | `lte_mcs` | LTE Toolbox；确认项目采用的表。 |
| D12 | LTE PDSCH 的 MCS 索引 12 对应什么调制方式和 TBS 索引？ | `lte_mcs` | LTE Toolbox；与 D11 同类不同输入。 |
| D13 | LTE PDSCHTable2 的 MCS 索引 23 对应什么调制方式和 TBS 索引？ | `lte_mcs` | LTE Toolbox；确认 256QAM 表在产品范围内。 |
| D14 | Eb/No 为 5 dB，QPSK 每符号 2 比特、编码率 0.5。换算成 SNR 是多少 dB？ | `convert_snr` | Communications Toolbox；确认采样率等默认条件。 |
| D15 | Eb/No 为 8 dB，16QAM 每符号 4 比特、编码率 0.75。对应 SNR 是多少 dB？ | `convert_snr` | Communications Toolbox；确认换算口径。 |
| D16 | 64QAM 每符号 6 比特且不编码，Es/No 为 12 dB。请换算成 Eb/No。 | `convert_snr` | Communications Toolbox；与 D14–D15 方向不同。 |
| D17 | 用初始状态 37 对 WLAN 数据比特 `1,0,1,0,1,1,0,0` 加扰，输出比特序列是什么？ | `wlan_scramble` | WLAN Toolbox；确认这类位级任务是否面向网站用户。 |
| D18 | 20 MHz Non-HT WLAN 数据字段的 FFT 长度、采样率和循环前缀长度是多少？ | `wlan_ofdm_info` | WLAN Toolbox；确认 Non-HT 是目标场景。 |
| D19 | WLAN 扰码器初始状态 93，对接收比特 `1,1,0,0,0,1,0,0` 解扰，恢复序列是什么？ | `wlan_scramble` | WLAN Toolbox；确认解扰使用场景。 |
| D20 | 无线节点初始位置 `(0,0,0)` 米，速度 `(3,4,0)` 米每秒。0、1、5 秒时分别在哪里？ | `node_mobility_constant_velocity` | Wireless Network Toolbox；确认轨迹规划是否属于产品范围。 |
| D21 | 在长 120 米、宽 60 米的区域内按 2 行 3 列网格中心放置节点，给出各节点三维位置。 | `node_position_grid` | Wireless Network Toolbox；确认坐标约定。 |
| D22 | 无线节点初始位置 `(10,5,0)` 米，以 `(-1,2,0)` 米每秒移动。0、4、8 秒时分别在哪里？ | `node_mobility_constant_velocity` | Wireless Network Toolbox；覆盖负向速度参数。 |
| D23 | 参考比特为 `0,1,1,0,1,0`，接收比特为 `0,1,0,0,1,1`。误比特数和 BER 是多少？ | `wireless_utils` | WirelessAgent Helper；确认与独立 `biterr` 工具的选择规则。 |
| D24 | BPSK 在 AWGN 信道下 Eb/N0 为 6 dB，理论 BER 是多少？ | `wireless_utils` | WirelessAgent Helper；确认与独立 `ber_awgn` 工具的选择规则。 |
| D25 | 参考比特为 `1,0,1,1,0,0,1,1`，接收比特为 `1,1,1,0,0,0,1,1`。误比特数和 BER 是多少？ | `wireless_utils` | WirelessAgent Helper；确认是否暴露聚合工具。 |
| D26 | 请帮我计算这次 5G NR 下行的传输块大小。 | 暂不调用工具，先询问条件 | 信息不足题；确认要追问 PRB、调制方式和码率等。 |

本地 MCP 已对 24 道工具题生成参考结果；D08、D26 是无需调用工具的信息不足题。参数、参考结果、答案必需字段和**暂定** train/selection/holdout 分组见 [待审 JSONL 草稿](SkillOpt_候选业务题标注.jsonl.example)。所有行仍为 `review_status: draft`，技术可执行不等于业务认可。D01–D04 是工作流步骤中的单工具问题；完整的多工具闭环问题尚不在当前单工具评分格式内。

## 请按业务用途审核

对每个编号回复“保留 / 修改（写一句修改意见）/ 删除”。重点确认：

- D01–D04：诊断和优化建议是否属于网站 agent 的实际职责；D04 的吞吐单位及验收标准是否需要补充。
- D05–D06：5G 参数组合与 MCS 表是否符合实际项目配置。
- D07–D08：是否需要蓝牙路径损耗、覆盖距离；信息不足时应该先问哪些参数。
- D09：产品是否能让用户取得生成的 PCAPNG 文件；如果不能，应删除或改成只返回可展示的结果。
- D10–D26：这些题用于补齐整个工具箱的产品领域。请特别判断 WLAN、节点仿真和 WirelessAgent Helper 是否会由网站用户直接提出；聚合工具 `wireless_utils` 与独立计算工具同时存在，需确定用户问法应路由到哪一个。

按“整个工具箱”范围，当前 26 题在 train、selection、holdout **每组都覆盖注册表的八个产品领域**，holdout 也含工具调用和信息不足两类请求。这只是最小领域覆盖，不能代表 144 个工具的真实用户分布或所有参数组合。审核后还要补充高频、易混工具及失败场景；若以后取得经许可、已脱敏的真实用户提问，应单独标为 `user_query`，不要与这里的 `expert_authored` 设计题混淆。
