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
| 标准检索 | 3GPP 协议检索与官方 PDF 引用 |
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

### 3GPP 标准检索

在后端工作目录安装 `requirements-app.txt` 中的依赖。服务器发布后该文件位于 `backend/requirements.txt`。将向量包、证据 JSONL 和 PDF 资产放在外部数据目录，在 `wireless-agent` 服务环境设置 `DASHSCOPE_API_KEY`。

网页选择「默认模型」时，后端使用服务端的 `OPENCLAW_API_KEY` 连接生成网关。用户只有选择「自定义配置」时才需要填写自己的生成服务接口地址、API Key 和模型名。标准检索的 Qwen 向量编码和重排始终使用服务端的 DashScope Key。

旧版 BGE 知识库的 `/api/rag/search` 和 `/api/rag/reindex` 接口已下线。服务器的旧 `.env` 仍可包含 `EMBEDDING_MODEL`，升级后可移除该行。

从后端工作目录导入索引，使 `--chroma-dir` 与 `CHROMA_PERSIST_DIR` 一致（默认 `./chroma_data`）。`--pdf-root` 是 PDF manifest 中 `pdf_path` 的基准目录。向运行环境的本地 Chroma 目录导入前先停止访问该目录的服务。完整导入并核对 Chunk ID 后才更新活动清单。导入中断可用同一条命令继续，旧集合须保留到相关请求的续跑窗口结束。

```bash
python -m app.services.protocol_index --vectors-dir "$VECTORS_DIR" --evidence-dir "$EVIDENCE_DIR" --pdf-root "$PDF_ROOT" --pdf-manifest "$PDF_MANIFEST" --chroma-dir ./chroma_data
```

章节路径参与 BM25 和重排。上线页码追溯前，用本版本的导入器和同一批 NPZ、JSONL 建立来源元数据 v3 的集合。部署预检会核对该版本。Dense 继续使用预计算向量。

导入时会核对原文的页内字符范围和正文。旧语料可通过条款范围内的唯一完整匹配定位证据页。跨页 Chunk 在生成上下文中按页标注，检索仍使用原 Chunk。若只能定位到条款起始页，网页会标注「条款起始页」；没有可核实的页码时，打开同版本官方 PDF。

可用「只用 TS 23.501」「TS 29.512 Rel-17」或「对比 TS 29.512 v17.6.0 和 v19.7.0」指定证据范围。Dense 和 BM25 先按文档范围过滤，再取候选。请求日志记录解析结果及有效文档 ID。任一指定范围未入库时，页面会提示调整范围。

部署脚本会在替换代码前检查后端 Python 环境是否已安装 `rank-bm25`、已配置 Key 并能打开完整索引。若脚本无法识别服务使用的 Python，可设置 `WIRELESS_AGENT_PYTHON`。部署后从「工作 → 标准检索」使用真实服务检查问答、同版本 PDF 和日志。

检索检查点和流式事件写入应用 SQL 数据库，默认保留 24 小时。浏览器重连时按序号恢复；若生成服务的处理结果未知，用户可以手动重试，生成从已保存的证据重新开始。点击「停止」会取消服务端请求和正在提取的附件。单个附件最多提取 15 秒，超时后跳过该附件。已显示的片段保留在问答日志，完整答案和结构化引用才会进入会话历史。后端每进程同时处理最多两个标准检索请求，单请求处理期限为 180 秒，包含排队。运行依赖现有数据库和 Chroma。

运维可在后端工作目录使用以下命令导出近期评测样本。

```bash
umask 077
python -m app.services.protocol_log_export --limit 100 > protocol-search-samples.jsonl
```

导出包含请求 ID、候选顺序、为生成准备的 Chunk ID、网关是否确认受理、已确认受理的上下文 Chunk ID、答案及引用，并遮蔽常见邮箱、手机号和凭据格式。分享前复核问答自由文本中的敏感信息。全文复核和调参在线下完成。

## 参与贡献 / Contributing

本项目采用 **GitHub Flow**，所有变更通过「Issue → 分支 → PR → 评审 → CI」流程合入，`main` 分支受保护。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证 / License

待定。
