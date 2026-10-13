# Wireless Toolbox MCP 接入说明

这个目录提供一个独立的 MCP 服务。它读取现有 `tool_registry.json` 和工具 schema，调用原有 `tools/*.py`，不重写计算算法。当前注册的 **144 个 CLI 工具全部通过 MCP `tools/list` 暴露**，并以各自 schema 示例完成 MCP 客户端端到端调用测试。

## 安装与启动

建议 Python 3.11 或更新版本。在仓库根目录建立虚拟环境并安装依赖：

```bash
python -m venv .venv
# Linux: . .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-mcp.txt
```

作为本机子进程接入 agent，使用 `stdio`（默认）：

```bash
python -m mcp_server
```

服务的标准输出只承载 MCP 协议，不要把调试信息写到标准输出。供服务器同学配置时，需要提供 Python 解释器绝对路径、仓库路径与上面的启动参数。一个通用的客户端配置示意如下，具体字段以 agent 框架为准：

```json
{
  "name": "wireless-toolbox",
  "command": "/srv/wireless-toolbox/.venv/bin/python",
  "args": ["-m", "mcp_server"],
  "cwd": "/srv/wireless-toolbox"
}
```

也可作为本机 Streamable HTTP 服务运行：

```bash
python -m mcp_server --transport streamable-http --port 8765
```

MCP 端点为 `http://127.0.0.1:8765/mcp`。当前 HTTP 只绑定回环地址，适合同一台服务器上的 agent 调用；跨主机访问需要服务器团队加认证代理与网络策略。不要把这个未认证的本机端点直接暴露到公网。

默认列出全部 144 个工具。若线上 agent 的工具上下文需要更小的集合，可在启动时选择子集，例如：

```bash
python -m mcp_server --tools q_function,ber_awgn,convert_snr,nr_tbs,lte_mcs,link_capacity
```

工具仍以 `tool_registry.json` 为来源；`--tools` 只是当前服务实例的可见集合。工具名无效时，服务在启动阶段报错。

## 调用契约

客户端通过 MCP `tools/list` 获取精确的 JSON Schema，再通过 `tools/call` 调用。参数名沿用原 CLI；例如 `nr_tbs` 使用 `nre-per-prb`。数值序列仍采用现有工具的字符串格式，例如 `"0,1,2"` 或 `"[0,1,2]"`，`inputSchema` 有详细字段说明。`wlan_ldpc` 中原 schema 的 `enum` / `float` 类型在 MCP 中分别转换为标准 JSON Schema 的字符串或整数枚举 / `number`。

两个使用位置子命令的 CLI 在 MCP 中增加 `command` 参数：`nr_dci` 可选 `encode` / `scramble`，`wireless_utils` 可选 `awgn` / `biterr` / `berawgn` / `bcc-interleave` / `golay`。MCP 会检查所选子命令的必需参数，再按 CLI 要求组织位置参数。示例：

```json
{"command":"biterr","x":"0,1","y":"0,0"}
```

示例：调用 `convert_snr`，参数为：

```json
{"x":"6","input_mode":"ebno","output_mode":"snr","bits_per_symbol":2}
```

成功时返回 MCP `structuredContent`（同时提供等价 JSON 文本），例如：

```json
{"input_mode":"ebno","output_mode":"snr","values_db":9.010299956639813}
```

错误时 `isError=true`，文本内容是 `{"code":"...","message":"..."}`。参数由 JSON Schema 校验；未知字段被拒绝。每次调用最多等待 30 秒，可用 `--timeout` 调整；最多同时运行两个 CLI；单次 JSON 输出限制为 1 MB。对于原 CLI 输出的 `Infinity`、`-Infinity`、`NaN`，MCP 层将其转成同名字符串以保持合法 JSON。

## 文件输入、输出与会话状态

部分工具支持 `input_file`、`output_file`、`state_file` 等文件参数，或在 `input` JSON 中使用 `session_file`、`output_path`、`waveform_file`。MCP 将这些路径限制在服务专用数据目录；相对路径从该目录解析，越界路径会返回 `INVALID_PATH`。默认目录是系统临时目录中的 `wireless-toolbox-mcp-data`。线上建议显式配置持久目录：

```bash
python -m mcp_server --data-root /srv/wireless-toolbox-data
```

文件输入需要先由服务器侧把 JSON/NPZ 放进该目录；生成的 NPZ、PCAP 或 SQLite 会话文件也留在该目录，返回结果中的路径供服务器侧后续读取。多数工具可直接使用内联参数，无需文件。大结果可用工具本身的 `output_file` / `inline_limit` 参数控制；MCP 不直接传输生成的二进制文件。

## 交接与验收

服务器同学需要：

1. 将整个仓库复制到服务器，安装 `requirements-mcp.txt`。
2. 选择 `stdio` 子进程或本机 HTTP 接入 agent；推荐同机 `stdio`。为文件型工具设置可写的 `--data-root`。
3. 决定 agent 看见全部 144 个工具还是通过 `--tools` 只看见业务所需子集。一次向模型展示 144 个工具可能影响选工具质量，建议按业务模块启动子集服务。
4. 运行 `python -m unittest scripts.test_mcp_server -v` 验证全部 144 个 schema 示例、文件路径限制、参数拒绝和两种传输。

新增注册工具会进入 MCP 全量目录，因此需要同时检查 schema 与 CLI 参数、文件路径行为、JSON 输出及资源消耗，并补充可执行的 schema 示例。当前实现没有改动 `wirelessagent.plus` 服务；网站端接线由其运行架构决定。
