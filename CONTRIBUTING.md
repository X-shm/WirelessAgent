# Contributing
> 欢迎参与 WirelessAgent 项目开发。
> 本文档定义项目贡献者协作规范，请所有参与开发人员阅读并遵守，用于统一开发流程、保障代码质量、确保科研实验可复现。

> Welcome to contribute to WirelessAgent.
> This document defines collaboration specifications for all contributors, to unify workflow, guarantee code quality and ensure research‑experiment reproducibility.

---

## 概述
本项目基于 GitHub 开展团队协同开发，解决代码版本混乱、接口不匹配、任务缺少负责人、科研结果难以复现等协作痛点。所有任务、代码变更、评审、版本发布均通过 GitHub Repository、Issue、Branch、Pull Request、GitHub Actions 完成。

## Overview
We conduct collaborative development on GitHub. It solves typical pain points: messy code versions, incompatible interfaces, unassigned tasks, and non‑reproducible research results. All tasks, changes, reviews and releases are managed via GitHub Repository, Issue, Branch, Pull Request and GitHub Actions.

---

## 核心 GitHub 概念说明

| 概念 | 说明 |
|---|---|
| Repository 仓库 | 项目代码与文档仓库，`main` 分支受保护，**禁止直接推送代码** |
| Issue 任务 | 需求、缺陷、开发任务全部通过 Issue 记录，写明负责人、输入输出、验收标准 |
| Branch 分支 | 每个任务使用独立分支；分支命名：`feature/xxx` 新功能，`bugfix/xxx` 缺陷修复 |
| Pull Request (PR) 合并请求 | 代码变更的合并申请；必须由非作者完成评审，禁止自评 PR |
| GitHub Actions | CI 自动检查，包含代码规范、单元测试、集成测试；全部通过方可合并 |
| Release 版本发布 | 经过验收的可部署稳定版本，保留版本号、部署记录，支持版本回滚 |

## Key GitHub Concepts

| Concept | Description |
|---|---|
| Repository | Code & document repository. The `main` branch is protected. **Direct push is forbidden** |
| Issue | Record feature requests, bugs and tasks. Assign assignee, define I/O and acceptance criteria |
| Branch | One independent branch per task. Naming: `feature/xxx` for features, `bugfix/xxx` for bug fixes |
| Pull Request (PR) | Merge proposal for code changes. Review must be done by others. Self‑review is prohibited |
| GitHub Actions | Automated CI checks including lint, unit test and integration test. Must pass before merge |
| Release | Verified deployable release. Keep version tag & deployment log, support rollback |

---

## 完整开发工作流
1. **领取任务**
认领 Issue，确认任务范围、输入输出与验收标准，明确任务负责人。

2. **创建开发分支**
同步本地 `main` 到最新状态，创建 `feature/*` / `bugfix/*` 分支，在独立工作区开展开发。

3. **编码开发**
仅修改任务约定范围内的模块。如果涉及接口变更，需要提前与相关模块维护者沟通。频繁提交 commit 并推送到远端仓库。

4. **提交 PR**
创建 PR，**关联对应 Issue**，补充改动说明，附上测试/实验结果，指定其他贡献者作为评审人。

5. **代码评审与 CI 校验**
- GitHub Actions CI 所有检查必须全部通过，失败需要修复后重新提交。
- 由非作者完成代码评审，根据反馈修改代码后重新进入审核流程。

6. **合并主分支**
在评审批准、CI 全部通过后，合并到受保护的 `main` 分支。

7. **集成验证**
合并后在测试环境完成真实业务场景串联验收。

8. **版本发布**
由负责人执行 Release，保存版本记录，做好版本回滚预案。

> 流程总览：Issue → 创建分支 → 提交代码 → PR + 评审 + CI → 合并 main → 发布部署
> 本项目采用 GitHub Flow：基于 main 创建短期功能分支，适合 AI 系统持续迭代。

## Development Workflow
1. **Pick up task**
Claim an Issue. Confirm scope, input‑output and acceptance criteria, confirm assignee.

2. **Create feature branch**
Sync local `main` to upstream latest. Create `feature/*` / `bugfix/*` branch and develop in isolated worktree.

