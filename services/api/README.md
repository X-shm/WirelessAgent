# services/api — WirelessAgent 后端

FastAPI + SQLAlchemy（async）实现的服务端数据存储：注册/登录/会话/聊天记录/文档/任务。
对应 Issue #15「服务端数据存储：PostgreSQL + 注册/登录/会话/文档 API」。

## 技术栈
- FastAPI + Uvicorn
- SQLAlchemy 2（async）
- 开发库：SQLite（零配置，秒跑）；生产库：PostgreSQL 16（Docker 部署）
- 密码：PBKDF2-HMAC-SHA256（标准库，无第三方依赖）
- token：HMAC-SHA256 签名（标准库），7 天有效

## 目录结构
```
services/api/
├── app/
│   ├── main.py          # 应用入口 + 建表
│   ├── config.py        # 环境变量配置
│   ├── database.py      # 异步引擎 / 会话
│   ├── models.py        # users/sessions/messages/files/tasks 表
│   ├── schemas.py       # Pydantic 模型
│   ├── security.py      # 密码哈希 + token
│   ├── deps.py          # 当前用户依赖（Bearer token）
│   └── routers/
│       ├── auth.py      # 注册/登录/游客/登出
│       ├── users.py     # /users/me
│       ├── sessions.py  # 会话 + 消息
│       ├── files.py     # 文档上传/列表/内容
│       ├── tasks.py     # 任务增删改查
│       └── chat.py      # 流式对话（SSE）
├── tests/test_api.py    # pytest 接口测试
├── docs/api.md          # 接口文档（数据存储接口记录）
└── requirements.txt / requirements-dev.txt
```

## 快速开始（开发，SQLite）
```powershell
cd services/api
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```
启动后访问：http://127.0.0.1:8000/api/health → `{"ok":true}`

## 生产（PostgreSQL）
```powershell
$env:DATABASE_URL="postgresql+asyncpg://user:password@host:5432/wirelessagent"
$env:SECRET_KEY="换成随机长字符串"
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
> 用 PostgreSQL 前需先安装驱动：`pip install asyncpg`

## 测试
```powershell
.venv\Scripts\python -m pytest tests/test_api.py -q
```

## 接口文档
见 [docs/api.md](docs/api.md)。