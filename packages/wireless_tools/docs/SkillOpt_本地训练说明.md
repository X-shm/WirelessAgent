# Wireless Toolbox × SkillOpt 本地训练

本目录为 MCP 工具调用技能提供离线优化流程。MCP 服务继续负责执行 `tool_registry.json` 中的 144 个工具；SkillOpt 只修改 agent 的工具选择、参数填写和回答规则。它不会因一次用户提问或 MCP 调用而自动启动。训练、评估和发布是独立的人工发起步骤。

## 当前交付

- `requirements-skillopt.txt` 将官方 SkillOpt 固定到 Git commit `343db229dbd5ddaf9df6b1d5540d8bcdb2604d5c`，同时安装现有 MCP 依赖。不要使用未经核验的浮动 `main`。
- `skillopt_wireless/` 提供数据生成、MCP 环境适配器、DeepSeek 目标模型调用、评分和命令行入口。
- `skills/wireless_mcp/seed_skill.md` 是独立的初始技能，不影响 `skills/wireless_numeric/`。
- `skillopt_data/splits/` 是经真实本地 MCP 调用生成的 144 × 3 条合成题，三组各覆盖全部工具。注册表变化后必须重新生成。
- `skillopt_runs/` 保存训练、评估、模型对话和结果；目录已在 `.gitignore` 中排除。密钥与用户原始日志不得写入仓库。

这些合成题主要验证调用链和基础路由；不代表真实用户问题的质量。发布前还须用经过审阅的真实业务题做独立验收。

## 专家草案的不可发布实验

2026-10-10 的[逐题取舍报告](SkillOpt_逐题取舍与训练选优扩充.md)和[筛选扩充草案](SkillOpt_筛选扩充草案.jsonl.example)包含 71 道仍为 `draft` 的专家设计题：train 28、selection 19、holdout 24。`freeze-draft` 会检查跨分组近似模板、重新调用本地 MCP 核对参考结果，并输出 `kind: draft_experiment`、`publishable: false` 的冻结数据。它不把题目改成 `approved`，也不能替代正式的 `freeze-reviewed`。当前已生成 `skillopt_data/experimental-001`；如更改草案，请使用新的输出目录。

在仓库根目录运行以下命令。当前 Codex 执行环境未检测到 DeepSeek 密钥，因此只完成了冻结与离线验证，**尚未运行下述付费训练**。在你自己的 PowerShell 会话中先检查密钥，再运行训练：

```powershell
Test-Path Env:DEEPSEEK_API_KEY
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless preflight
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless train `
  --cases skillopt_data\experimental-001 `
  --output skillopt_runs\experiment-001
```

训练时只读取 train 与 selection，配置会变为 train 28、batch 24、selection 19、`eval_test: false`、最多 4 轮工具交互。训练结束后会封存 selection 选中的 `best_skill.md`。**在选定技能之前不要运行下面的 holdout 评估**。选定后，仅做一次预先约定的诊断比较：

```powershell
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless evaluate `
  --cases skillopt_data\experimental-001 `
  --skill skillopt_runs\experiment-001\best_skill.md `
  --output skillopt_runs\experiment-001-holdout
