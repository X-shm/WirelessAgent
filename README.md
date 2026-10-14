# WirelessAgent

面向无线通信研究的 **AI Agent 平台**：用自然语言完成习题解答、标准检索、论文研读、网络规划与报告生成。

An **AI agent platform** for wireless communications research.

---

## 简介 / Overview

WirelessAgent 是一个面向无线通信研究者的垂直 AI Agent 平台，将大模型 Agent 能力与无线通信领域知识（3GPP / IEEE 标准、学术论文、仿真工具）相结合，支持多用户会话隔离、流式对话与可复现的科研计算。

## 核心能力 / Features

| 模块 | 说明 |
|---|---|
| 习题解答 | 通信计算题分步解答、知识点延伸与错题本 |
| 标准检索 | 3GPP / IEEE 文档 RAG 检索 |
| 论文速递 / Agent2Paper | 论文抓取、摘要生成与虚拟作者问答 |
| 网规辅助 | 链路预算 → SINR 热图 |
| 报告生成 | 结构化报告导出 |

## 仓库结构 / Repository Structure

| 目录 | 用途 | 负责团队 |
|---|---|---|
| `apps/web` | 聊天与工作界面 | 网站与系统集成组 |
| `services/api` · `services/worker` | 会话、任务与后台执行 | 网站与系统集成组 / 工具与网络优化组 |
| `packages/knowledge` | RAG、知识库与论文处理 | RAG与知识库组 |
| `packages/agent` · `wireless_tools` | Agent 任务编排、无线仿真优化 | 工具与网络优化组 |
| `contracts` / `benchmarks` / `infra` | 公共接口、评测脚本、部署配置 | 三组共同维护 |

## 快速开始 / Getting Started

首个可运行的端到端仿真切片是 BLE 发射功率与距离扫描：独立任务页、版本化任务 API、持久队列、固定 Agent 编排器及 MCP 工具调用。它可以在本地与预发环境运行，不代表整个 WirelessAgent 平台或所有仿真场景已经集成。启动、接口和验收命令见 [BLE 仿真任务接入说明](docs/BLE仿真任务接入说明.md)。

## 参与贡献 / Contributing

本项目采用 **GitHub Flow**，所有变更通过「Issue → 分支 → PR → 评审 → CI」流程合入，`main` 分支受保护。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证 / License

待定。