3. **Implement changes**
Only modify modules within task scope. Discuss interface changes with related maintainers in advance. Make frequent commits and push to remote.

4. **Open Pull Request**
Open PR, **link corresponding Issue**, describe changes, attach test / experiment evidence and assign reviewers from other contributors.

5. **Code Review & CI Checks**
- All GitHub Actions CI checks must pass; fix failures before resubmit.
- Review must be performed by non‑author. Revise code according to feedback for re‑review.

6. **Merge into main**
Merge into protected `main` after review approval and all CI passed.

7. **Integration verification**
Perform end‑to‑end acceptance on staging environment after merge.

8. **Release**
Maintainer triggers Release, keep version records and prepare rollback plan.

> Workflow summary: Issue → Create branch → Commit & Push → PR + Review + CI → Merge to main → Release & Deploy
> This project adopts **GitHub Flow**: short‑lived feature branches based on `main`, suitable for continuous iteration of AI‑oriented systems.

---

## CI/CD 规范
- **CI（持续集成）**：每次 Push / PR 触发 GitHub Actions，自动执行：
  - Lint：代码格式与编码规范校验
  - Unit Test：单元测试
  - Integration：集成测试
- **CD（持续交付）**：将通过全部校验的代码打包，部署至测试或生产环境。
- 🚨 **硬性规则：CI 全部检查不通过，禁止合并 PR。**

## CI/CD Rules
- **CI (Continuous Integration)**: GitHub Actions is triggered on each Push / PR and automatically runs:
  - Lint: Code format & style check
  - Unit Test: Unit test
  - Integration: Integration test
- **CD (Continuous Delivery)**: Package verified code and deploy to staging or production environment.
- 🚨 **Hard rule: PR cannot be merged if any CI check fails.**

---

## 仓库目录与模块归属
本项目为单仓库架构，由多小组协同维护。

| 目录 | 用途 | 负责团队 |
|---|---|---|
| `apps/web` | 聊天与工作界面 | 网站与系统集成组 |
| `services/api` & `services/worker` | 会话、任务与后台执行逻辑 | 网站与系统集成组 / 工具与网络优化组 |
| `packages/knowledge` | RAG、知识库与论文处理模块 | RAG与知识库组 |
| `packages/agent` & `wireless_tools` | Agent任务编排、无线仿真优化 | 工具与网络优化组 |
| `contracts` / `benchmarks` / `infra` | 公共接口、评测脚本、部署配置 | 三组共同维护 |

> ⚠️ 禁止将仿真大数据、二进制产物提交 Git 仓库。仓库仅保存版本与校验信息，大文件存放至外部存储。
>
> **科研代码强制要求**
> - 算法模块统一输入输出。
> - 功率、距离、带宽必须显式标注单位。
> - 每次实验留存代码版本、参数、随机种子与原始结果，保障可复现。

## Repository Structure & Module Ownership
This is a single‑repo project maintained by multiple groups.

| Directory | Purpose | Responsible Team |
|---|---|---|
| `apps/web` | Chat & workspace frontend | Web & System Integration |
| `services/api` & `services/worker` | Session, task & background execution | Web & System Integration / Tool & Network Optimization |
| `packages/knowledge` | RAG, knowledge base & paper processing | RAG & Knowledge Base |
| `packages/agent` & `wireless_tools` | Agent orchestration, wireless simulation & optimization | Tool & Network Optimization |
| `contracts` / `benchmarks` / `infra` | Common interfaces, benchmarks & deployment config | All groups (shared maintenance) |

> ⚠️ Do NOT commit large simulation data or big binary artifacts into git repository.
> Store only version info & checksum in repo; put large assets to external storage system.
>
> **Research code requirement**
> - Unified input & output for algorithm modules.
> - Explicitly record units for power, distance, bandwidth.
> - Preserve code version, parameters, random seed and raw results for every experiment to ensure reproducibility.

---

## 日常开发行为准则
### 开发前
1. 同步本地 `main` 至远端最新，阅读 Issue 确认验收标准后再新建任务分支。
2. 修改 `contracts` 公共接口**必须提前与相关小组沟通达成共识，禁止私自修改共享接口**。

