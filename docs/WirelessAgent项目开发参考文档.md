# WirelessAgent 项目开发参考文档

> 生成时间：2026-08-07 | 来源：Codex 多轮对话汇总
> 用途：给同学做项目参考，了解完整开发历程、技术决策和当前状态

---

## 一、项目总览

### 1.1 项目名称
**WirelessAgent（无线智能体）** — 面向无线通信领域的垂直 AI 助手平台

### 1.2 技术架构

| 层 | 技术栈 |
|---|---|
| 前端 | React 18 + Vite + TypeScript + Tailwind CSS + shadcn/ui |
| 后端 | Python FastAPI + SQLAlchemy 2 (async) + Alembic |
| AI 网关 | OpenClaw Gateway (npm 包，端口 18789，OpenAI 兼容 REST API) |
| AI 模型 | DeepSeek chat（通过 OpenClaw agent 调用） |
| RAG | ChromaDB + BGE-small-zh-v1.5 |
| 数据库 | SQLite（开发）/ PostgreSQL 16（生产 Docker） |
| 部署 | 阿里云 ECS (<SERVER_IP>: 2核 2G) + Cloudflare Tunnel |

### 1.3 五大功能模块

| 模块 | 说明 | 进度 |
|------|------|:---:|
| F1 习题解答 | 分步解答 + 知识点延伸 + 错题本 | MVP |
| F2 标准检索 | 3GPP/IEEE 文档 RAG 检索 | MVP |
| F3 论文速递 | arXiv 每日抓取 + 中文摘要 | M2 |
| F4 网规辅助 | 链路预算 → SINR 热图 | M3 |
| F5 报告生成 | 结构化报告导出 Word/PDF | M3 |

---

## 二、项目文件结构

```
code/
├── docker-compose.yml
├── .env / .env.example
├── README.md
├── 部署信息汇总.md
├── 快速上手.md
├── CloudflareTunnel部署方案.md
├── 阿里云ICP备案部署方案.md
├── 多用户会话隔离方案.md
├── frontend/                  # React + Vite
│   ├── src/
│   │   ├── components/chat/   # ChatInput, ChatBubble, ChatList, SessionSidebar
│   │   ├── hooks/             # useChat, useSessions
│   │   ├── lib/               # api.ts, utils.ts
│   │   └── pages/             # ChatPage, LoginPage
│   ├── dist/                  # 构建产物（已部署到服务器）
│   ├── vite.config.ts         # Vite proxy: /api → 127.0.0.1:8000
│   └── package.json
├── backend/                   # FastAPI
│   ├── app/
│   │   ├── main.py            # 入口 + 前端静态文件托管
│   │   ├── config.py          # Pydantic Settings
│   │   ├── database.py        # SQLAlchemy async engine
│   │   ├── models/            # User, Session, Message, Feedback
│   │   ├── routes/            # auth, chat(SSE), session, file, rag
│   │   ├── services/          # openclaw_client, rag_service, chroma_service
│   │   └── middleware/        # auth (JWT)
│   └── chroma_data/           # ChromaDB 向量库
└── skills/                    # OpenClaw skills 符号链接
```

---

## 三、开发历程（按时间线）

---

### 阶段 1：本地环境搭建与全链路测试 (2026-07-26)

**目标**：验证本地代码能正常运行，AI 对话全链路打通

**关键操作**：
- 检查本地环境：Node.js v24.14.1 at `D:\node.js\`，Python 3.11 at `D:\python\`，OpenClaw Gateway v2026.6.1
- 启动 OpenClaw Gateway（端口 18789，DeepSeek provider）
- 启动 FastAPI 后端（端口 8000，SQLite 数据库）
- 启动前端 Vite dev server（端口 5173）

**测试结果**：

| 组件 | 状态 | 验证 |
|------|:---:|------|
| OpenClaw REST API | ✅ | curl 返回 "你好呀..." |
| FastAPI 健康检查 | ✅ | `{"status":"ok"}` |
| SSE 流式聊天 | ✅ | `1+1=2。喵~` 逐 token 返回 |
| 用户注册/登录 | ✅ | JWT token 正确发放 |
| 前端页面 | ✅ | HTTP 200 on port 5173 |

**数据流验证**：
```
前端(Vite:5173) → proxy /api → FastAPI(8000) → OpenClaw Gateway(18789) → DeepSeek
```

---

### 阶段 2：云端排查与修复 (2026-07-26)

**问题 1：云端网站发消息无回复**

**根因**：
- Token 不匹配：`backend/.env` 的 `OPENCLAW_API_KEY` 为 `<REDACTED>`，Gateway 实际 token 为 `<REDACTED>`
- 模型问题：Gateway 默认模型 `deepseek-v4-flash`（推理模型），在 OpenAI 兼容模式下只产生 `reasoning_content`，Gateway 检测后触发 `reasoning-only retry` 导致死循环

**修复**：
```bash
# 1. 模型切换（/root/.openclaw/openclaw.json）
sed -i 's/deepseek\/deepseek-v4-flash/deepseek\/deepseek-chat/g'

