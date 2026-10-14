/**
 * Issue #11 前端「登录态 + 数据存储」单测
 * ------------------------------------------------------------------
 * 运行：node --test apps/web/tests/auth_storage.test.mjs
 * 特点：直接加载 _build/_auth_store.js（与线上 /assets/auth-store.js 同一份源码），
 *       用 node:vm 注入假 localStorage / fetch / location，无需浏览器、无需 npm 依赖。
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import vm from "node:vm";

const here = path.dirname(fileURLToPath(import.meta.url));
const STORE_SOURCE = readFileSync(path.join(here, "..", "_build", "_auth_store.js"), "utf8");

function jsonResponse(status, body) {
  return {
    status,
    ok: status >= 200 && status < 300,
    json: async () => body,
    text: async () => (typeof body === "string" ? body : JSON.stringify(body))
  };
}

/**
 * 建立隔离的运行环境：假 localStorage + 假 location + 记录型 fetch。
 * handler(url, init) 返回假 Response。
 */
function createEnv({ pathname = "/", search = "", handler } = {}) {
  const data = new Map();
  const localStorage = {
    get length() { return data.size; },
    key: (i) => Array.from(data.keys())[i] ?? null,
    getItem: (k) => (data.has(k) ? data.get(k) : null),
    setItem: (k, v) => { data.set(k, String(v)); },
    removeItem: (k) => { data.delete(k); },
    clear: () => data.clear()
  };
  const navigations = [];
  const calls = [];
  const location = { pathname, search, replace: (url) => { navigations.push(url); } };
  const fetchImpl = async (url, init = {}) => {
    calls.push({ url, init });
    return handler ? handler(url, init) : jsonResponse(200, {});
  };
  const root = { localStorage, location, console, WAGENT_API_BASE: "/api", fetch: fetchImpl };
  vm.createContext(root);
  vm.runInContext(STORE_SOURCE, root, { filename: "_auth_store.js" });
  return { WkAuth: root.WkAuth, localStorage, location, navigations, calls, root };
}

/* --------------------------- 验收项 1：表单校验与错误提示 --------------------------- */

test("validateForm：登录表单校验邮箱与密码", () => {
  const { WkAuth } = createEnv();
  assert.equal(WkAuth.validateForm({ mode: "login", email: "", password: "" }).message, "请输入邮箱");
  assert.equal(WkAuth.validateForm({ mode: "login", email: "abc", password: "123456" }).message, "邮箱格式不正确，例如 student@example.com");
  assert.equal(WkAuth.validateForm({ mode: "login", email: "a@b.com", password: "" }).message, "请输入密码");
  assert.equal(WkAuth.validateForm({ mode: "login", email: "a@b.com", password: "123" }).message, "密码至少 6 位");

  const ok = WkAuth.validateForm({ mode: "login", email: " Student@Example.com ", password: "abcdef" });
  assert.equal(ok.ok, true);
  assert.equal(ok.value.email, "Student@Example.com");
});

test("validateForm：注册表单校验二次密码与昵称", () => {
  const { WkAuth } = createEnv();
  const base = { mode: "register", email: "a@b.com", password: "abcdef" };
  assert.equal(WkAuth.validateForm(base).message, "请再次输入密码");
  assert.equal(WkAuth.validateForm({ ...base, confirm: "abcdefg" }).message, "两次输入的密码不一致");
  assert.equal(WkAuth.validateForm({ ...base, confirm: "abcdef", displayName: "x".repeat(25) }).message, "昵称不能超过 24 个字符");

  const ok = WkAuth.validateForm({ ...base, confirm: "abcdef" });
  assert.equal(ok.ok, true);
  assert.equal(ok.value.displayName, "a"); // 未填昵称时取邮箱前缀
});

test("authErrorMessage：错误密码有明确提示，各类状态码可读", () => {
  const { WkAuth } = createEnv();
  assert.equal(WkAuth.authErrorMessage(401, "Incorrect password", "login"), "邮箱或密码错误，请检查后重试");
  assert.equal(WkAuth.authErrorMessage(409, "", "register"), "该邮箱已被注册，请直接登录");
  assert.equal(WkAuth.authErrorMessage(403, "", "register"), "该邮箱已被注册，请直接登录");
  assert.equal(WkAuth.authErrorMessage(403, "", "login"), "账号已被禁用，请联系管理员");
  assert.equal(WkAuth.authErrorMessage(400, "password too short", "login"), "输入有误：password too short");
  assert.equal(WkAuth.authErrorMessage(404, "", "login"), "认证接口不存在（404），请与后端同学确认 /api/auth 契约");
  assert.equal(WkAuth.authErrorMessage(503, "", "login"), "服务异常（503），请稍后重试");
  assert.equal(WkAuth.networkErrorMessage(), "无法连接服务器，请检查网络或后端服务是否已启动");
});

