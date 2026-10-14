/**
 * 可读副本生成器（Issue #11）
 * ------------------------------------------------------------------
 * 背景：apps/web 的 React 源已丢失，团队按「反美化后的构建产物」增量开发。
 * 本脚本从 _build/index.js 抽取本次改动的组件，生成/刷新可读副本，供 PR 评审阅读：
 *   _auth_login.js       登录 / 注册页      ← index.js 的 hx()
 *   _docs_panel.js       工作模式文档库      ← index.js 的 WkDocsView()
 *   _Ww_new.js           侧边栏             ← index.js 的 Dh()
 *   _work_components.js  工作模式页面组件    ← 追加 WkDocsView 可读副本
 * 用法：node _build/_extract_readable.mjs
 * 注意：真正生效的代码只有 _build/index.js（经 esbuild 压缩为 assets/index-*.js）。
 */
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dir = path.dirname(fileURLToPath(import.meta.url));
const bundle = readFileSync(path.join(dir, "index.js"), "utf8");

function slice(a, b) {
  const i = bundle.indexOf(a);
  const j = bundle.indexOf(b, i);
  if (i < 0 || j < 0) throw new Error("定位失败: " + a);
  return bundle.slice(i, j).trimEnd();
}

// 图标别名映射；短标识符加负向断言，避免误伤 px-3 / px-4 这类 class 前缀
const ICONS = [[/\bSh\b(?![-\w])/g, "WkSearch"], [/\bNh\b(?![-\w])/g, "WkUpload"], [/\bEc\b(?![-\w])/g, "nw"], [/\bAo\b(?![-\w])/g, "xl"],
  [/\b_h\b(?![-\w])/g, "rw"], [/\bcx\b(?![-\w])/g, "ow"], [/\bdx\b(?![-\w])/g, "aw"], [/\bGx\b(?![-\w])/g, "jw"], [/\bpx\b(?![-\w])/g, "WkBriefcase"],
  [/\bWkFileTextIcon\b/g, "WkFileText"], [/\bWkRefreshIcon\b/g, "WkRefresh"], [/\bWkLogOutIcon\b/g, "WkLogOut"], [/\bWkEyeIcon\b/g, "WkEye"], [/\bfx\b(?![-\w])/g, "WkClose"]];

/** bundle 内部别名 → 可读别名（与 _Ww_new.js / _work_components.js 的既有约定一致） */
function readable(code) {
  let out = code
    .replace(/\bw\.jsxs?/g, (m) => m.replace("w.", "T."))
    .replace(/\bR\.use([A-Za-z]+)/g, (m) => m.replace("R.", "D."))
    .replace(/\bvt\(/g, "Or(")
    .replace(/\bMt\./g, "Yt.")
    .replace(/\bVa\(\)/g, "tc()");
  for (const [re, name] of ICONS) out = out.replace(re, name);
  return out;
}

const HEADER = (title, origin, note) => `/* ---------------------------------------------------------------------------
 * ${title}（可读副本）—— 由 _build/_extract_readable.mjs 生成，真正生效的代码在 ${origin}。
 * ${note}
 * 别名对照：w→T（jsx 运行时）、R→D（React）、vt→Or（className 合并）、Mt→Yt（API client）、
 *           Va→tc（useNavigate）、WkAuth（_build/_auth_store.js 注入的全局对象）。
 * --------------------------------------------------------------------------- */

`;

writeFileSync(path.join(dir, "_auth_login.js"),
  HEADER("登录 / 注册页", "_build/index.js 的 hx()", "Issue #11：表单校验、错误码提示、游客账号、登录后跳回来源页。") +
  readable(slice("function hx(){", 'function Ch(e){var t,n,r="";')) + "\n", "utf8");

writeFileSync(path.join(dir, "_docs_panel.js"),
  HEADER("工作模式 · 文档库", "_build/index.js 的 WkDocsView()", "Issue #11：文档列表 / 刷新 / 查看，后端接口未就绪时退回本地记录。") +
  readable(slice("function WkDocsView(){", "function IT(){")) + "\n", "utf8");

writeFileSync(path.join(dir, "_Ww_new.js"),
  HEADER("侧边栏（对话 / 工作 模式切换）", "_build/index.js 的 Dh()", "Issue #11：底部登录态（用户名 + 退出登录）、会话刷新按钮、新增「文档库」入口。") +
  readable(slice("function Dh(", "function Qx(")) + "\n", "utf8");

const wcPath = path.join(dir, "_work_components.js");
const wc = readFileSync(wcPath, "utf8");
const marker = "/* ---------------------------------------------------------------------------\n * 工作模式 · 文档库";
const base = wc.includes(marker) ? wc.slice(0, wc.indexOf(marker)) : wc;
writeFileSync(wcPath, base.trimEnd() + "\n\n" +
  HEADER("工作模式 · 文档库", "_build/index.js 的 WkDocsView()", "Issue #11：文档列表 / 刷新 / 查看；其余组件为既有可读副本。") +
  readable(slice("function WkDocsView(){", "function IT(){")) + "\n", "utf8");

console.log("可读副本已刷新：_auth_login.js / _docs_panel.js / _Ww_new.js / _work_components.js");