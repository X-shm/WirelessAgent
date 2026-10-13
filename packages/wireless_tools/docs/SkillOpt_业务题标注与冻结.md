# SkillOpt 业务题标注与冻结

当前没有已获准使用且已脱敏的真实用户原题。人工审核应以[71 题合并草案](SkillOpt_筛选扩充草案.jsonl.example)和[逐题取舍报告](SkillOpt_逐题取舍与训练选优扩充.md)为起点：train 28、selection 19、holdout 24，均为 `expert_authored`、`draft`。参考结果已由本地 MCP 复算，且已通过 `freeze-draft` 冻结到 `skillopt_data/experimental-001`，仅供不可发布实验。网站产品用途、题目来源权限与最终答案是否符合真实业务仍需人工确认。

原始 26 题、4 道工作流题、18 道独立验收候选题及其逐题审核保存在 [skillopt_review/](skillopt_review/) 供追溯；不要把它们当成当前合并草案之外的独立发布证据。[标注模板](reviewed_cases_template.jsonl.example)仅展示格式，不能直接导入。现有 `skillopt_data/splits` 是已看过的合成诊断题，也不能改名为业务验收集。

## 标注格式

复制模板至仓库忽略的 `skillopt_data/reviewed_imports/`，一行一题，UTF-8 JSONL。每题必须包含：

| 字段 | 要求 |
|---|---|
| `id` | 唯一稳定 ID，2–100 位英文字母、数字、`_`、`-` |
| `split` | `train`、`selection` 或 `holdout` |
| `scenario_id` | 同一业务场景的所有改写使用同一 ID，不能跨组 |
| `question` | 经许可且已脱敏的用户原题，或经业务人员核对的专家设计场景问法；不含答案或期望工具提示 |
| `origin_type` | `user_query`、`expert_authored` 或 `public_example`；三者在结果中分开统计 |
| `source_ref` | 可内部追溯的脱敏来源代号，不写原始用户 ID、日志或工单正文 |
| `reviewer`、`review_status` | 人工核对者的代号；核对及授权完成后设为 `approved` |
| `kind`、`tool` | `tool_call` 表示具备参数应调用指定工具；`ask_clarification` 表示应先询问缺少的参数，此时 `tool` 标注相关工具 |
| `steps`、`answer_fields` | `tool_workflow` 必填：2–5 个有序工具步骤及最终答案字段；顶层 `tool` 可省略，由首个步骤决定主领域 |
| `arguments`、`expected` | `tool_call` 必填，分别为 MCP 参数对象与本地 MCP 结构化参考结果；结果含路径时使用 `<DATA_ROOT>` |
| `answer_paths` | `tool_call` 必填，列出用户真正需要的结果字段，以 JSON Pointer 表示，例如 `/output`、`/artifacts/file`；答案必须包含这些字段 |
| `answer_terms` | `ask_clarification` 必填，列出回答中必须提到的缺失信息关键词；此类型不填 `arguments` 或 `expected` |

`tool_workflow` 的 `steps` 按调用顺序列出 2–5 个工具。每步保存 `tool`、`arguments` 和完整 MCP `expected`；从前一步结果传值时，用 `bindings` 指定当前参数名、`from_step`（从 0 开始）、结果的 JSON Pointer `path`，以及 `identity`、`string`、`json` 或 `csv` 格式。`answer_fields` 把最终答案字段映射到指定步骤的结果路径。当前评分要求严格按顺序调用；若一道题允许多条同样正确的工具路线，须先调整标注或改用人工判分。完整样例见[71 题合并草案](SkillOpt_筛选扩充草案.jsonl.example)中的 W01、W02、A25 和 A28；早期说明见[多工具题说明](skillopt_review/SkillOpt_多工具题说明.md)。

人工检查问题可否按原意复现、工具与参数是否正确、数值及文件返回是否可信，且确认来源允许用于此评估。逐题确定保留、修改或删除，再将确认的行复制到新的审核文件；不得批量把草稿改成 `approved`。来源与审批事实由数据提供方负责；程序只检查标注字段、重复题目、场景隔离和参考 MCP 结果。相同问题即使换 ID 也会被拒绝。各组至少一题；正式验收时应覆盖 5G、蓝牙、高频任务、易混工具、长结果、文件工具和信息不足的请求。模板示例本身不算覆盖。若 holdout 全部来自 `expert_authored`，结论仅能说明对这些设计场景的表现，不能推断真实用户提问分布。

每条题应可独立执行，不依赖上一题生成的会话或文件。当前自动评分要求工具调用题最终返回 `<answer>` 包裹的 JSON，包含全部 `answer_paths` 指定的字段，且值与 MCP 结果一致；信息不足题要求不调用工具，并明确询问 `answer_terms` 中的缺失项。发布前仍需人工检查回答是否真正满足用户问题。

## 冻结与使用

```powershell
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless freeze-reviewed `
  --input skillopt_data\reviewed_imports\approved.jsonl `
  --output skillopt_data\reviewed_imports\freeze-001
```

冻结命令通过本地 MCP 逐题重算 `tool_call` 参考结果，检查题目和场景没有跨组泄漏，并记录输入、工具注册表、各组覆盖情况和三个输出分组的 SHA-256。输出目录必须为空。冻结后不要编辑 `items.json`；内容变动会被训练与评估入口拒绝。审批、脱敏和答案判断仍需人工负责。

```powershell
# 可选：只用 train/selection 训练；训练时禁止 SkillOpt 评估 holdout。
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless train `
  --cases skillopt_data\reviewed_imports\freeze-001 `
  --output skillopt_runs\reviewed-001

# 训练正常结束会自动封存 selection 选中的 best_skill.md。
# 仅当训练已完成但 selection.json 缺失时，离线补建封存记录：
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless seal-selection `
  --run skillopt_runs\reviewed-001 `
  --cases skillopt_data\reviewed_imports\freeze-001

# 先做不联网的链路测试，结果永远不能通过发布门槛。
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless evaluate `
  --cases skillopt_data\reviewed_imports\freeze-001 `
  --skill skillopt_runs\reviewed-001\best_skill.md --mock `
  --output skillopt_runs\reviewed-001-mock

# 仅在候选由 selection 预先选定后，运行一次真实 holdout 验收。
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless evaluate `
  --cases skillopt_data\reviewed_imports\freeze-001 `
  --skill skillopt_runs\reviewed-001\best_skill.md `
  --repeats 2 `
  --output skillopt_runs\reviewed-001-holdout
```

`comparison.json` 记录候选路径、内容哈希、数据集哈希、逐题配对结果、各领域分数、覆盖缺口及重复调用的方向波动。自动门槛要求 holdout 覆盖注册表全部产品领域，以及 `tool_call` 和 `ask_clarification` 两类请求；候选是同一冻结题集训练所得、已封存的 `best_skill.md`；至少做两轮真实调用，且每轮整体提高、各领域无回退，同一题的胜负方向一致。`--repeats 2` 会增加 API 用量与费用。`--mock` 和未指定 `--cases` 的旧合成题评估均标记不可发布。候选应只根据 selection 确定；查看 holdout 后不能再从多个技能版本中挑最高分。关键差异和模型波动仍须人工复核；当题量不足以支持稳健结论时，即使自动门槛通过也不要发布。
