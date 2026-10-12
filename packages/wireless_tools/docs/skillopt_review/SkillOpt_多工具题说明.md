# SkillOpt 多工具题格式与本地试跑

当前支持 `tool_workflow` 题型：一题记录 2–5 个**有序** MCP 调用、可选的前后步骤传值关系，以及最终答案必须包含的字段。原有 `tool_call` 和 `ask_clarification` 题型继续可用。该功能只改变本地 SkillOpt 的题目、执行轨迹和评分；MCP 工具接口不因题型改变。

## 待审试题

[多工具候选题 JSONL](SkillOpt_多工具候选题.jsonl.example)由 `scripts/build_workflow_review_draft.py` 通过真实本地 MCP 生成。四题均是 `expert_authored`、`review_status: draft`，没有真实用户来源或业务批准：

| ID | 暂定分组 | 期望流程 | 关键传值 |
|---|---|---|---|
| W01 | train | `lte_mcs` → `lte_tbs` | 第一步的 `itbs` 转字符串传给第二步 |
| W02 | selection | `nr_mcs_tables` → `nr_tbs` | 第一步的调制方式、目标码率传给第二步 |
| W03 | holdout | `convert_snr` → `ber_awgn` | 第一步的 Eb/N0 转字符串传给第二步 |
| W04 | train | `radio_link_diagnosis` → `link_adaptation_optimizer` → `closed_loop_validator` | 三个阶段按顺序执行；测量与前后 KPI 已在题面提供，不声明工具间数值传值 |

W04 只是可执行的三阶段示例：`closed_loop_validator` 核对题面给定的前后 KPI，并不执行网络变更。W01–W04 不能单独构成正式训练或发布验收集；该四题文件的 holdout 只有一题。另有隔离保存的 [18 道独立验收候选题](SkillOpt_独立验收候选题.jsonl.example)；逐题技术审核及限制见[审核报告](SkillOpt_多工具及独立验收逐题审核.md)。

## 一条题目的核心字段

```json
{
  "kind": "tool_workflow",
  "steps": [
    {"tool": "lte_mcs", "arguments": {"imcs": "18", "table": "PDSCH"}, "expected": {"...": "完整 MCP 结果"}},
    {"tool": "lte_tbs", "arguments": {"nprb": 18, "itbs": "16", "smnlayer": 1},
     "bindings": [{"argument": "itbs", "from_step": 0, "path": "/itbs", "format": "string"}],
     "expected": {"...": "完整 MCP 结果"}}
  ],
  "answer_fields": {
    "mod": {"step": 0, "path": "/mod"},
    "tbs": {"step": 1, "path": "/tbs"}
  }
}
```

完整行还需原有 `id`、`split`、`scenario_id`、`question`、`origin_type`、`source_ref`、`reviewer` 和 `review_status`。`tool` 顶层字段可省略；冻结时会由第一步工具确定主领域。每步 `arguments` 和 `expected` 都是对象，后者保存本地 MCP 的完整规范化结果。`bindings` 的 `from_step` 为从 0 开始的**较早步骤**；`path` 是该步骤结果中的 JSON Pointer；`argument` 是当前工具的顶层参数名；`format` 可为 `identity`、`string`、`json`（列表或对象序列化为 JSON 字符串）或 `csv`（标量列表变为逗号分隔字符串）。`answer_fields` 将最终 `<answer>` JSON 的字段映射到某一步的结果路径。

冻结时先检查审核字段、工具存在、传值与参考结果一致，再按顺序重新调用每个 MCP 工具。运行时要求工具名和调用次数严格匹配预期步骤，每一步必须在前一步的结果返回后发起；评分同时检查参数、实际结果及最终答案字段。答案中的额外字段也必须可从某一步实际结果摘录，不能臆造。多余调用、乱序、同轮并发依赖步骤或错误传值均不能通过。训练与独立评估会按最长工作流自动增加允许的对话轮数；本格式最多 5 个工具步骤。

目前仅支持**单一路径、严格顺序**的题。若同一业务问题存在多个同样正确的工具路线，需先定义允许的路线或人工判分，不能把另一条有效路线当作失败。自动评分也不能代替业务人员判断诊断建议和网络策略是否适用。

## 本地验证，不调用 DeepSeek

```powershell
.\.venv-skillopt\Scripts\python.exe -X utf8 -m scripts.build_workflow_review_draft --overwrite
.\.venv-skillopt\Scripts\python.exe -X utf8 -m unittest scripts.test_skillopt_workflow scripts.test_skillopt_reviewed -v
```

测试仅在临时目录内把试题标为技术测试用的 `approved`，用来运行冻结与模拟 agent；仓库中的草稿始终保持 `draft`。正式使用时，把经业务方逐题核对并明确来源的案例连同单工具题、信息不足题一起准备为新的 JSONL，按[业务题标注与冻结说明](../SkillOpt_业务题标注与冻结.md)执行 `freeze-reviewed`。不要以这四题的模拟成绩宣称 SkillOpt 已提高真实业务效果。
