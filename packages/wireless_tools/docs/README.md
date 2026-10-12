# 文档导航

本目录按 **当前操作**、**待审题集** 和 **技术参考** 区分。当前工作以 144 个 MCP 工具和 71 道 SkillOpt 专家草案为基线。云服务器上的 agent 接入尚待端到端验证；71 道题仍是 `draft`，实验结果不可作为发布验收。

## 当前操作

| 需要做什么 | 阅读 |
|---|---|
| 接入服务器 agent 并验证 MCP 调用 | [MCP 接入说明](MCP_接入说明.md) |
| 修改工具、schema 或注册表 | [工具接口契约规范](工具接口契约规范.md) |
| 本地安装、预检、训练及诊断实验 | [SkillOpt 本地训练说明](SkillOpt_本地训练说明.md) |
| 审核业务题、冻结数据及独立验收 | [SkillOpt 业务题标注与冻结](SkillOpt_业务题标注与冻结.md) |

模块当前进度见 [INTEGRATION_STATUS.md](../INTEGRATION_STATUS.md)。工具列表以 `tool_registry.json` 和 `tools/*.schema.json` 为准。

## 当前待审题集

- [71 题合并草案](SkillOpt_筛选扩充草案.jsonl.example)：train 28、selection 19、holdout 24；全部为专家设计的 `draft`。已冻结到 `skillopt_data/experimental-001` 供不可发布实验使用。
- [逐题取舍与扩充记录](SkillOpt_逐题取舍与训练选优扩充.md)：说明原 48 题的保留、修改、删除以及新增 28 题的依据。
- [标注模板](reviewed_cases_template.jsonl.example)：仅示范 JSONL 格式，不是可训练或可验收的题集。

## 技术参考

- [原始题集与逐题审核](skillopt_review/)：D01–D26、W01–W04、H01–H18 的 JSONL、题面和技术审核。原始 JSONL 仍供生成脚本、测试与取舍记录追溯；**当前人工审核请以 71 题合并草案为起点**。