/* --------------------------- 验收项 2：token 存储与自动附带、401 自动登出 --------------------------- */

test("setSession：token 与用户信息写入本地存储", () => {
  const { WkAuth, localStorage } = createEnv();
  const user = WkAuth.setSession({ access_token: "tk-1", user_id: 7, display_name: "泽扬", email: "z@example.com" });
  assert.equal(user.name, "泽扬");
  assert.equal(WkAuth.getToken(), "tk-1");
  assert.equal(WkAuth.isAuthed(), true);
  assert.equal(WkAuth.isGuest(), false);
  assert.equal(localStorage.getItem("wagent.token"), "tk-1");
  assert.equal(localStorage.getItem("token"), "tk-1"); // 兼容旧标签页
});

test("getToken：兼容旧版本写入的裸 token", () => {
  const { WkAuth, localStorage } = createEnv();
  localStorage.setItem("token", "legacy-token");
  assert.equal(WkAuth.getToken(), "legacy-token");
  assert.equal(WkAuth.isAuthed(), true);
});

test("request：自动附带 Authorization 头", async () => {
  const { WkAuth, calls } = createEnv({ handler: () => jsonResponse(200, []) });
  WkAuth.setSession({ access_token: "tk-abc", user_id: 1, display_name: "用户" });
  const res = await WkAuth.API.listSessions();
  assert.equal(res.status, 200);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "/api/sessions/");
  assert.equal(calls[0].init.headers.Authorization, "Bearer tk-abc");
});

test("request：401 自动登出并跳转登录页（携带来源路径）", async () => {
  const { WkAuth, navigations, localStorage } = createEnv({
    pathname: "/work",
    search: "?tab=docs",
    handler: () => jsonResponse(401, { detail: "token expired" })
  });
  WkAuth.setSession({ access_token: "tk-old", user_id: 1, display_name: "用户" });
  await WkAuth.API.listSessions();
  assert.equal(WkAuth.isAuthed(), false);
  assert.equal(localStorage.getItem("wagent.token"), null);
  assert.equal(navigations.length, 1);
  assert.equal(navigations[0], "/login?redirect=%2Fwork%3Ftab%3Ddocs&reason=expired");
});

test("request：已在 /login 页时 401 不再跳转（防止循环）", async () => {
  const { WkAuth, navigations } = createEnv({ pathname: "/login", handler: () => jsonResponse(401, {}) });
  WkAuth.setSession({ access_token: "tk-old", user_id: 1, display_name: "用户" });
  await WkAuth.API.listSessions();
  assert.equal(WkAuth.isAuthed(), false);
  assert.equal(navigations.length, 0);
});

test("API.login：后端返回 401 时不跳转，交给页面提示「邮箱或密码错误」", async () => {
  const { WkAuth, navigations, calls } = createEnv({ handler: () => jsonResponse(401, { detail: "Incorrect email or password" }) });
  const res = await WkAuth.API.login("a@b.com", "wrongpass");
  assert.equal(res.status, 401);
  assert.equal(calls[0].url, "/api/auth/login");
  assert.equal(calls[0].init.method, "POST");
  assert.deepEqual(JSON.parse(calls[0].init.body), { email: "a@b.com", password: "wrongpass" });
  assert.equal(navigations.length, 0);
  const detail = await WkAuth.readDetail(res);
  assert.equal(WkAuth.authErrorMessage(res.status, detail, "login"), "邮箱或密码错误，请检查后重试");
});

test("API.chatStream / upload：流式与上传请求同样附带 token，401 也会自动登出", async () => {
  let status = 200;
  const { WkAuth, navigations, calls } = createEnv({ handler: () => jsonResponse(status, {}) });
  WkAuth.setSession({ access_token: "tk-s", user_id: 2, display_name: "用户" });
  await WkAuth.API.chatStream("s-1", "你好");
  assert.equal(calls[0].url, "/api/chat/stream");
  assert.equal(calls[0].init.headers.Authorization, "Bearer tk-s");
  assert.equal(navigations.length, 0);

  status = 401;
  await WkAuth.API.chatStream("s-1", "你好");
  assert.equal(WkAuth.isAuthed(), false);
  assert.equal(navigations.length, 1);
});

