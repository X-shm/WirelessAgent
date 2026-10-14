/**
 * Issue #11 前端冒烟测试：用无头 Chrome + CDP 实际加载构建产物，验证
 *   1) /login 可渲染 + 主题样式生效（computed style 断言）
 *   2) 空表单提交 → 前端校验提示
 *   3) 后端 401 → 「邮箱或密码错误」提示（附截图）
 *   4) 登录成功 → token 落 localStorage 并跳转
 *   5) 登录后请求自动附带 Bearer token；侧边栏显示用户与退出入口
 *   6) 工作模式「文档库」列出文档并可查看内容（附截图）
 * 运行：node smoke_test.mjs <webRoot> <outDir>
 */
import { createServer } from "node:http";
import { readFile, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";
import os from "node:os";
import { mkdtempSync } from "node:fs";

const WEB_ROOT = process.argv[2] || path.join(path.dirname(new URL(import.meta.url).pathname.slice(1)), "..");
const OUT_DIR = process.argv[3] || process.cwd();
const PORT = 8210 + Math.floor(Math.random() * 300);
const CDP_PORT = 9410 + Math.floor(Math.random() * 300);
const CHROME = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const MIME = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".json": "application/json" };

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, "http://127.0.0.1");
    let file = path.join(WEB_ROOT, decodeURIComponent(url.pathname));
    if (url.pathname === "/" || !path.extname(file)) file = path.join(WEB_ROOT, "index.html");
    const body = await readFile(file);
    res.writeHead(200, { "Content-Type": MIME[path.extname(file)] || "application/octet-stream" });
    res.end(body);
  } catch { res.writeHead(404, { "Content-Type": "text/plain" }); res.end("not found"); }
});
await new Promise((r) => server.listen(PORT, "127.0.0.1", r));

const userDataDir = mkdtempSync(path.join(os.tmpdir(), "wa-chrome-"));
let chromeLog = "";
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--remote-debugging-port=0", `--user-data-dir=${userDataDir}`, "about:blank"], { stdio: ["ignore", "pipe", "pipe"] });
chrome.stdout.on("data", (d) => (chromeLog += d));
chrome.stderr.on("data", (d) => (chromeLog += d));

async function waitForCdp() {
  const portFile = path.join(userDataDir, "DevToolsActivePort");
  for (let i = 0; i < 120; i++) {
    try {
      const port = (await readFile(portFile, "utf8")).split("\n")[0].trim();
      const list = JSON.parse(await (await fetch(`http://127.0.0.1:${port}/json/list`)).text());
      const page = list.find((t) => t.type === "page") || list[0];
      if (page && page.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch {}
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error("Chrome CDP 未就绪；chrome 输出：\n" + chromeLog.slice(-600));
}

const ws = new WebSocket(await waitForCdp());
await new Promise((r) => (ws.onopen = r));
let nextId = 1;
const pending = new Map();
let events = [];
ws.onmessage = (m) => {
  const msg = JSON.parse(m.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); return; }
  events.push(msg);
};
const send = (method, params = {}) => {
  const id = nextId++;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => pending.set(id, (msg) => (msg.error ? reject(new Error(method + ": " + JSON.stringify(msg.error))) : resolve(msg.result))));
};
async function evaluate(expression) {
  const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error("页面执行异常: " + JSON.stringify(r.exceptionDetails));
  return r.result.value;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function waitFor(expression, timeout = 20000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    try { if (await evaluate(expression)) return true; } catch {}
    await sleep(200);
  }
  return false;
}
async function goto(url, settle = 400) {
  events = [];
  await send("Page.navigate", { url });
  await sleep(settle);
  // 页面需要等待 CDN 的 KaTeX 延迟脚本，用 DOM 条件代替固定等待
  await waitFor("!!document.getElementById('root') && document.getElementById('root').children.length > 0");
  await sleep(500);
}
async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  await writeFile(path.join(OUT_DIR, name), Buffer.from(r.data, "base64"));
}
/** 安装可配置的 fetch 桩，并记录请求（含 Authorization 头） */
const INSTALL_MOCK = `(() => {
  window.__calls = [];
  window.fetch = async (url, init) => {
    const u = String(url), method = (init && init.method) || "GET";
    window.__calls.push({ url: u, method, headers: (init && init.headers) || {}, body: (init && init.body) || "" });
    const json = (status, body) => ({ ok: status < 300, status, json: async () => body, text: async () => (typeof body === "string" ? body : JSON.stringify(body)) });
    if (u.includes("/api/auth/login")) return window.__mock.login ? window.__mock.login() : json(401, { detail: "Incorrect email or password" });
    if (u.includes("/api/files/") && u.includes("/content")) return json(200, "第四讲 信道容量\\nC = B·log2(1+SNR)");
    if (u.includes("/api/files")) return json(200, { files: [{ id: "f-1", name: "第四讲-信道容量.pdf", size: 204800, uploaded_at: "2026-10-14T02:00:00Z" }] });
    if (u.includes("/api/sessions/") && method === "POST") return json(200, { id: "s-1", title: "新会话" });
    return json(200, []);
  };
  window.__mock = {};
  return true;
})()`;

