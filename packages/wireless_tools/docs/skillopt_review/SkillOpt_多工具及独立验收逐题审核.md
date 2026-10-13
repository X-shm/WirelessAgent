# SkillOpt 多工具题与独立验收候选题逐题审核

日期：2026-10-10。审核对象：[W01–W04 多工具题](SkillOpt_多工具候选题.jsonl.example)及新建的 [H01–H18 独立验收候选题](SkillOpt_独立验收候选题.jsonl.example)。两份文件全部保留 `origin_type: expert_authored`、`review_status: draft`。下文“技术通过”表示参数、工具路线、参考输出及答案路径与**当前本地 MCP 实现**一致，不表示外部标准的独立复核、真实用户来源或产品业务批准。

逐题使用工具注册表、输入 schema、工具实现和本地 MCP 复算检查；H01–H18 还与已有 D01–D26 及 W01–W04 的题面做了精确去重，并在临时技术测试文件中通过冻结和模拟执行。`wirelessagent.plus` 当前无法通过检索工具取得功能页面，故网站实际可用场景、文件交付和用户提问分布仍需业务方确认。

## 原有四道多工具题

| 题目 | 审核结论 | 处理与边界 |
|---|---|---|
| W01 | 修订后技术通过 | LTE `lte_mcs` 的 `itbs=16` 被转成字符串传给 `lte_tbs`，18 PRB、单层得到 `tbs=5992` 比特。MCS 改为 18，避开旧 D12 的索引 12。业务方仍须确认 PDSCH 表适用。 |
| W02 | 修订后技术通过 | `QAM256Table` 索引 21 返回 256QAM，调制和码率实际传给 `nr_tbs`，得到 `tbs=23568` 比特。索引由与 D06 重复的 17 改为 21。表名、索引和资源配置仍需业务确认。 |
| W03 | 修订后技术通过；不纳入新独立验收文件 | 11 dB Es/N0 经 `convert_snr` 得 Eb/N0 `4.979400086720376` dB，实际传给 `ber_awgn`。题面为未编码 16QAM；这是本地理论模型的输出，不能外推现场 BER。保留为工作流示例，不与 H01–H18 混作新 holdout。 |
| W04 | 有条件保留为流程示例 | `radio_link_diagnosis` → `link_adaptation_optimizer` → `closed_loop_validator` 顺序可执行。已把前后吞吐修正为 3.0/4.0 Mbps，低于本题工具估算的 4.776 Mbps 峰值，并说明调整由外部人员完成。后两步所需数值直接来自题面，**不构成跨工具数值传递**；验证器只核对已给数据，不执行或批准网络变更。 |

## 新增独立验收候选题

这 18 题全部暂分到 `holdout`，与训练、选优题分开保存。13 道单工具题、3 道多工具题、2 道信息不足题，覆盖注册表的八个产品领域。18 题共完成 19 次本地 MCP 参考调用。