# 2. Token 修正（/opt/wireless-agent/backend/.env）
OPENCLAW_API_KEY=<REDACTED>

# 3. 重启
systemctl --user restart openclaw-gateway.service
systemctl restart wireless-agent
```

---

**问题 2：SSE 格式不匹配导致前端无显示**

**根因**：云端 `chat.py` MD5 与本地不一致（`9e79...35b8` vs `902d...b114`）。云端版本直接透传 Gateway 的原始 SSE 格式 `{"choices":[{...}]}`，而前端 `useChat` hook 只认识 `{"token":"..."}` 格式

**修复**：
```powershell
scp chat.py root@<SERVER_IP>:/opt/wireless-agent/backend/app/routes/chat.py
```
```
systemctl restart wireless-agent
```

---

**问题 3：会话历史无法保存**

**根因**：
- 后端缺失 `GET /api/sessions/{session_id}/messages` API
- 前端 `ChatPage.tsx` 切换会话时只调 `clear()`，没从后端加载历史

**修复**：
- 后端 `session.py` 新增 `MessageOut` 模型 + `get_session_messages` 端点
- 前端 `api.ts` 新增 `getMessages()` 方法
- 前端 `ChatPage.tsx` 切换会话时调用 API 加载历史消息

**⚠️ 踩坑：Windows PowerShell `Set-Content -Encoding UTF8` 会加 BOM（`EF BB BF`），导致 Linux Python 语法错误。修复方式：用 `[System.IO.File]::WriteAllBytes` 去 BOM 后上传**

---

### 阶段 3：前端构建 + 静态文件托管 (2026-07-26)

**目标**：让 FastAPI 同时托管前端页面

**修改 `backend/app/main.py`**：
```python
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 前端 dist 路径（相对 main.py 的 ../.. 即项目根目录）
_FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")

if os.path.isdir(_FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_FRONTEND_DIST, "assets")))
    @app.get("/{path:path}")
    async def spa_fallback(path: str):
        if path.startswith("api/"):
            raise HTTPException(status_code=404)
        return FileResponse(os.path.join(_FRONTEND_DIST, "index.html"))
```

**构建部署**：
```bash
cd frontend && npm run build          # → dist/（540KB JS + 63KB CSS）
scp -r dist root@<SERVER_IP>:/opt/wireless-agent/frontend/dist
```

---

### 阶段 4：游客模式（不注册直接聊天）(2026-07-26 → 08-04)

**需求**：像豆包/千问一样，用户不需要注册就能聊天

**问题 1（07-26）**：`ChatPage` 检测不到 token 就 `navigate("/login")`，强制跳转登录页

**修复**：改为自动调 guest API 创建临时用户

**问题 2（08-04）**：部署后新用户点击发送无反应

**根因**：新用户 `sessions` 为空 → `activeSession=null` → `handleSend` 直接 `return`（静默吞消息）

**修复**：
- `ChatPage.tsx` 加 `useEffect`：检测到 `sessions.length===0` 时自动调用 `create()`
- `handleSend` 改为 async：无 session 时自动创建再发送
- `ChatInput` 的 `disabled` prop 从 `loading||!activeSession` 改为仅 `loading`
- 修复编码损坏的中文字符串（全改为英文）

**修改的关键文件**：

`backend/app/middleware/auth.py`：公共路径加 `/api/auth/guest`
`backend/app/routes/auth.py`：新增 `POST /api/auth/guest`，自动创建 Guest-xxxxx 临时用户
`frontend/src/lib/api.ts`：新增 `guest()` 方法
`frontend/src/pages/ChatPage.tsx`：auto-guest useEffect + auto-create session + 移除强制登录
`frontend/src/pages/LoginPage.tsx`：加「跳过登录直接使用」按钮
`frontend/src/components/chat/ChatInput.tsx`：loading prop 控制 spinner，disabled 不影响输入
`frontend/src/components/chat/SessionSidebar.tsx`：底部加 Login/Register 链接

---

### 阶段 5：多用户会话隔离方案（方案 B）(2026-08-04 → 08-05)

**核心发现**：网站通过 `openclaw/default` 模型调用时，所有用户共享同一个 Agent 实例（workspace + identity + memory），导致：
- User A 说名字 → User B 看到 A 的信息
- 每次新对话触发 BOOTSTRAP 身份初始化（"我刚上线，你是谁？我叫什么？"）
- 无法按用户追踪研究数据

**方案 B — 基于 OpenClaw `user` 字段的会话隔离**

**原理**：
- OpenAI API 标准的 `user` 字段标识终端用户
- OpenClaw 配置 `session.dmScope: per-channel-peer` 确保不同 `user` 值独立
- 网站每个对话有 UUID → 作为 `user` 值传给 Gateway

**架构**：
```
                  OpenClaw Agent (全局共享)
             ┌─────────────────────────────────┐
             │  Skills / Tools / System Prompt │
             │     （老师维护，全局生效）         │
             └──────────┬──────────────────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
       user="s-A"  user="s-B"  user="s-C"
       独立记忆     独立记忆     独立记忆