```

比较会同时运行初始 Skill 和所选 Skill，输出 `comparison.json`；实验报告的 `evaluation_kind` 为 `draft_experiment`，`publishable` 固定为 `false`，`package` 会拒绝它。不要根据这次 holdout 的结果在同一题集上反复挑选技能。正式发布仍按下文的人工审核、`freeze-reviewed` 和独立验收流程执行。

## 安装与离线自检

在仓库根目录执行。当前工作区用 Python 3.13 完成安装；其他 Python 版本应先单独运行以下自检。

```powershell
python -m venv .venv-skillopt
.\.venv-skillopt\Scripts\python.exe -X utf8 -m pip install -r requirements-skillopt.txt
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless prepare
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless smoke
```

Linux 上将解释器路径换成 `.venv-skillopt/bin/python`。`prepare` 通过 MCP 逐项调用工具，生成 train、val、test 各 144 条互不相同的参数实例；`smoke` 用模拟目标模型跑完整 stdio MCP 链、评分和对话存档，不访问 DeepSeek。`skillopt_data/splits/manifest.json` 的 `complete` 必须为 `true`，`smoke` 的 `hard` 必须为 `1.0`。

## DeepSeek 预检、训练和诊断评估

当前配方以 `deepseek-flash` 为目标 agent，以 `deepseek-v4-pro` 为 SkillOpt 优化模型。两者都通过 OpenAI 兼容协议访问；合成题首轮强制工具调用，审核业务题则让目标模型自行判断是否需要工具。将密钥只放在当前进程的环境变量或受控密钥服务中：

```powershell
$env:DEEPSEEK_API_KEY = [System.Net.NetworkCredential]::new(
    "", (Read-Host "DeepSeek API Key" -AsSecureString)
).Password
# 如使用专用网关，再设置 $env:DEEPSEEK_BASE_URL
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless preflight
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless train --output skillopt_runs\trial-001
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless review-run --run skillopt_runs\trial-002
```

`preflight` 先验证 SkillOpt 优化模型的认证和 JSON 响应，再一次发送全部 144 个工具定义，确认目标模型接受当前工具目录。只需检查优化模型时可运行 `python -X utf8 -m skillopt_wireless optimizer-preflight`，它只发一条短请求。训练启动时也会自动执行这项短预检，认证失败会在跑题前停止。若供应商的请求限制、上下文或账户权限不允许调用，先处理供应商限制；本地离线自检不能替代这个检查。训练配置见 `skillopt_wireless/config.yaml`，默认合成题配方为 1 epoch、24 条训练批次、48 条验证题和 144 条训练结束时测试题。指定 `train --cases` 时，训练批次和 selection 大小随审核题集调整，训练结束时的 holdout 评估关闭。API 调用有费用；运行前可在配置中调低规模进行探索。

如果训练在中途报错，修复后用**相同的 `--output` 目录**重新执行 `train`。SkillOpt 根据 `runtime_state.json` 从最后完成的步骤继续；适配器会核对未完成步骤已保存的 `rollouts.json`、题目、技能提示词、模型、评分和对话文件，匹配时复用整批目标模型结果。校验不通过则重新调用目标模型。请保留原输出目录，并留意后续反思、验证和测试阶段仍会产生新的 API 调用。

若旧运行已经生成 `summary.json`，请用新目录重新训练。可以用 `--reuse-from` 读取旧运行中经逐项校验的目标模型结果，避免对未变化的题目和技能提示词重复计费。例如修复优化模型认证后：

```powershell
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless optimizer-preflight
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless train --output skillopt_runs\trial-002 --reuse-from skillopt_runs\trial-001
```

旧目录只读，新结果写入 `trial-002`。某一步若真正修改了技能，后续批次提示词不再匹配，适配器会重新调用目标模型；反思阶段的优化模型调用也仍需重新进行。

环境变量只在设置它的当前 PowerShell 窗口及其子进程中有效。先运行 `Test-Path Env:DEEPSEEK_API_KEY`，应返回 `True`；不要用会打印密钥值的命令检查。预检成功时应看到 `functions_sent: 144` 且 `tool_calls_received` 大于 0。若报错，可分享错误文本，但不要分享密钥。

`review-run` 离线分析一次已完成训练的初始、验证集选中和最后三个技能版本，输出逐题差异。旧合成 `test` 在训练结束时已经被调用并查看；不带 `--cases` 的 `evaluate` 只生成诊断报告，`publishable` 固定为 `false`。评分检查首个工具、参数、实际 MCP 结果和最终答案；审核业务题还检查 `answer_paths` 指定的必需字段。真实业务题模板、冻结与验收命令见 [SkillOpt_业务题标注与冻结.md](SkillOpt_业务题标注与冻结.md)。新的冻结 holdout 发布验收要求 selection 版本封存、全部产品领域及两类请求覆盖、至少两轮配对调用、每轮整体严格提升且各领域无回退、逐题胜负方向稳定、技能正文不超过 8 KB；失败轨迹及模型波动还需要人工复核。

## 生成待审阅交付包

只有经新的冻结业务 holdout 验收、人工复核后，才执行：

```powershell
.\.venv-skillopt\Scripts\python.exe -X utf8 -m skillopt_wireless package `
  --skill skillopt_runs\reviewed-001\best_skill.md `
  --comparison skillopt_runs\reviewed-001-holdout\comparison.json `
  --output skillopt_runs\reviewed-001-release
```

`package` 拒绝旧合成诊断或 `--mock` 的报告，并核对候选文件哈希。输出为 `SKILL.md` 和版本 `manifest.json`，供负责人审阅后手动接入服务器 agent 的技能或系统提示词配置。此命令不向 `wirelessagent.plus` 发布，也不修改 MCP 工具名、schema 或服务代码。服务器 agent 必须实际加载此技能，优化才会影响运行时调用。

## 数据与维护边界

当前训练数据来自 schema 示例及经过 MCP 验证的参数变体，不包含自动采集的线上提问。后续若要加入真实提问，应先取得可使用范围、脱敏并人工核对题目、期望工具、参数和结果，然后另建独立验证集，防止把训练题直接用作发布评估。禁止把原始用户日志、密钥或会话文件直接提交到仓库。

工具实现或 schema 变更后，先运行现有 MCP 测试，再重新执行 `prepare` 和 `smoke`；旧 `manifest.json` 的注册表摘要会阻止误用旧题集。单独改进技能提示词时，MCP 服务本身无需修改。SkillOpt 的依赖版本升级也应先重新跑本页自检和 DeepSeek 预检。
