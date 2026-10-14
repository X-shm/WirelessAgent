# 数据存储接口文档（Issue #15）

> 统一前缀 `/api`，鉴权方式 `Authorization: Bearer <token>`（`/auth/*` 除外）。
> 除鉴权接口外，所有接口都**按当前登录用户隔离**：只能访问自己的会话/文档/任务。

## 一、鉴权

| 方法 | 路径 | 入参 | 成功返回 |
|---|---|---|---|
| POST | /auth/register | `{ email, password(≥6), display_name? }` | `{ access_token, user_id, display_name }` |
| POST | /auth/login | `{ email, password }` | 同上 |
| POST | /auth/guest | `{}` | 同上（游客账号） |
| POST | /auth/logout | `{}` | `{ ok: true }` |

错误：401 邮箱或密码错误；409 邮箱已注册；422 邮箱格式不对。

## 二、用户（每个用户的数据存储入口）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /users/me | 当前用户信息 `{ id, email, display_name, is_guest }` |

## 三、会话与聊天记录（按用户隔离）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /sessions/ | 当前用户的会话列表 |
| POST | /sessions/ | 新建会话 `{ title? }` → 返回会话对象 |
| DELETE | /sessions/{id} | 删除会话（校验归属，非本人 404） |
| GET | /sessions/{id}/messages | 会话消息 `[{ id, role, content }]` |
| POST | /chat/stream | `{ session_id, message }`，SSE 返回，并落库 user/assistant 两条消息 |

## 四、文档（按用户隔离）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /files/upload | `multipart`，字段 `file` → `{ id, filename, size, created_at }` |
| GET | /files/ | 当前用户文档列表 |
| GET | /files/{id}/content | 文档内容（校验归属，非本人 404） |

## 五、任务（每个任务的数据存储接口）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /tasks/ | 当前用户任务列表 |
| POST | /tasks/ | 创建任务 `{ type, params, status? }` |
| GET | /tasks/{id} | 任务详情 / 结果 |
| PATCH | /tasks/{id} | 更新 `{ status?, result?, params? }` |
| DELETE | /tasks/{id} | 删除任务（校验归属） |

## 六、数据表结构

| 表 | 字段 |
|---|---|
| users | id, email(唯一), password_hash, display_name, is_guest, created_at |
| sessions | id, user_id(外键), title, created_at, updated_at |
| messages | id, session_id(外键), role(user/assistant), content, created_at |
| files | id, user_id(外键), filename, size, content_type, content, created_at |
| tasks | id, user_id(外键), type, params(JSON), status, result(JSON), created_at, updated_at |

## 七、安全说明
- 密码用 PBKDF2-HMAC-SHA256（12 万次迭代）加盐哈希，不存明文。
- token 用 HMAC-SHA256 签名，含过期时间（默认 7 天），密钥通过环境变量 `SECRET_KEY` 配置。
- 所有数据查询都带 `user_id` 过滤，保证用户之间数据隔离。
- 文件内容开发期直接入库（BLOB），生产建议换对象存储（MinIO / 阿里云 OSS）。