| 题目 | 领域与结论 | 逐题核查要点 |
|---|---|---|
| H01 | LTE，技术通过 | 显式给出 Port0、Subband 与三个 SINR；返回宽带 CQI 9、子带 CQI `[5,8,11]`。按工具内置门限评分。 |
| H02 | LTE，技术通过 | CRC8、输入比特和零掩码均明确；校验位及完整编码比特来自 `lte_crc`。 |
| H03 | 5G，技术通过 | `nr_prbs` 产生 12 位序列，经 `csv` 绑定原样传入 `nr_crc` 的 `bits`；答案分别取原序列和追加 CRC6 后序列。 |
| H04 | 5G，技术通过 | NR QPSK 输入长度为偶数，输出实、虚部各四项；与 WLAN 星座映射题使用不同工具。 |
| H05 | Bluetooth，技术通过；业务措辞待确认 | LE1M、无 CTE、载荷 12 字节和 `Disabled` 类型均明确；返回 176 微秒、176 比特。`Disabled` 是工具的包类型名称，需确认网站用户是否理解此问法。 |
| H06 | Bluetooth，技术通过 | CSA #2 先运行两事件，再把返回的状态以 JSON 绑定给第二次调用；第二次返回信道 `[21,21]`、末次事件计数 3。题面明确使用默认接入地址；真实业务是否让用户管理状态须确认。 |
| H07 | Communications，技术通过 | Q 函数方向和两个输入值明确，`Q(0)=0.5` 提供独立算术校验点。 |
| H08 | Communications，技术通过 | 三个整数、三位宽和 LSB-first 位序全部明确，避免与默认 MSB-first 混淆。 |
| H09 | WLAN，技术通过 | 10 MHz、L-LTF、过采样 1 均明确；返回 FFT 64、采样率 10 MHz、CP `[32,0]` 采样点。与旧 D18 的数据字段不同。 |
| H10 | WLAN，技术通过 | 16QAM 对应每子载波四比特，八个输入比特映射为两个复符号，答案取实、虚部。 |
| H11 | Wireless Network，技术通过 | 包记录的主要物理字段已给定，其他属性明说沿用工具默认值；实际返回为顶层 `TransmitterID`、`Power`、`Data` 等键，并非 `/packet` 嵌套对象，已按返回结构修正答案路径。 |
| H12 | Wireless Network，修订后技术通过 | 区域中心、边界、网格、高度明确；改为单元**中心**放置，避免先前“左下角”说法与本地返回坐标不符。 |
| H13 | WirelessAgent Helper，仅技术契约测试 | 显式要求 `wireless_utils golay`，返回两条 16 项序列。自然语言不点名工具时还可选择 WLAN Golay 工具，因此本题**不能证明 Helper 的自然路由正确**；业务验收前需给出唯一产品场景或等价路线评分。 |
| H14 | Workflow，技术通过；规则检查范围 | `qos_policy_builder` 输出的 `qos_data` 经 `json` 绑定给 `policy_decision_validator`；容量可行且规则校验通过。没有实测 KPI，不能据此断言现场策略有效或已完成变更。 |
| H15 | Workflow，技术通过 | 接入 A 的时延超过 30 ms 约束，工具把业务流分到 B，未满足流数为 0；输入容量、时延、SNR 与滞回均已给定。 |
| H16 | Workflow，技术通过 | 明确是 SISO Shannon 理论上界；5 MHz、10 dB 对应 `5e6 × log2(11)` bps，并非现场吞吐承诺。 |
| H17 | LTE 信息不足，技术通过 | 缺数据比特和 CRC 多项式，应先问清，不应默认生成 CRC。当前自动评分用关键词匹配追问，需人工核对同义表达。 |
| H18 | Bluetooth 信息不足，技术通过 | 缺模式、包类型和载荷长度，应先问清。自动评分同样可能误判语义正确但措辞不同的回答。 |

## 验收边界与使用顺序

这批题的“独立”仅指题面、`scenario_id` 和 holdout 文件与已有开发题隔离，且 SkillOpt 训练入口只使用 train/selection。题目仍由同一项目资料设计，不能视为真实用户分布的随机样本；每个领域只有少量题，H13 还只是显式工具契约测试。不能用 18 题的成绩声称整个 144 工具箱全面改善。

所有题需先由负责产品用途和数据授权的人员逐题决定保留、改写或删除，再把获准的 train/selection 与 holdout 行合并成新的 JSONL，运行 `freeze-reviewed`。不要直接批量改 `review_status`，也不要把模拟结果当发布验收。若后续获得已脱敏且获准使用的用户题，应单独标 `origin_type: user_query` 并替换或补充 holdout；真实 holdout 只评估已在 selection 选定的技能版本，避免查看分数后反复调参。

离线重建及技术验证命令：

```powershell
.\.venv-skillopt\Scripts\python.exe -X utf8 -m scripts.build_workflow_review_draft --overwrite
.\.venv-skillopt\Scripts\python.exe -X utf8 -m scripts.build_independent_holdout_draft --overwrite
.\.venv-skillopt\Scripts\python.exe -X utf8 -m unittest scripts.test_independent_holdout_draft scripts.test_skillopt_workflow -v
```
