# Contributing
> 欢迎参与 WirelessAgent 项目开发。
> 本文档为项目贡献者协作规范，请所有参与开发的人员阅读并遵守，用于统一开发流程、保障代码质量、确保科研实验可复现。
> Welcome to contribute to WirelessAgent.
> This document defines collaboration specifications for all contributors, to unify workflow, guarantee code quality and ensure research‑experiment reproducibility.

## Overview / 概述
本项目基于 GitHub 完成团队协同开发，致力于解决代码版本混乱、接口不匹配、任务缺少负责人、科研结果难以复现等协作问题。所有任务、代码变更、评审、版本发布均依托 GitHub Repository、Issue、Branch、Pull Request、GitHub Actions 完成。

We conduct collaborative development on GitHub. It solves typical pain points: messy code versions, incompatible interfaces, unassigned tasks, and non‑reproducible research results. All tasks, changes, reviews and releases are managed via GitHub Repository, Issue, Branch, Pull Request and GitHub Actions.

## Key GitHub Concepts / 核心概念说明

| Concept 概念 | Description 说明 |
|---|---|
| Repository 仓库 | 项目代码与文档仓库，`main` 分支受保护，**禁止直接推送代码**<br>Code & document repository. The `main` branch is protected. **Direct push is forbidden** |
| Issue 任务 | 需求、缺陷、开发任务全部通过 Issue 记录，写明负责人、输入输出、验收标准<br>Record feature requests, bugs and tasks. Assign assignee, define I/O and acceptance criteria |
| Branch 分支 | 每个任务使用独立分支；分支命名：`feature/xxx` 新功能，`bugfix/xxx` 缺陷修复<br>One independent branch per task. Naming: `feature/xxx` for features, `bugfix/xxx` for bug fixes |
| Pull Request (PR) 合并请求 | 代码变更的合并申请；必须由非作者完成评审，禁止自评 PR<br>Merge proposal for code changes. Review must be done by others. Self‑review is prohibited |
| GitHub Actions | CI 自动检查，包含代码规范、单元测试、集成测试；全部通过方可合并<br>Automated CI checks including lint, unit test and integration test. Must pass before merge |
| Release 版本发布 | 经过验收的可部署稳定版本，保留版本号、部署记录，支持版本回滚<br>Verified deployable release. Keep version tag & deployment log, support rollback |

## Development Workflow / 完整开发工作流

1. **Pick up task / 领取任务**
认领 Issue，确认任务范围、输入输出与验收标准，明确任务负责人。

Claim an Issue. Confirm scope, input‑output and acceptance criteria, confirm assignee.

2. **Create feature branch / 创建开发分支**
同步本地 `main` 到最新状态，创建 `feature/*` / `bugfix/*` 分支，在独立工作区开展开发。

Sync local `main` to upstream latest. Create `feature/*` / `bugfix/*` branch and develop in isolated worktree.

3. **Implement changes / 编码开发**
仅修改任务约定范围内的模块。如果涉及接口变更，需要提前与相关模块维护者沟通。频繁提交 commit 并推送到远端仓库。

Only modify modules within task scope. Discuss interface changes with related maintainers in advance. Make frequent commits and push to remote.

4. **Open Pull Request / 提交PR**
创建 PR，**关联对应 Issue**，补充改动说明，附上测试/实验结果，指定其他贡献者作为评审人。

Open PR, **link corresponding Issue**, describe changes, attach test / experiment evidence and assign reviewers from other contributors.

5. **Code Review & CI Checks / 代码评审与CI校验**
- GitHub Actions CI 所有检查必须全部通过，失败需要修复后重新提交。
- 由非作者完成代码评审，根据反馈修改代码后重新进入审核流程。

- All GitHub Actions CI checks must pass; fix failures before resubmit.
- Review must be performed by non‑author. Revise code according to feedback for re‑review.

6. **Merge into main / 合并主分支**
在评审批准、CI 全部通过后，合并到受保护的 `main` 分支。

Merge into protected `main` after review approval and all CI passed.

7. **Integration verification / 集成验证**
合并后在测试环境完成真实业务场景串联验收。

Perform end‑to‑end acceptance on staging environment after merge.

8. **Release / 版本发布**
由负责人执行 Release，保存版本记录，做好版本回滚预案。

Maintainer triggers Release, keep version records and prepare rollback plan.

> Workflow summary / 流程总览:
> Issue → Create branch → Commit & Push → PR + Review + CI → Merge to main → Release & Deploy
>
> This project adopts **GitHub Flow** / 本项目采用 GitHub Flow：
> short‑lived feature branches based on `main`, suitable for continuous iteration of AI‑oriented systems.
> 基于 main 创建短期功能分支，适合 AI 系统持续迭代。

## CI/CD Rules / CI/CD 规范

- **CI (Continuous Integration / 持续集成)**：每次 Push / PR 触发 GitHub Actions，自动执行：
  - Lint：代码格式与编码规范校验 / Code format & style check
  - Unit Test：单元测试 / Unit test
  - Integration：集成测试 / Integration test
- **CD (Continuous Delivery / 持续交付)**：将通过全部校验的代码打包，部署至测试或生产环境。
  Package verified code and deploy to staging or production environment.
- 🚨 Hard rule / 硬性规则: **PR cannot be merged if any CI check fails. CI不通过禁止合并PR。**

## Repository Structure & Module Ownership / 仓库目录与模块归属
This is a single‑repo project maintained by multiple groups.
本项目为单仓库架构，由多小组协同维护。