await send("Page.enable"); await send("Runtime.enable"); await send("Log.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });

const results = [];
const check = (name, ok, detail = "") => { results.push({ name, ok }); console.log((ok ? "  ✔ " : "  ✖ ") + name + (detail ? "  → " + detail : "")); };

/* ---------- 1. 登录页渲染与样式 ---------- */
console.log("\n[1] 登录页渲染");
await goto(`http://127.0.0.1:${PORT}/login`);
await shot("login-page.png");
const text1 = await evaluate("document.body.innerText");
check("页面渲染出登录表单", text1.includes("欢迎回来") && text1.includes("WirelessAgent"));
check("提供游客账号入口", text1.includes("游客"));
const style1 = await evaluate(`(() => {
  const inputs = [...document.querySelectorAll("input")];
  const cs = getComputedStyle(inputs[0]);
  const cs2 = getComputedStyle(inputs[1]);
  return JSON.stringify({ radius: cs.borderRadius, padX: cs.paddingLeft, border: cs.borderTopWidth, gap: cs2.marginTop });
})()`);
check("输入框主题样式生效（圆角/内边距/字段间距）", style1.includes('"radius":"20px"') && style1.includes('"padX":"16px"') && style1.includes('"gap":"14px"'), style1);

/* ---------- 2. 空表单校验 ---------- */
console.log("\n[2] 表单校验");
await evaluate("document.querySelector('form button[type=submit]').click()");
await sleep(400);
const emptyErr = await evaluate("(document.querySelector('[role=alert]')||{}).textContent||''");
check("空表单提示「请输入邮箱」", emptyErr.includes("请输入邮箱"), emptyErr);
const errStyle = await evaluate("(() => { const el = document.querySelector('[role=alert]'); if (!el) return ''; const cs = getComputedStyle(el); return cs.color + ' / ' + cs.backgroundColor; })()");
check("错误提示使用红色主题色", errStyle.includes("rgb(248, 113, 113)") && errStyle.includes("rgb(254, 242, 242)"), errStyle);
await shot("login-validation.png");

/* ---------- 3. 错误密码提示 ---------- */
console.log("\n[3] 后端 401");
await evaluate(INSTALL_MOCK + "; window.__mock.login = null; true");
await evaluate(`(() => {
  const setValue = (el, v) => { Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set.call(el, v); el.dispatchEvent(new Event("input", { bubbles: true })); };
  const inputs = [...document.querySelectorAll("input")];
  setValue(inputs[0], "student@example.com"); setValue(inputs[1], "wrongpass"); return true;
})()`);
await evaluate("document.querySelector('form button[type=submit]').click()");
await sleep(600);
const authErr = await evaluate("(document.querySelector('[role=alert]')||{}).textContent||''");
check("提示「邮箱或密码错误，请检查后重试」", authErr.includes("邮箱或密码错误"), authErr);
const req = await evaluate("JSON.stringify(window.__calls[0]||{})");
check("请求打到 /api/auth/login 且请求体正确", req.includes("/api/auth/login") && req.includes("student@example.com") && req.includes("wrongpass"), "");
await shot("login-wrong-password.png");

/* ---------- 4. 登录成功 ---------- */
console.log("\n[4] 登录成功");
await evaluate(`window.__mock.login = () => { const b = { access_token: "tk-smoke", user_id: 42, display_name: "冒烟测试用户" }; return { ok: true, status: 200, json: async () => b, text: async () => JSON.stringify(b) }; }; true`);
await evaluate("document.querySelector('form button[type=submit]').click()");
await sleep(900);
const stored = await evaluate("JSON.stringify({ token: localStorage.getItem('wagent.token'), user: localStorage.getItem('wagent.user'), path: location.pathname })");
check("token 写入 localStorage 并跳转首页", stored.includes("tk-smoke") && stored.includes('"path":"/"'), stored);

/* ---------- 5. 未授权自动登出（401） ---------- */
console.log("\n[5] 401 自动登出");
await goto(`http://127.0.0.1:${PORT}/work`);
await evaluate(INSTALL_MOCK + "; window.__mock.login = null; true");
await evaluate(`(() => { window.fetch = async (url, init) => { window.__calls.push({ url: String(url), headers: (init&&init.headers)||{} }); return { ok: false, status: 401, json: async () => ({}), text: async () => "{}" }; }; return true; })()`);
await evaluate("[...document.querySelectorAll('button')].find(b => b.textContent.trim() === '文档库').click()");
await sleep(900);
const after401 = await evaluate("JSON.stringify({ token: localStorage.getItem('wagent.token'), path: location.pathname + location.search })");
check("401 清除 token 并跳转 /login?redirect=", after401.includes('"token":null') && after401.includes('"path":"/login?redirect=%2Fwork&reason=expired"'), after401);

/* ---------- 6. 文档库（登录态 + 列表 + 查看） ---------- */
console.log("\n[6] 文档库");
await goto(`http://127.0.0.1:${PORT}/login`);
await evaluate(`localStorage.setItem("wagent.token","tk-smoke"); localStorage.setItem("wagent.user", JSON.stringify({ id: 42, name: "冒烟测试用户", email: "s@example.com", guest: false })); true`);
await goto(`http://127.0.0.1:${PORT}/work`, 1200);
await evaluate(INSTALL_MOCK + "; true");
const side = await evaluate(`JSON.stringify({ user: document.body.innerText.includes("冒烟测试用户"), signOut: !!document.querySelector('[title="退出登录"]') })`);
check("侧边栏显示当前用户与退出登录入口", side.includes('"user":true') && side.includes('"signOut":true'), side);
await evaluate("[...document.querySelectorAll('button')].find(b => b.textContent.trim() === '文档库').click()");
await sleep(800);
const authHeader = await evaluate("JSON.stringify((window.__calls.find(c => c.url.includes('/api/files')) || {}).headers || {})");
check("文档列表请求自动附带 Bearer token", authHeader.includes("Bearer tk-smoke"), authHeader);
const docsText = await evaluate("document.body.innerText");
check("列出后端返回的文档", docsText.includes("第四讲-信道容量.pdf") && docsText.includes("200.0 KB"), docsText.split("\n").filter((l) => l.includes("第四讲") || l.includes("KB")).join(" | "));
const pad = await evaluate("(() => { const h = [...document.querySelectorAll('h2')].find(x => x.textContent === '文档库'); return h ? getComputedStyle(h.parentElement.parentElement).paddingTop : ''; })()");
check("文档库页头间距样式生效（p-6 = 24px）", pad === "24px", pad);
await shot("work-docs.png");
await evaluate("[...document.querySelectorAll('button')].find(b => b.textContent.trim() === '查看').click()");
await sleep(700);
const modal = await evaluate("document.body.innerText");
check("查看弹层显示文档正文", modal.includes("信道容量") && modal.includes("log2"), "");
await shot("work-docs-view.png");

/* ---------- 7. 运行期报错（忽略静态服务器 404） ---------- */
console.log("\n[7] 运行期报错");
const errs = events.filter((e) => e.method === "Log.entryAdded" && e.params.entry.level === "error" && !/404|favicon/i.test(e.params.entry.text)).map((e) => e.params.entry.text);
check("无 JS 运行期报错", errs.length === 0, errs.slice(0, 3).join(" | "));

ws.close(); if (process.platform === "win32") { spawn("taskkill", ["/PID", String(chrome.pid), "/T", "/F"], { stdio: "ignore" }); } else { chrome.kill(); } server.close();
const failed = results.filter((r) => !r.ok).length;
console.log("\n通过 " + (results.length - failed) + "/" + results.length);
process.exit(failed ? 1 : 0);