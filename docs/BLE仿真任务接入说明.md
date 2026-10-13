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

访问 `http://127.0.0.1:8000/simulations/ble-coverage`。页面提交后将任务 ID 保存在 URL 中，刷新可恢复状态。默认持久数据目录为 `.runtime`；可用 `WIRELESS_SIM_DATA_ROOT` 改为专用目录。API 和 worker 必须使用同一个目录。本地 API 仅监听回环地址。

## 任务 API

`POST /api/v1/simulation-tasks` 返回 `202`、任务 ID 和查询链接。默认请求：

```json
{"type":"ble_power_distance_v1","parameters":{"tx_power_dbm":0,"receiver_sensitivity_dbm":-75,"distances_m":[1,5,10,25,50,100],"packets_per_distance":20}}
```

`GET /api/v1/simulation-tasks/{id}` 返回持久状态 `queued/running/succeeded/failed`、进度、结果或错误。`GET /api/v1/simulation-tasks/{id}/events?after_sequence=0&limit=100` 分页返回工具调用、包事件与进度。`/healthz` 检查 API；`/readyz` 还要求 worker 最近 15 秒有心跳。OpenAPI 契约在 `/openapi.json`。

范围约束：发射功率 −20～20 dBm、灵敏度 −110～−70 dBm、2～20 个严格递增的 1～1000 米距离、每点 1～100 包。每点独立 SQLite 会话和完整事件轨迹保存在任务数据目录。worker 重启时将原 `running` 任务重新入队，并用新的 attempt 目录执行；已有文件不被覆盖。

## 预发部署

在支持 Docker Compose 的预发机上，从 `.team-contribution` 根目录执行：

```bash
docker compose -f infra/compose.simulation.yaml up --build -d
```

API 只发布到主机 `127.0.0.1:8000`。若要让其他人访问，由预发环境现有认证反向代理转发该地址；不要直接公开未认证的任务 API。`simulation_data` 卷保存任务、事件和工具会话。用 `docker compose -f infra/compose.simulation.yaml ps` 检查两项服务为 healthy；然后提交默认任务，等待 `succeeded`，检查六个距离点、验证结果和事件记录。

## 验收

```bash
python -m unittest discover -s tests -p 'test_simulation*.py' -v
python packages/wireless_tools/scripts/validate_bluetooth_session.py
python packages/wireless_tools/scripts/validate_bluetooth_path_loss.py
```

工具调用须通过 MCP；worker 启动时只公开 `bluetooth_path_loss,bluetooth_session`。MCP 把每项任务的会话文件限制在独立数据目录，并为单次工具调用设置 30 秒超时。API/页面不读取其他目录的文件。
