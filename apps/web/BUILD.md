# apps/web 前端构建与部署说明

> 现状：本目录的 React 源文件已丢失（见 `docs/PPT纲要-前端改版与服务异常复盘.txt`：「React 源码已丢失，基于反美化后的构建产物增量开发」）。
> 因此应用代码直接维护在「反美化后的构建产物」`_build/index.js` 中；`_build/` 下的 `_*.js` 是脚本生成的可读副本，**不参与构建**。

## 一、目录与文件职责

| 路径 | 职责 |
|---|---|
| `index.html` | 页面入口。**先加载 `/assets/auth-store.js`，再加载 bundle**（bundle 依赖全局 `WkAuth`） |
| `_build/index.js` | 唯一生效的前端代码（React 运行时、React Router、lucide 图标已内联，无外部 import） |
| `_build/_auth_store.js` | 登录态与数据存储层源码；浏览器（部署为 `/assets/auth-store.js`）与 Node 单测共用同一份文件 |
| `_build/_auth_login.js`、`_build/_docs_panel.js`、`_build/_Ww_new.js`、`_build/_work_components.js` | 由 `_extract_readable.mjs` 生成的可读副本，仅供阅读与评审 |
| `_build/_extract_readable.mjs` | 可读副本生成脚本：`node _build/_extract_readable.mjs` |
| `assets/index-<hash>.js` | 上线 bundle（esbuild 压缩产物） |
| `assets/auth-store.js` | `_build/_auth_store.js` 的部署副本 |
| `assets/index-CqKFswva.css` | 历史 Tailwind 产物（源已丢失，请勿手改） |
| `assets/utilities-patch.css` | 补齐上述产物缺失的工具类（Issue #11 引入；恢复 Tailwind 构建链后可删除） |
| `tests/auth_storage.test.mjs` | 登录态 / 存储层单测（`node --test`，无第三方依赖） |
| `tests/smoke_test.mjs` | 无头 Chrome 端到端冒烟测试（CDP 驱动真实浏览器） |
| `docs/` | 接口契约与测试说明 |

## 二、构建（esbuild）

仓库不引入 `node_modules`，esbuild 单文件二进制即可（示例：从 npm registry 取 `@esbuild/win32-x64` 解压得到 `esbuild.exe`）。

```powershell
# 1) 压缩 bundle：index.html 里引用的文件名必须与新产物一致
esbuild _build/index.js --minify --format=esm --target=es2020 --legal-comments=inline `
        --outdir=assets --entry-names=index-[hash]

# 2) 同步存储层部署副本
Copy-Item _build/_auth_store.js assets/auth-store.js -Force

# 3) 刷新可读副本（改了 index.js 里的 hx() / WkDocsView() / Dh() 之后）
node _build/_extract_readable.mjs

# 4) 校验：单测 + 冒烟测试
node --test tests/auth_storage.test.mjs
$env:CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
node tests/smoke_test.mjs . .
```

## 三、部署

沿用既有流程：**esbuild 压缩 → SFTP 上传 `assets/` → 重启服务**。
本次改动涉及 3 类静态文件，请一起上传：

1. `assets/index-<新 hash>.js`（新增，旧 bundle 已在仓库中删除，线上可保留旧文件不影响）
2. `assets/auth-store.js`（新增）
3. `assets/utilities-patch.css`（新增）与 `index.html`（新增两处引用、更新 bundle 名）

## 四、已知问题与后续建议

1. `assets/index-CqKFswva.css` 与 JS 代码不同步：实测 268 个 `className` 中有 90 余个在 CSS 中不存在（如 `p-6`、`justify-between`、`animate-spin`、`space-y-3`），这是源码丢失后无法重建 Tailwind 导致的既有问题。本次只补齐 Issue #11 触及区域所需的 37 个类（`assets/utilities-patch.css`），未触碰其他页面；**建议后续任务专门恢复 Tailwind 源与构建链**。
2. 后端 `GET /api/files`、`GET /api/files/{id}/content`、`POST /auth/logout` 尚未实现，前端已做降级处理，契约见 `docs/auth-storage-api.md`。
3. `apps/web` 无 package.json / CI：目前测试由 `node --test` 与无头浏览器脚本手工执行，后续可迁入 GitHub Actions。