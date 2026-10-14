# 前端鉴权与数据接口契约（Issue #11）

> 前端实现：`_build/_auth_store.js`（部署为 `/assets/auth-store.js`）、登录页 `_build/_auth_login.js`、文档库 `_build/_docs_panel.js`。
> API 前缀：`/api`（可用 `window.WAGENT_API_BASE` 覆盖）。
> 说明：带 ✅ 的接口是现有生产后端已实现的；带 ➕ 的是本次前端新增依赖、**需要 services/api 同学确认或补齐**的接口。
> 按 CONTRIBUTING「公共契约需协商」的约定，本文先放在 `apps/web/docs/` 作为前端期望记录；与后端确认后可移入 `contracts/`。

## 一、鉴权

| 接口 | 请求体 | 成功响应 | 前端行为 |
|---|---|---|---|
| ✅ `POST /api/auth/register` | `{ email, password, display_name }` | `{ access_token, user_id, display_name }` | 注册成功即登录，token 落 localStorage 并跳转 `redirect` |
| ✅ `POST /api/auth/login` | `{ email, password }` | `{ access_token, user_id, display_name }` | 登录成功同上 |
| ✅ `POST /api/auth/guest` | `{}` | `{ access_token, user_id, display_name }` | 「跳过登录，以游客身份使用」；进入聊天页时若未登录也会自动调用 |
| ➕ `POST /api/auth/logout` | `{}` | 任意 2xx | 侧边栏「退出登录」先调用（失败也继续），随后清除本地登录态与缓存 |

**登录态存储**：`Authorization: Bearer <access_token>`；token 存 `localStorage["wagent.token"]`，用户信息存 `localStorage["wagent.user"]`
（同时镜像旧的 `token` / `user` 键，兼容尚未刷新的旧标签页）。

## 二、会话与聊天记录

| 接口 | 说明 | 前端行为 |
|---|---|---|
| ✅ `GET /api/sessions/` | 会话列表（`[{ id, title, updated_at }]`） | 侧边栏列表；结果缓存到 `wagent.sessions`，刷新页面先渲染缓存再覆盖 |
| ✅ `POST /api/sessions/` | 新建会话 | 「New Chat」；首次进入且无历史会话时自动创建 |
| ✅ `DELETE /api/sessions/{id}` | 删除会话 | 同时清理该会话的本地聊天记录缓存 |
| ✅ `GET /api/sessions/{id}/messages` | 会话消息（`[{ id, role, content }]`） | 切换/刷新会话时拉取；写入 `wagent.messages.<sessionId>`（每会话最多 50 条） |
| ✅ `POST /api/chat/stream` | SSE 流式对话 | 401 时自动登出并跳转登录页 |

**会话隔离**：前端按 `sessionId` 分桶缓存；真正的数据隔离由后端按 token 校验，需后端联调验证（见 Issue #11 验收项 3）。

## 三、工作文档

| 接口 | 说明 | 前端行为 |
|---|---|---|
| ✅ `POST /api/files/upload` | `multipart/form-data`，字段名 `file` | 「文件上传」页；成功后把 `{ id, name, size }` 记入本地文档索引，避免刷新后记录丢失 |
| ➕ `GET /api/files/` | 文档列表，兼容 `[...]` 或 `{ files: [...] }` | 「文档库」列表；返回 404 时退回本地记录并提示「后端 /api/files 尚未提供（404）」 |
| ➕ `GET /api/files/{id}/content` | 文档内容（文本/JSON 均可） | 「查看」弹层；非 2xx 时提示「查看失败（HTTP xxx）」并保留列表 |

## 四、知识检索

| 接口 | 说明 |
|---|---|
| ✅ `GET /api/rag/search?q=&top_k=` | 标准检索页；`/rag/search` 返回 500 是知识库未索引的既有问题，不在本 Issue 范围 |

## 五、错误码 → 页面提示（登录 / 注册）

| HTTP | 前端提示 |
|---|---|
| 401 | 邮箱或密码错误，请检查后重试 |
| 403（注册） | 该邮箱已被注册，请直接登录 |
| 403（登录） | 账号已被禁用，请联系管理员 |
| 409 | 该邮箱已被注册，请直接登录 |
| 400 / 422 | 输入有误：<后端 detail> |
| 404 | 认证接口不存在（404），请与后端同学确认 /api/auth 契约 |
| 429 | 尝试过于频繁，请稍后再登录 |
| 5xx | 服务异常（状态码），请稍后重试 |
| 网络异常 | 无法连接服务器，请检查网络或后端服务是否已启动 |

## 六、401 统一处理（自动登出）

`/api` 下**非 `/auth/*`** 的任意请求返回 401 时：清除 token / 用户信息 / 本地聊天记录与文档索引，并跳转
`/login?redirect=<当前路径>&reason=expired`；登录页据此显示「登录状态已过期，请重新登录」，登录成功后回到来源页面。
已在 `/login` 页面时不再跳转，避免死循环。

## 七、localStorage 键位

| Key | 内容 |
|---|---|
| `wagent.token` / `wagent.user` | 登录态（另有旧的 `token` / `user` 兼容键） |
| `wagent.last_session` | 上次打开的会话 ID，刷新后自动恢复 |
| `wagent.sessions` | 会话列表缓存 |
| `wagent.messages.<sessionId>` | 每个会话最近 50 条消息缓存 |
| `wagent.docs` | 工作文档索引（后端列表未就绪时的兜底记录） |