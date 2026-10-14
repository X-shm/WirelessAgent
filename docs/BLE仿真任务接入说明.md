# BLE 功率与距离扫描：本地及预发联调

此任务调用 `packages/wireless_tools` 的 `bluetooth_path_loss` 和 `bluetooth_session`。Agent 是固定工具编排器；结果来自 Industrial、指数 2、零阴影衰落、静止 LE 节点与灵敏度门限模型。它不输出真实信道统计 PER，也不代表完整 BLE 协议仿真。

## 本地启动

在 `.team-contribution` 根目录使用 Python 3.11 或更新版本：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-simulation.txt
.venv\Scripts\python.exe -m services.worker
```

在另一个终端启动 API：

```powershell
.venv\Scripts\python.exe -m services.api
```

也可先运行一次真实 HTTP API + 独立 worker 进程的本地烟测，并把输入、结果和完整分页事件写入 Git 忽略的 `.runtime`：

```powershell
.venv\Scripts\python.exe scripts/smoke_ble_task_http.py --output .runtime/ble-local-smoke.json
```

访问 `http://127.0.0.1:8000/simulations/ble-coverage`。页面提交后将任务 ID 保存在 URL 中，刷新可恢复状态。默认持久数据目录为 `.runtime`；可用 `WIRELESS_SIM_DATA_ROOT` 改为专用目录。API 和 worker 必须使用同一个目录。本地 API 仅监听回环地址。

## 任务 API

`POST /api/v1/simulation-tasks` 返回 `202`、任务 ID 和查询链接。默认请求：

```json
{"type":"ble_power_distance_v1","parameters":{"tx_power_dbm":0,"receiver_sensitivity_dbm":-75,"distances_m":[1,5,10,25,50,100],"packets_per_distance":20}}
```

`GET /api/v1/simulation-tasks/{id}` 返回持久状态 `queued/running/succeeded/failed`、进度、结果或错误。`GET /api/v1/simulation-tasks/{id}/events?after_sequence=0&limit=100` 分页返回工具调用、包事件与进度。`/healthz` 检查 API；`/readyz` 还要求 worker 最近 15 秒有心跳。OpenAPI 契约在 `/openapi.json`。

成功结果中的 `code_commit_sha` 是部署时注入的 40 位 Git 提交 SHA，`registry_sha256` 是工具注册表文件的 SHA-256。直接在本机启动且未设置 `WIRELESS_SIM_COMMIT_SHA` 时，前者为 `null`；预发部署必须设置该变量并把两个值记录在验收证据中。

范围约束：发射功率 −20～20 dBm、灵敏度 −110～−70 dBm、2～20 个严格递增的 1～1000 米距离、每点 1～100 包。每点独立 SQLite 会话和完整事件轨迹保存在任务数据目录。worker 重启时将原 `running` 任务重新入队，并用新的 attempt 目录执行；已有文件不被覆盖。

## 预发部署

预发机的 SSH 入口、部署目录及认证代理负责人尚待团队确认。在确认前只进行本地联调，不执行远程部署。部署时从已合入 `main` 的确定提交检出代码，在 `.team-contribution` 根目录设置该提交的 SHA 后执行（示例为 Bash）：

```bash
export WIRELESS_SIM_COMMIT_SHA="$(git rev-parse HEAD)"
test "${#WIRELESS_SIM_COMMIT_SHA}" -eq 40
docker compose -f infra/compose.simulation.yaml config --quiet
docker compose -f infra/compose.simulation.yaml up --build -d
```

API 只发布到主机 `127.0.0.1:8000`。若要让其他人访问，由预发环境现有认证反向代理转发该地址；不要直接公开未认证的任务 API。代理须同时覆盖页面 `/simulations/ble-coverage` 和同源的 `/api/v1/simulation-tasks`，并阻止绕过认证访问。`simulation_data` 卷保存任务、事件和工具会话；不得提交 Git。用 `docker compose -f infra/compose.simulation.yaml ps` 检查两项服务为 healthy；然后提交默认任务，等待 `succeeded`，检查六个距离点、验证结果和事件记录。

部署前需由团队明确以下配置；任何一项未知时不启动公网入口：

| 待确认项 | 所需信息 |
| --- | --- |
| 服务器入口 | SSH 主机、登录用户、授权方式、运维联系人；不要在 Issue 中贴密码或令牌 |
| 代码与构建 | 部署目录、`main` 上确定的 40 位提交 SHA、Docker/Compose 版本与镜像构建权限 |
| 网络与认证 | 预发域名、TLS、现有认证代理负责人和配置位置、同源页面/API 路由、8000 端口回环与防火墙限制 |
| 数据与恢复 | `simulation_data` 卷的位置、容量、备份/保留策略、失败回滚负责人 |
| 验收责任 | 非作者代码评审人、网站/后端接口评审人、部署执行人和验收记录 Issue |

镜像启动后在预发机运行 `docker compose -f infra/compose.simulation.yaml exec worker python packages/wireless_tools/scripts/verify_ble_simulation_mcp.py`，实际核对 `tools/list` 仅返回两个指定工具，且两个 `tools/call` 均成功。禁止只凭仓库中的注册表推断预发实例已提供工具。容器基于 Python 3.11；若选择主机 Python 运行，则主机须为 3.11+ 且安装 `requirements-simulation.txt`。

预发验收须保存部署提交 SHA、镜像修订标签、注册表哈希、CI 链接、任务 ID、完整输入/结果 JSON、分页事件、页面刷新恢复和失败/非法参数/未知任务/worker 重启的证据；另建部署验收 Issue 跟踪结果。原始 SQLite 文件留在持久卷。未取得真实服务器入口、CI 结果和非作者评审前，不宣称预发验收完成，也不合并或部署。

## 验收

```bash
python -m unittest discover -s tests -p 'test_simulation*.py' -v
python packages/wireless_tools/scripts/validate_bluetooth_session.py
python packages/wireless_tools/scripts/validate_bluetooth_path_loss.py
python packages/wireless_tools/scripts/verify_ble_simulation_mcp.py
```

工具调用须通过 MCP；worker 启动时只公开 `bluetooth_path_loss,bluetooth_session`。MCP 把每项任务的会话文件限制在独立数据目录，并为单次工具调用设置 30 秒超时。API/页面不读取其他目录的文件。
