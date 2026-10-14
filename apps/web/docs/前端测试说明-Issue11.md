# 前端测试说明（Issue #11 登录界面与数据存储）

## 一、怎么运行

两条命令都不需要安装依赖（用系统 / 运行时自带的 node），浏览器测试需要本机 Chrome。

```powershell
cd apps/web

# 1) 登录态与存储层单测（node:test，16 条）
node --test tests/auth_storage.test.mjs

# 2) 端到端冒烟测试（无头 Chrome + CDP，15 项断言，并输出截图）
$env:CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
node tests/smoke_test.mjs . .
```

冒烟测试会临时启动静态服务器（随机端口）与无头 Chrome，把 `/login`、`/work` 页面真实渲染出来，
用桩函数替换 `window.fetch` 后断言页面文本、computed style 与 localStorage 状态，因此不依赖后端即可回归。

## 二、测试覆盖 → 验收标准对照

| Issue #11 验收标准 | 覆盖用例 |
|---|---|
| 登录 / 注册页面可正常使用，错误密码有明确提示 | 单测：`validateForm`、`authErrorMessage` 全分支；冒烟：空表单校验提示、401 提示「邮箱或密码错误，请检查后重试」、成功登录后跳转 |
| 登录后 token 正确存储并自动附带；401 自动登出 | 单测：`setSession` / `getToken` / 请求头断言 / 401 清 token + 跳转（含「已在 /login 不重复跳转」）；冒烟：真实浏览器中 localStorage 落库、`Authorization: Bearer`、401 后跳 `/login?redirect=%2Fwork&reason=expired` |
| 聊天记录可正常展示与刷新 | 单测：`saveMessages` / `loadMessages`（上限 50 条、会话隔离、清空）；冒烟：刷新会话时先读缓存再覆盖（代码路径由 `tests` 与人工回归覆盖） |
| 工作文档可上传 / 查看，数据不丢失 | 单测：`saveDocs` / `mergeDocs` / `removeDoc`；冒烟：文档库列出后端文档、查看弹层显示正文、上传成功后本地索引保留 |
| 与后端接口契约对齐，附前端测试说明 | `docs/auth-storage-api.md`（接口 / 错误码 / 存储键）+ 本文 |

## 三、执行结果（2026-10-14，本地）

```
node --test tests/auth_storage.test.mjs   → tests 16 / pass 16 / fail 0
node tests/smoke_test.mjs . .             → 通过 15/15
```

冒烟测试输出摘要：

```
[1] 登录页渲染            ✔ 登录表单 / 游客入口 / 主题样式（输入框圆角 20px、字段间距 14px）
[2] 表单校验              ✔ 空表单提示「请输入邮箱」；错误提示色 rgb(248,113,113)
[3] 后端 401              ✔ 提示「邮箱或密码错误，请检查后重试」；请求体 { email, password }
[4] 登录成功              ✔ token 写入 localStorage 并跳转首页
[5] 401 自动登出          ✔ 清除 token → /login?redirect=%2Fwork&reason=expired
[6] 文档库                ✔ 侧边栏显示用户与退出入口；列表请求带 Bearer token；查看弹层显示正文
[7] 运行期报错            ✔ 无 JS 报错
```

### 截图

| 文件 | 说明 |
|---|---|
| `screenshots/login-wrong-password.png` | 输入错误密码后，登录页展示「邮箱或密码错误，请检查后重试」 |
| `screenshots/work-docs.png` | 工作模式「文档库」：已登录侧边栏（用户名 + 退出登录）与文档列表 |

> 截图由 `tests/smoke_test.mjs` 自动生成，可在本地重跑复现。

## 四、未覆盖 / 待后端联调

1. 会话与聊天记录的**服务端隔离**需要后端配合验证（前端仅保证按会话分桶、401 自动登出）。
2. `GET /api/files/`、`GET /api/files/{id}/content`、`POST /auth/logout` 后端未实现，当前走降级分支（提示 + 本地记录）。
3. 未做真实 SSE 流式对话的端到端测试（既有能力，本次未改动其逻辑）。