| Directory 目录 | Purpose 用途 | Responsible Team 负责团队 |
|---|---|---|
| `apps/web` | Chat & workspace frontend<br>聊天与工作界面 | Web & System Integration<br>网站与系统集成组 |
| `services/api` & `services/worker` | Session, task & background execution<br>会话、任务与后台执行逻辑 | Web & System Integration / Tool & Network Optimization<br>网站集成组 / 工具网络优化组 |
| `packages/knowledge` | RAG, knowledge base & paper processing<br>RAG、知识库与论文处理模块 | RAG & Knowledge Base<br>RAG与知识库组 |
| `packages/agent` & `wireless_tools` | Agent orchestration, wireless simulation & optimization<br>Agent任务编排、无线仿真优化 | Tool & Network Optimization<br>工具与网络优化组 |
| `contracts` / `benchmarks` / `infra` | Common interfaces, benchmarks & deployment config<br>公共接口、评测脚本、部署配置 | All groups (shared maintenance)<br>三组共同维护 |

> ⚠️ Do NOT commit large simulation data or big binary artifacts into git repository.
> 禁止将仿真大数据、二进制产物提交Git仓库。
> Store only version info & checksum in repo; put large assets to external storage system.
> 仓库仅保存版本与校验信息，大文件存放至外部存储。

> Research code requirement / 科研代码强制要求:
> - Unified input & output for algorithm modules. 算法模块统一输入输出。
> - Explicitly record units for power, distance, bandwidth. 功率、距离、带宽必须显式标注单位。
> - Preserve code version, parameters, random seed and raw results for every experiment to ensure reproducibility.
> 每次实验留存代码版本、参数、随机种子与原始结果，保障可复现。

## Daily Development Guidelines / 日常开发行为准则

### Before coding / 开发前
1. Sync your local `main` branch to upstream latest. Read related Issue and confirm acceptance criteria before creating your task branch.
同步本地 `main` 至远端最新，阅读 Issue 确认验收标准后再新建任务分支。
2. Any modification to public interfaces under `contracts` **must be discussed and agreed with related teams in advance. Do NOT modify shared interfaces without consensus.**
修改 `contracts` 公共接口**必须提前与相关小组沟通达成共识，禁止私自修改共享接口**。

### During development / 开发中
1. Modify only modules assigned to your current task. Avoid touching unrelated files.
仅修改当前任务分配模块，不要改动无关文件。
2. Make small, meaningful commits with clear commit messages. Avoid huge monolithic commits.
提交粒度尽量小，commit 信息清晰，避免一次性提交巨型变更。
3. If you use Codex / AI assistant for coding / 使用Codex等AI辅助开发时:
   - Provide full Issue context, allowed modification paths, interfaces, acceptance cases and test commands.
     提供完整Issue上下文、允许修改路径、接口、验收用例与测试命令。
   - AI‑generated code should live in an isolated worktree / branch.
     AI生成代码放在独立worktree/分支。
   - **Human review diff and run tests before opening PR. AI output cannot replace human validation.**
     **提交PR前人工审阅diff并执行测试，AI输出不能替代人工校验。**
   - It is recommended to work on one active task at a time; increase parallel tasks according to your reviewing capacity.
     建议同一时间只处理一个任务，根据评审能力再增加并行任务数量。

### Pull Request & Review / PR提交与评审
1. Link related Issue number in PR description. Attach test logs or experiment evidence.
PR描述中关联Issue编号，附带测试日志或实验证据。
2. Reviewer **must NOT be the PR author. Self‑review is forbidden.**
评审人不能是PR作者，禁止自评。
3. All CI failures shall be fixed before requesting review.
请求评审前修复全部CI报错。
4. Never push directly to `main`. All changes must go through PR.
禁止直接推送`main`，所有变更必须走PR流程。

## Multi‑layer Acceptance Check / 四层测试验收标准
Before merging or releasing, pass all following checks.
合并或发布前必须完成全部层级检查。

| Check Layer 检查层级 | Content 检查内容 | Responsible Role 负责角色 |
|---|---|---|
| Code Check 代码检查 | Format, unit test, interface compatibility<br>代码格式、单元测试、接口兼容性 | PR author + external reviewer<br>PR作者 + 外部评审人 |
| Research Check 科研检查 | Source, baseline, constraints, reproducibility<br>实验来源、算法基线、约束、可复现性 | Knowledge / algorithm module owner<br>知识库/算法模块负责人 |
| Integration Check 集成检查 | UI interaction, task start/cancel, file download<br>页面交互、任务启停、任务取消、文件下载 | Scenario owner<br>业务场景负责人 |
| Release Check 发布检查 | Permission, backup, image, rollback plan<br>权限、备份、镜像、回滚预案 | Release owner & technical lead<br>发布人 & 技术负责人 |

> Rule / 规则: Verify full real‑world scenarios on staging environment first, then promote to production.
> 先在测试环境完成完整真实场景验证，再发布到生产环境。
> Long‑running simulation jobs should run on background worker; tasks should be traceable even after page closed.
> 长时间仿真任务交给后台worker执行，页面关闭后任务依然可追踪。

## Violations & Enforcement / 违规约束
1. Direct push to `main` branch is strictly forbidden; all changes must pass PR workflow.
严禁直接向`main`推送代码，所有变更必须走PR流程。
2. Do NOT force‑merge PR with failing CI jobs.
CI失败不允许强行合并PR。
3. Unauthorized modification to shared `contracts` interfaces will cause PR rejection.
未经协商修改`contracts`公共接口将直接驳回PR。
4. Research‑related PR lacking parameters, seeds or experiment records will be sent back for revision.
科研类PR缺少参数、随机种子、实验记录将被打回修改。
5. Self‑review of your own PR is not allowed.
不允许评审自己提交的PR。

> This document applies to all contributors. When specification needs update, discuss within team then revise this file.
> 本文档适用于全部贡献者。若规范需要更新，需团队讨论后修改本文件。