### 开发中
1. 仅修改当前任务分配模块，不要改动无关文件。
2. 提交粒度尽量小，commit 信息清晰，避免一次性提交巨型变更。
3. 使用 Codex / AI 辅助开发时：
   - 提供完整 Issue 上下文、允许修改路径、接口、验收用例与测试命令。
   - AI 生成代码放在独立 worktree / 分支。
   - **提交 PR 前人工审阅 diff 并执行测试，AI 输出不能替代人工校验。**
   - 建议同一时间只处理一个任务，根据评审能力再增加并行任务数量。

### PR 提交与评审
1. PR 描述中关联 Issue 编号，附带测试日志或实验证据。
2. 评审人不能是 PR 作者，禁止自评。
3. 请求评审前修复全部 CI 报错。
4. 禁止直接推送 `main`，所有变更必须走 PR 流程。

## Daily Development Guidelines
### Before coding
1. Sync your local `main` branch to upstream latest. Read related Issue and confirm acceptance criteria before creating your task branch.
2. Any modification to public interfaces under `contracts` **must be discussed and agreed with related teams in advance. Do NOT modify shared interfaces without consensus.**

### During development
1. Modify only modules assigned to your current task. Avoid touching unrelated files.
2. Make small, meaningful commits with clear commit messages. Avoid huge monolithic commits.
3. If you use Codex / AI assistant for coding:
   - Provide full Issue context, allowed modification paths, interfaces, acceptance cases and test commands.
   - AI‑generated code should live in an isolated worktree / branch.
   - **Human review diff and run tests before opening PR. AI output cannot replace human validation.**
   - It is recommended to work on one active task at a time; increase parallel tasks according to your reviewing capacity.

### Pull Request & Review
1. Link related Issue number in PR description. Attach test logs or experiment evidence.
2. Reviewer **must NOT be the PR author. Self‑review is forbidden.**
3. All CI failures shall be fixed before requesting review.
4. Never push directly to `main`. All changes must go through PR.

---

## 四层测试验收标准
合并或发布前必须完成全部层级检查。

| 检查层级 | 检查内容 | 负责角色 |
|---|---|---|
| 代码检查 | 代码格式、单元测试、接口兼容性 | PR作者 + 外部评审人 |
| 科研检查 | 实验来源、算法基线、约束、可复现性 | 知识库/算法模块负责人 |
| 集成检查 | 页面交互、任务启停、任务取消、文件下载 | 业务场景负责人 |
| 发布检查 | 权限、备份、镜像、回滚预案 | 发布人 & 技术负责人 |

> 规则：先在测试环境完成完整真实场景验证，再发布到生产环境。
> 长时间仿真任务交给后台 worker 执行，页面关闭后任务依然可追踪。

## Multi‑layer Acceptance Check
Before merging or releasing, pass all following checks.

| Check Layer | Content | Responsible Role |
|---|---|---|
| Code Check | Format, unit test, interface compatibility | PR author + external reviewer |
| Research Check | Source, baseline, constraints, reproducibility | Knowledge / algorithm module owner |
| Integration Check | UI interaction, task start/cancel, file download | Scenario owner |
| Release Check | Permission, backup, image, rollback plan | Release owner & technical lead |

> Rule: Verify full real‑world scenarios on staging environment first, then promote to production.
> Long‑running simulation jobs should run on background worker; tasks should be traceable even after page closed.

---

## 违规约束
1. 严禁直接向 `main` 推送代码，所有变更必须走 PR 流程。
2. CI 失败不允许强行合并 PR。
3. 未经协商修改 `contracts` 公共接口将直接驳回 PR。
4. 科研类 PR 缺少参数、随机种子、实验记录将被打回修改。
5. 不允许评审自己提交的 PR。

> 本文档适用于全部贡献者。若规范需要更新，需团队讨论后修改本文件。

## Violations & Enforcement
1. Direct push to `main` branch is strictly forbidden; all changes must pass PR workflow.
2. Do NOT force‑merge PR with failing CI jobs.
3. Unauthorized modification to shared `contracts` interfaces will cause PR rejection.
4. Research‑related PR lacking parameters, seeds or experiment records will be sent back for revision.
5. Self‑review of your own PR is not allowed.

> This document applies to all contributors. When specification needs update, discuss within team then revise this file.