```

**需修改文件**：

| 文件 | 改动 | 行数 |
|------|------|:---:|
| `backend/app/services/openclaw_client.py` | `chat_stream()` 加 `user_id` 参数 → `payload["user"]` | ~5 行 |
| `backend/app/routes/chat.py` | 加 `WIRELESS_PROMPT` 常量 + 调用时传 `user_id=session.id` | ~15 行 |

---

### 阶段 6：方案 B 前置条件验证 (2026-08-05)

**验证 1：`user` 字段是否隔离会话**

本地测试：
- User A（`user=test-user-a`）说 "我叫张三"
- User A 再问 "我叫什么名字？" → GateWay 回答 "张三" ✅
- User B（`user=test-user-b`）问 "我叫什么名字？" → GateWay 回答 "你还没有告诉我" ✅
- **结论：隔离有效**

**验证 2：system prompt 能否抑制 BOOTSTRAP**

云端测试：
- 无 system prompt：agent 进入身份初始化流程
- 有 system prompt（`"Do not bootstrap. Answer directly."`）：直接返回答案 ✅

**验证 3：修复缺失的 DeepSeek API Key**

- 发现 systemd 服务里没有 `DEEPSEEK_API_KEY` 环境变量
- 添加：`Environment="DEEPSEEK_API_KEY=<REDACTED>"`
- 验证：`curl https://api.deepseek.com/v1/models` → 返回模型列表 ✅

**验证 4：预填 IDENTITY.md 跳过 BOOTSTRAP**

- 云端 workspace 的 `IDENTITY.md` 是空模板
- 填入 WirelessAgent 身份信息（name/vibe/emoji: 📡/expertise）
- 填入 `USER.md`（防止 "你是谁" 追问）
- 重新测试 SSE 全链路 → `"我是 WirelessAgent 📡"` ✅

---

## 四、当前服务器状态

| 组件 | 状态 | 端口 | 说明 |
|------|:---:|:---:|------|
| FastAPI 后端 (wireless-agent) | ✅ | 8000 | systemd 管理，含前端静态文件 |
| OpenClaw Gateway | ✅ | 18789 | systemd 用户服务，model: deepseek-chat |
| Cloudflare Tunnel (cloudflared) | ✅ | - | 出站连接，映射 wirelessagent.plus → :8000 |
| 前端 | ✅ | - | 已构建 dist/，FastAPI 托管 |

---

## 五、关键配置文件速查

### 5.1 服务器路径

| 文件 | 路径 |
|------|------|
| FastAPI 入口 | `/opt/wireless-agent/backend/app/main.py` |
| 聊天路由 | `/opt/wireless-agent/backend/app/routes/chat.py` |
| OpenClaw 客户端 | `/opt/wireless-agent/backend/app/services/openclaw_client.py` |
| 后端配置 | `/opt/wireless-agent/backend/app/config.py` |
| 后端 .env | `/opt/wireless-agent/backend/.env` |
| 前端构建产物 | `/opt/wireless-agent/frontend/dist/` |
| Gateway 配置 | `/root/.openclaw/openclaw.json` |
| Gateway 身份 | `/root/.openclaw/workspace/IDENTITY.md` |
| Gateway systemd | `/root/.config/systemd/user/openclaw-gateway.service` |
| 网站 systemd | `/etc/systemd/system/wireless-agent.service` |

### 5.2 认证 / Token

