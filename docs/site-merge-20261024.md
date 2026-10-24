# 服务器网站代码与 GitHub 仓库对齐记录

来源：本地 `wireless-agent-github-ready-20261021-210621(1)`；对照仓库 `main` 的 `34e9227`（2026-10-24）。本分支只做本地改动，未部署、未推送。

## 现有部署映射

`infra/deploy.sh` 已将 `services/api/app` 发布到服务器的 `backend/app`，并将 `apps/web` 的静态文件发布到 `frontend/dist`。因此不能把 GitHub-ready 包整体复制到仓库顶层，也不能覆盖现有的 BLE 任务 API/worker。

对照时，GitHub-ready 的 `backend/app` 与仓库 `services/api/app` 有 27 个文件哈希相同、10 个不同；其中 `limiter.py`、`models/analytics.py`、`routes/analytics.py` 只是换行格式不同。其余差异主要是仓库新增的资料库模型、访客标记、聊天附件/模式、流式上传和文件预览能力。此次保留这些较新的仓库实现，只选取安全性和本地启动所需的改动。

## 本分支改动

- `services/api/app/main.py`：外部 arXiv digest 未安装时不注册 `/api/digest`，避免网站 API 启动时直接 `ModuleNotFoundError`；安装后保留原路由。
- `services/api/app/routes/papers.py`：没有外部抓取脚本时，刷新接口返回 503，而非内部异常 500；已有论文查询不受影响。
- `services/api/app/config.py`：`SECRET_KEY`、`DATABASE_URL`、`OPENCLAW_API_KEY` 必须从环境配置，不再使用不安全的默认值。
- `services/api/.env.example`：只包含示例占位符；真实 `.env` 不可提交。

## 本地验证

在独立环境安装 `services/api/requirements-app.txt`（以及测试依赖）。从 `services/api` 作为工作目录运行网站 API；该目录的私有 `.env` 至少包含上述三个必填项。健康检查是 `GET /api/health`。不接入真实 Gateway 时，聊天接口无法完成真实回复，但健康检查、导入和数据库测试可进行。不要使用生产密钥或生产数据库测试。

在当前 Windows 沙箱中，测试的临时文件型 SQLite 数据库不可写；测试配置支持用 `TEST_DATABASE_URL=sqlite+aiosqlite:///:memory:` 覆盖。以此运行 `services/api/tests` 得到 **10 passed**；网站 API 使用本地占位配置启动后 `/api/health` 返回 200。`git diff --check` 与网站代码语法检查通过。

仓库原有 BLE 入口 `services/api/app.py` 与网站包目录 `services/api/app/` 同名，导致 Python 导入时选择包目录，BLE 测试无法取得 `create_app`。本分支将 BLE 入口改名为 `services/api/simulation_app.py`，并同步更新测试、uvicorn 启动脚本和 compose 启动命令。该命名冲突修复后，仍需运行 BLE unittest 和网站 API tests。

## 暂不自动合并的部分

- `apps/web` 与服务器包的 `frontend` 构建产物不是同一版本，服务器包也没有 `src/` 或 `package.json`。需网页组提供可重建的前端源码，确认以哪个版本为准，再重新构建；不可直接覆盖现有静态资源。
- `services/worker` 已有 BLE 与网站任务实现；不能用服务器包较旧的 `backend/worker` 覆盖。
- 其余有实质差异的 `backend/app` 文件里有 GitHub 后续功能修改，不能批量覆盖。逐项功能合并必须由相应模块负责人验收。
- `arxiv-wireless-digest`、知识库、MCP、MATLAB 与 SkillOpt 是独立组件，不在此网站包中；外部项目安装、路径和权限需另行确认。
- 仓库许可证尚未确定；公开上传服务器包或前端构建产物前，需团队确认代码与素材的发布权限。

此分支不更改线上部署脚本、不访问生产 Gateway、不复制任何真实 `.env`、数据库或上传文件。
