/**
 * WirelessAgent 前端「登录态 + 数据存储」层  (Issue #11)
 * ------------------------------------------------------------------
 * 该文件是前端鉴权与本地数据存储的唯一实现，被两处使用：
 *   1) 浏览器：index.html 通过 <script src="/assets/auth-store.js"> 先加载，
 *      注入 window.WkAuth，构建产物 _build/index.js 内部直接引用 WkAuth。
 *   2) 测试：apps/web/tests/auth_storage.test.mjs 用 node:vm 加载同一份文件，
 *      注入假的 localStorage / fetch / location，逐条覆盖 Issue #11 验收项。
 *
 * 依赖后端契约（详见 apps/web/docs/auth-storage-api.md）：
 *   POST /api/auth/register  POST /api/auth/login  POST /api/auth/guest
 *   POST /api/auth/logout    GET  /api/sessions/   POST /api/sessions/
 *   DELETE /api/sessions/{id}      GET /api/sessions/{id}/messages
 *   POST /api/chat/stream    GET  /api/files/      GET /api/files/{id}/content
 *   POST /api/files/upload   GET  /api/rag/search
 */
(function (root, factory) {
  var api = factory(root);
  if (typeof module === "object" && module.exports) { module.exports = api; }
  if (root) { root.WkAuth = api; }
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  var API_BASE = (root && root.WAGENT_API_BASE) || "/api";
  var MESSAGE_CACHE_LIMIT = 50;   // 每个会话最多缓存 50 条消息，避免 localStorage 膨胀
  var DOC_CACHE_LIMIT = 100;

  var KEYS = {
    token: "wagent.token",
    user: "wagent.user",
    lastSession: "wagent.last_session",
    docs: "wagent.docs",
    msgPrefix: "wagent.messages.",
    sessions: "wagent.sessions"
  };

  /* ---------------------------- 存储访问 ---------------------------- */

  var memoryStore = null;

  function createMemoryStore() {
    var map = {};
    var order = [];
    return {
      get length() { return order.length; },
      key: function (i) { return order[i] == null ? null : order[i]; },
      getItem: function (k) { return Object.prototype.hasOwnProperty.call(map, k) ? map[k] : null; },
      setItem: function (k, v) { if (!Object.prototype.hasOwnProperty.call(map, k)) { order.push(k); } map[k] = String(v); },
      removeItem: function (k) { delete map[k]; order = order.filter(function (x) { return x !== k; }); },
      clear: function () { map = {}; order = []; }
    };
  }

  function store() {
    if (root && root.localStorage) { return root.localStorage; }
    if (!memoryStore) { memoryStore = createMemoryStore(); }
    return memoryStore;
  }

  function readRaw(key) {
    try { return store().getItem(key); } catch (e) { return null; }
  }

  function writeRaw(key, value) {
    try { store().setItem(key, value); return true; } catch (e) { return false; }
  }

  function removeRaw(key) {
    try { store().removeItem(key); return true; } catch (e) { return false; }
  }

  function readJSON(key, fallback) {
    var raw = readRaw(key);
    if (!raw) { return fallback; }
    try { return JSON.parse(raw); } catch (e) { return fallback; }
  }

  function writeJSON(key, value) {
    try { return writeRaw(key, JSON.stringify(value)); } catch (e) { return false; }
  }

  function allKeys() {
    var out = [];
    try {
      var s = store();
      if (typeof s.key === "function" && typeof s.length === "number") {
        for (var i = 0; i < s.length; i++) { out.push(s.key(i)); }
      }
    } catch (e) { /* 隐私模式下 localStorage 可能抛异常，忽略 */ }
    return out;
  }

  /* ---------------------------- 登录态 ---------------------------- */

  // 兼容旧版本前端写入的裸 key（"token" / "user"），避免老标签页掉登录态
  function getToken() {
    var token = readRaw(KEYS.token) || readRaw("token");
    return token || "";
  }

  function getUser() {
    var user = readJSON(KEYS.user, null) || readJSON("user", null);
    return user && typeof user === "object" ? user : null;
  }

  function isAuthed() { return !!getToken(); }

  function isGuest() { var u = getUser(); return !!(u && u.guest); }

  /**
   * 保存登录态。payload 为后端返回体：
   * { access_token, user_id, display_name, email?, guest? }
   */
  function setSession(payload) {
    var data = payload || {};
    var token = data.access_token || data.token || "";
    var user = {
      id: data.user_id != null ? data.user_id : null,
      name: data.display_name || data.name || data.email || (data.guest ? "游客" : "用户"),
      email: data.email || "",
      guest: !!(data.guest || data.is_guest)
    };
    writeRaw(KEYS.token, token);
    writeJSON(KEYS.user, user);
    writeRaw("token", token);
    writeJSON("user", user);
    return user;
  }

  /** 登出：清除登录态与本地缓存（聊天记录、会话列表、文档索引） */
  function clearSession() {
    [KEYS.token, KEYS.user, KEYS.lastSession, KEYS.docs, "token", "user"].forEach(removeRaw);
    allKeys().forEach(function (k) {
      if (k.indexOf(KEYS.msgPrefix) === 0 || k === KEYS.sessions) { removeRaw(k); }
    });
    return true;
  }

  /* ---------------------------- 请求封装 ---------------------------- */

  function isAuthPath(path) { return path.indexOf("/auth/") === 0; }

  function currentPath() {
    try {
      if (root && root.location) { return (root.location.pathname || "/") + (root.location.search || ""); }
    } catch (e) { /* ignore */ }
    return "/";
  }

  /**
   * 登录态失效时跳转登录页；已在 /login 上不重复跳转，避免循环。
   * 返回是否发生了跳转。
   */
  function goToLogin(reason) {
    if (!root || !root.location || typeof root.location.replace !== "function") { return false; }
    var path = currentPath();
    if (path.indexOf("/login") === 0) { return false; }
    var target = "/login?redirect=" + encodeURIComponent(path) + (reason ? "&reason=" + encodeURIComponent(reason) : "");
    root.location.replace(target);
    return true;
  }

  function authHeaders(extra) {
    var headers = {};
    var k;
    for (k in (extra || {})) { if (Object.prototype.hasOwnProperty.call(extra, k)) { headers[k] = extra[k]; } }
    var token = getToken();
    if (token) { headers.Authorization = "Bearer " + token; }
    return headers;
  }

  function fetchOf(options) {
    var fn = (options && options.fetch) || (root && root.fetch);
    if (typeof fn !== "function") { return null; }
    return fn;
  }

  /**
   * 统一请求入口：自动附带 token；非 /auth/* 接口返回 401 时自动登出并跳转登录页。
   * 保持与旧实现一致的返回：Promise<Response>，由调用方判断 res.ok。
   */
  function request(path, options) {
    var opts = options || {};
    var fetchFn = fetchOf(opts);
    if (!fetchFn) { return Promise.reject(new Error("fetch is not available")); }
    var headers = authHeaders(opts.headers);
    if (opts.body && typeof opts.body === "string" && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }
    return Promise.resolve(fetchFn(API_BASE + path, {
      method: opts.method || "GET",
      headers: headers,
      body: opts.body
    })).then(function (res) {
      if (res && res.status === 401 && !isAuthPath(path)) {
        clearSession();
        goToLogin("expired");
      }
      return res;
    });
  }

  /* ---------------------------- 接口定义 ---------------------------- */

  var API = {
    login: function (email, password) {
      return request("/auth/login", { method: "POST", body: JSON.stringify({ email: email, password: password }) });
    },
    register: function (email, password, displayName) {
      return request("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email: email, password: password, display_name: displayName })
      });
    },
    guest: function () {
      return request("/auth/guest", { method: "POST", body: "{}" });
    },
    logout: function () {
      var p;
      try { p = request("/auth/logout", { method: "POST", body: "{}" }); } catch (e) { p = Promise.resolve(null); }
      return Promise.resolve(p).catch(function () { return null; }).then(function () { clearSession(); return true; });
    },
    listSessions: function () { return request("/sessions/"); },
    createSession: function () { return request("/sessions/", { method: "POST" }); },
    deleteSession: function (id) { return request("/sessions/" + id, { method: "DELETE" }); },
    getMessages: function (sessionId) { return request("/sessions/" + sessionId + "/messages"); },
    listFiles: function () { return request("/files/"); },
    fileContent: function (fileId) { return request("/files/" + fileId + "/content"); },
    search: function (query, topK) {
      return request("/rag/search?q=" + encodeURIComponent(query) + "&top_k=" + (topK || 5));
    },
    chatStream: function (sessionId, message) {
      var fetchFn = fetchOf(null);
      if (!fetchFn) { return Promise.reject(new Error("fetch is not available")); }
      var headers = authHeaders({ "Content-Type": "application/json" });
      return Promise.resolve(fetchFn(API_BASE + "/chat/stream", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ session_id: sessionId, message: message })
      })).then(function (res) {
        if (res && res.status === 401) { clearSession(); goToLogin("expired"); }
        return res;
      });
    },
    upload: function (file) {
      var fetchFn = fetchOf(null);
      if (!fetchFn) { return Promise.reject(new Error("fetch is not available")); }
      var form = new FormData();
      form.append("file", file);
      return Promise.resolve(fetchFn(API_BASE + "/files/upload", {
        method: "POST",
        headers: authHeaders({}),
        body: form
      })).then(function (res) {
        if (res && res.status === 401) { clearSession(); goToLogin("expired"); }
        return res;
      });
    }
  };

  /* ---------------------------- 本地缓存 ---------------------------- */

  function cleanMessages(messages) {
    return (messages || [])
      .filter(function (m) { return m && typeof m.content === "string" && m.content.length > 0; })
      .slice(-MESSAGE_CACHE_LIMIT)
      .map(function (m) {
        return { id: m.id != null ? m.id : null, role: m.role || "user", content: m.content };
      });
  }

  /** 缓存某个会话的聊天记录，用于刷新页面后立即恢复（服务端返回后再覆盖） */
  function saveMessages(sessionId, messages) {
    if (!sessionId) { return false; }
    return writeJSON(KEYS.msgPrefix + sessionId, cleanMessages(messages));
  }

  function loadMessages(sessionId) {
    if (!sessionId) { return []; }
    var list = readJSON(KEYS.msgPrefix + sessionId, []);
    return Array.isArray(list) ? list : [];
  }

  function clearMessages(sessionId) {
    if (!sessionId) { return false; }
    return removeRaw(KEYS.msgPrefix + sessionId);
  }

  function saveLastSessionId(sessionId) { return writeRaw(KEYS.lastSession, sessionId || ""); }

  function getLastSessionId() { return readRaw(KEYS.lastSession) || ""; }

  function saveSessions(list) {
    return writeJSON(KEYS.sessions, Array.isArray(list) ? list.slice(0, 50) : []);
  }

  function loadSessions() {
    var list = readJSON(KEYS.sessions, []);
    return Array.isArray(list) ? list : [];
  }

  function docKey(doc) {
    if (!doc) { return ""; }
    return String(doc.id != null ? doc.id : (doc.name || "") + ":" + (doc.size != null ? doc.size : ""));
  }

  function saveDocs(list) {
    var clean = (Array.isArray(list) ? list : [])
      .filter(function (d) { return d && (d.id != null || d.name); })
      .slice(0, DOC_CACHE_LIMIT)
      .map(function (d) {
        return {
          id: d.id != null ? d.id : null,
          name: d.name || d.filename || "未命名文档",
          size: d.size != null ? d.size : null,
          uploaded_at: d.uploaded_at || d.created_at || null,
          source: d.source || "server"
        };
      });
    return writeJSON(KEYS.docs, clean);
  }

  function loadDocs() {
    var list = readJSON(KEYS.docs, []);
    return Array.isArray(list) ? list : [];
  }

  /** 本地记录与后端列表合并（后端优先，按 id/名称去重），保证上传记录不丢失 */
  function mergeDocs(list) {
    var merged = normalizeDocs(list || []);
    var byKey = {};
    merged.forEach(function (d) { byKey[docKey(d)] = d; });
    loadDocs().forEach(function (d) {
      var key = docKey(d);
      if (!byKey[key]) { byKey[key] = d; }
    });
    var out = Object.keys(byKey).map(function (k) { return byKey[k]; }).slice(0, DOC_CACHE_LIMIT);
    writeJSON(KEYS.docs, out);
    return out;
  }

  function normalizeDocs(list) {
    return (Array.isArray(list) ? list : [])
      .filter(function (d) { return d && (d.id != null || d.name); })
      .slice(0, DOC_CACHE_LIMIT)
      .map(function (d) {
        return {
          id: d.id != null ? d.id : null,
          name: d.name || d.filename || "未命名文档",
          size: d.size != null ? d.size : null,
          uploaded_at: d.uploaded_at || d.created_at || null,
          source: d.source || "server"
        };
      });
  }

  function removeDoc(id) {
    var list = loadDocs().filter(function (d) { return String(d.id) !== String(id); });
    writeJSON(KEYS.docs, list);
    return list;
  }

  /* ---------------------------- 表单校验与错误提示 ---------------------------- */

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /**
   * 登录 / 注册表单校验（纯函数，便于单测）。
   * 返回 { ok, field, message, value }
   */
  function validateForm(form) {
    var f = form || {};
    var mode = f.mode === "register" ? "register" : "login";
    var email = (f.email || "").trim();
    var password = f.password || "";
    var confirm = f.confirm || "";
    var displayName = (f.displayName || "").trim();

    if (!email) { return { ok: false, field: "email", message: "请输入邮箱" }; }
    if (!EMAIL_RE.test(email)) { return { ok: false, field: "email", message: "邮箱格式不正确，例如 student@example.com" }; }
    if (!password) { return { ok: false, field: "password", message: "请输入密码" }; }
    if (password.length < 6) { return { ok: false, field: "password", message: "密码至少 6 位" }; }
    if (mode === "register") {
      if (!confirm) { return { ok: false, field: "confirm", message: "请再次输入密码" }; }
      if (confirm !== password) { return { ok: false, field: "confirm", message: "两次输入的密码不一致" }; }
      if (displayName.length > 24) { return { ok: false, field: "displayName", message: "昵称不能超过 24 个字符" }; }
    }
    return {
      ok: true,
      field: "",
      message: "",
      value: { mode: mode, email: email, password: password, displayName: displayName || email.split("@")[0] }
    };
  }

  /** 把后端状态码翻译成给用户看的中文提示（错误密码必须明确提示） */
  function authErrorMessage(status, detail, mode) {
    var isRegister = mode === "register";
    if (status === 401) { return "邮箱或密码错误，请检查后重试"; }
    if (status === 409) { return "该邮箱已被注册，请直接登录"; }
    if (status === 403) { return isRegister ? "该邮箱已被注册，请直接登录" : "账号已被禁用，请联系管理员"; }
    if (status === 400) { return detail ? "输入有误：" + detail : "输入有误，请检查邮箱与密码"; }
    if (status === 422) { return detail ? "输入有误：" + detail : "邮箱或密码格式不符合要求"; }
    if (status === 404) { return "认证接口不存在（404），请与后端同学确认 /api/auth 契约"; }
    if (status === 429) { return "尝试过于频繁，请稍后再登录"; }
    if (status >= 500) { return "服务异常（" + status + "），请稍后重试"; }
    return detail || "认证失败，请稍后重试";
  }

  function networkErrorMessage() { return "无法连接服务器，请检查网络或后端服务是否已启动"; }

  /** 读取响应体中的错误详情（后端可能返回 { detail } / { message } / 纯文本） */
  function readDetail(response) {
    if (!response || typeof response.json !== "function") { return ""; }
    return Promise.resolve(response.json())
      .then(function (body) {
        if (!body) { return ""; }
        if (typeof body === "string") { return body; }
        return body.detail || body.message || body.error || "";
      })
      .catch(function () { return ""; });
  }

  function formatSize(bytes) {
    if (bytes == null || isNaN(bytes)) { return ""; }
    if (bytes < 1024) { return bytes + " B"; }
    if (bytes < 1024 * 1024) { return (bytes / 1024).toFixed(1) + " KB"; }
    return (bytes / 1024 / 1024).toFixed(1) + " MB";
  }

  return {
    API_BASE: API_BASE,
    KEYS: KEYS,
    getToken: getToken,
    getUser: getUser,
    isAuthed: isAuthed,
    isGuest: isGuest,
    setSession: setSession,
    clearSession: clearSession,
    goToLogin: goToLogin,
    request: request,
    API: API,
    saveMessages: saveMessages,
    loadMessages: loadMessages,
    clearMessages: clearMessages,
    saveLastSessionId: saveLastSessionId,
    getLastSessionId: getLastSessionId,
    saveSessions: saveSessions,
    loadSessions: loadSessions,
    saveDocs: saveDocs,
    loadDocs: loadDocs,
    mergeDocs: mergeDocs,
    removeDoc: removeDoc,
    validateForm: validateForm,
    authErrorMessage: authErrorMessage,
    networkErrorMessage: networkErrorMessage,
    readDetail: readDetail,
    formatSize: formatSize
  };
});