| 用途 | 值 |
|------|-----|
| DeepSeek API Key | `<REDACTED>`（环境变量） |
| Gateway Auth Token | `<REDACTED>` |
| SSH | `root@<SERVER_IP>` / `<REDACTED>...` |

---

## 六、常用运维命令

### 服务管理
```bash
# 网站后端
systemctl status wireless-agent
systemctl restart wireless-agent
journalctl -xeu wireless-agent.service -n 20

# OpenClaw Gateway
systemctl --user status openclaw-gateway.service
systemctl --user restart openclaw-gateway.service
```

### 快速验证
```bash
# 网站健康
curl -s http://127.0.0.1:8000/api/health

# 前端页面
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/

# AI 网关
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18789/

# 游客注册
curl -s -X POST http://127.0.0.1:8000/api/auth/guest -H "Content-Type: application/json" -d '{}'
```

---

## 七、踩坑记录 ⚠️

| 坑 | 现象 | 解决 |
|----|------|------|
| PowerShell UTF-8 BOM | Python 在 Linux 上 SyntaxError | 用 `[System.IO.File]::WriteAllBytes` 去 BOM 后 scp |
| `Set-Content -Encoding UTF8` | 文件开头加 `EF BB BF` | 同上 |
| scp 覆盖失败 | 文件时间没变 | 先 `rm -rf` 云端旧文件再传 |
| v4-flash 推理模型 | REST API 挂死 | 切 `deepseek-chat` |
| Token 不匹配 | 后端发请求被 Gateway 拒 | `.env` 对齐 Gateway 的 `token` |
| `chat.py` 被编码搞坏 | 只剩 9 行，所有路由丢失 | 从云端 curl 获取最新内容或用 .NET WriteAllBytes 复原 |
| `session.py` 中文 `"新对话"` | 上传后 `title="鏂板..."` 导致 Python 崩 | 全改成 ASCII `"New Chat"` |
| Gateway systemd 缺 API Key | Gateway 能启动但 Agent couldn't generate | systemd 加 `Environment="DEEPSEEK_API_KEY=..."` |
| `ps aux` 管道输出太慢 | `head -5` 卡住 | `systemctl status` 替代 |

---

## 八、云端的 chat.py 恢复方式

如果 `chat.py` 再被搞坏：

```bash
# 从云端 session.py 结构推断 chat.py，或从 GitHub/备份恢复
# 关键检查点：文件行数应为 ~68 行
wc -l /opt/wireless-agent/backend/app/routes/chat.py

# 语法检查
python3 -c "compile(open('/opt/wireless-agent/backend/app/routes/chat.py').read(),'test','exec')"
```

---

## 九、部署方案 B 的完整步骤（待执行）

1. 本地修改 `openclaw_client.py`：`chat_stream` 函数签名加 `user_id=None`，payload 加 `payload["user"] = user_id`
2. 本地修改 `chat.py`：加 `WIRELESS_PROMPT` 常量 + `openclaw.chat_stream(messages, user_id=session.id, system_prompt=WIRELESS_PROMPT)`
3. 构建前端：`cd frontend && npm run build`
4. 上传：
   ```powershell
   scp backend/app/services/openclaw_client.py root@<SERVER_IP>:/opt/wireless-agent/backend/app/services/
   scp backend/app/routes/chat.py root@<SERVER_IP>:/opt/wireless-agent/backend/app/routes/
   scp -r frontend/dist root@<SERVER_IP>:/opt/wireless-agent/frontend/
   ```
5. SSH 重启：`systemctl restart wireless-agent`
6. 隐身窗口验证：进入聊天页 → 发消息 → 身份正确 + 无 BOOTSTRAP + 两窗口互不干扰

---

## 十、部署后的待办事项

| 优先级 | 事项 | 说明 |
|:---:|------|------|
| P0 | 隐身窗口双开测试 | 验证隔离有效 + 无 BOOTSTRAP |
| P1 | 禁用文件写入工具 | `openclaw.json` → `denyCommands` |
| P1 | 对话历史优化 | `chat.py` 只发最新一条消息 |
| P1 | 更新部署信息汇总 | 记录 API Key 变更 + 方案 B 部署 |
| P2 | 数据收集模块 | 新增 analytics 表 |
| P2 | 系统提示词外置 | WIRELESS_PROMPT → `.env` |
| P2 | 限流 | slowapi，每 IP 每秒 1 条 |
| P3 | Gateway session 清理 | 自动过期机制 |
| P3 | 老师后台 | 在线改提示词、查看数据 |

---

**欢迎继续补充。遇到任何问题，参考本文档的踩坑记录和运维命令。**