test("API.logout：调用后端并清除本地登录态", async () => {
  const { WkAuth, calls } = createEnv({ handler: () => jsonResponse(200, { ok: true }) });
  WkAuth.setSession({ access_token: "tk-x", user_id: 3, display_name: "用户" });
  await WkAuth.API.logout();
  assert.equal(calls[0].url, "/api/auth/logout");
  assert.equal(WkAuth.isAuthed(), false);
});

/* --------------------------- 验收项 3：聊天记录本地缓存与恢复 --------------------------- */

test("saveMessages/loadMessages：刷新页面后可恢复聊天记录，并限制缓存条数", () => {
  const { WkAuth } = createEnv();
  const many = Array.from({ length: 60 }, (_, i) => ({ id: i, role: i % 2 ? "assistant" : "user", content: "msg-" + i }));
  WkAuth.saveMessages("s-1", many);
  const cached = WkAuth.loadMessages("s-1");
  assert.equal(cached.length, 50);
  assert.equal(cached[0].content, "msg-10");      // 只保留最近 50 条
  assert.equal(cached[49].content, "msg-59");
  assert.equal(WkAuth.loadMessages("s-2").length, 0); // 会话之间相互隔离
});

test("saveMessages：过滤空消息，会话隔离", () => {
  const { WkAuth } = createEnv();
  WkAuth.saveMessages("s-1", [{ id: 1, role: "user", content: "问题" }, { id: 2, role: "assistant", content: "" }, null]);
  assert.equal(WkAuth.loadMessages("s-1").map((m) => m.content).join("|"), "问题"); // vm 跨域数组，用字符串比较
  assert.equal(WkAuth.saveMessages("", []), false);
});

test("clearSession：登出后清理消息、会话列表与文档索引", () => {
  const { WkAuth, localStorage } = createEnv();
  WkAuth.setSession({ access_token: "tk", user_id: 1, display_name: "用户" });
  WkAuth.saveMessages("s-1", [{ id: 1, role: "user", content: "hi" }]);
  WkAuth.saveSessions([{ id: "s-1", title: "会话" }]);
  WkAuth.saveDocs([{ id: "f-1", name: "讲义.pdf", size: 1024 }]);
  WkAuth.saveLastSessionId("s-1");

  WkAuth.clearSession();
  assert.equal(WkAuth.getToken(), "");
  assert.equal(WkAuth.getUser(), null);
  assert.equal(WkAuth.loadMessages("s-1").length, 0);
  assert.equal(WkAuth.loadSessions().length, 0);
  assert.equal(WkAuth.loadDocs().length, 0);
  assert.equal(WkAuth.getLastSessionId(), "");
  assert.equal(localStorage.length, 0);
});

/* --------------------------- 验收项 4：工作文档本地记录 --------------------------- */

test("文档缓存：saveDocs / loadDocs / mergeDocs 去重且不丢本地记录", () => {
  const { WkAuth } = createEnv();
  WkAuth.saveDocs([{ id: "f-1", name: "本地讲义.pdf", size: 2048 }]);
  const merged = WkAuth.mergeDocs([
    { id: "f-1", name: "本地讲义.pdf", size: 2048, source: "server" },
    { id: "f-2", name: "标准.pdf", size: 4096, source: "server" }
  ]);
  assert.equal(merged.length, 2);
  assert.equal(WkAuth.loadDocs().length, 2);
  assert.equal(WkAuth.removeDoc("f-2").length, 1);
  assert.equal(WkAuth.formatSize(1536), "1.5 KB");
});

test("归一化：缺少 id 时用「名称+大小」作为兜底 key", () => {
  const { WkAuth } = createEnv();
  WkAuth.saveDocs([{ name: "无 id 文档.docx", size: 100 }]);
  assert.equal(WkAuth.loadDocs()[0].name, "无 id 文档.docx");
  const merged = WkAuth.mergeDocs([{ name: "无 id 文档.docx", size: 100 }]);
  assert.equal(merged.length, 1); // 不会因为缺少 id 而重复
});