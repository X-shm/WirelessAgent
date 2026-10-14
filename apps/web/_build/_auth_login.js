/* ---------------------------------------------------------------------------
 * 登录 / 注册页（可读副本）—— 由 _build/_extract_readable.mjs 生成，真正生效的代码在 _build/index.js 的 hx()。
 * Issue #11：表单校验、错误码提示、游客账号、登录后跳回来源页。
 * 别名对照：w→T（jsx 运行时）、R→D（React）、vt→Or（className 合并）、Mt→Yt（API client）、
 *           Va→tc（useNavigate）、WkAuth（_build/_auth_store.js 注入的全局对象）。
 * --------------------------------------------------------------------------- */

function hx(){
  const navigate = tc();
  const params = new URLSearchParams(window.location.search);
  const rawRedirect = params.get("redirect") || "/";
  const redirect = rawRedirect.indexOf("/") === 0 && rawRedirect.indexOf("//") !== 0 ? rawRedirect : "/";
  const expired = params.get("reason") === "expired";
  const [register, setRegister] = D.useState(false);
  const [email, setEmail] = D.useState("");
  const [password, setPassword] = D.useState("");
  const [confirm, setConfirm] = D.useState("");
  const [displayName, setDisplayName] = D.useState("");
  const [error, setError] = D.useState("");
  const [busy, setBusy] = D.useState(false);
  const mode = register ? "register" : "login";
  const fieldClass = "w-full bg-white border border-cream-300 rounded-2xl px-4 py-3 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-sunset-400/30 focus:border-sunset-400 transition-all";
  const submit = async event => {
    if (event) event.preventDefault();
    const checked = WkAuth.validateForm({ mode, email, password, confirm, displayName });
    if (!checked.ok) { setError(checked.message); return; }
    setBusy(true); setError("");
    try {
      const res = register
        ? await WkAuth.API.register(checked.value.email, checked.value.password, checked.value.displayName)
        : await WkAuth.API.login(checked.value.email, checked.value.password);
      if (res.ok) {
        const body = await res.json().catch(() => ({}));
        WkAuth.setSession({ ...body, email: checked.value.email });
        WkAuth.saveLastSessionId("");
        navigate(redirect);
        return;
      }
      setError(WkAuth.authErrorMessage(res.status, await WkAuth.readDetail(res), mode));
    } catch (e) {
      setError(WkAuth.networkErrorMessage());
    } finally {
      setBusy(false);
    }
  };
  const asGuest = async () => {
    setBusy(true); setError("");
    try {
      const res = await WkAuth.API.guest();
      if (res.ok) {
        const body = await res.json().catch(() => ({}));
        WkAuth.setSession({ ...body, guest: true });
        WkAuth.saveLastSessionId("");
        navigate(redirect);
        return;
      }
      setError(WkAuth.authErrorMessage(res.status, await WkAuth.readDetail(res), mode));
    } catch (e) {
      setError(WkAuth.networkErrorMessage());
    } finally {
      setBusy(false);
    }
  };
  const swapMode = () => { setRegister(!register); setError(""); setConfirm(""); };
  return T.jsxs("div",{className:"min-h-screen flex bg-gradient-to-br from-cream-50 via-cream-100 to-lavender-100",children:[
    T.jsxs("div",{className:"hidden lg:flex flex-1 items-center justify-center relative overflow-hidden",children:[
      T.jsx("div",{className:"absolute inset-0 welcome-grid"}),
      T.jsxs("div",{className:"relative z-10 text-center",children:[
        T.jsx("div",{className:"w-20 h-20 mx-auto mb-6 bg-white rounded-3xl p-4 shadow-xl shadow-orange-100 border border-cream-200",children:T.jsx(xl,{className:"w-full h-full text-sunset-500"})}),
        T.jsx("h1",{className:"text-4xl font-brand text-foreground mb-3",children:"WirelessAgent"}),
        T.jsxs("p",{className:"text-muted-foreground text-sm leading-relaxed max-w-xs mx-auto",children:["Your 24/7 Wireless AI Assistant",T.jsx("br",{}),"习题解答 · 标准检索 · 论文速递 · 网规辅助"]})
      ]})
    ]}),
    T.jsx("div",{className:"flex-1 flex items-center justify-center px-8",children:T.jsxs("div",{className:"w-full max-w-sm",children:[
      T.jsxs("div",{className:"lg:hidden text-center mb-8",children:[
        T.jsx("div",{className:"w-14 h-14 mx-auto mb-3 bg-white rounded-2xl p-3 shadow-lg shadow-orange-100 border border-cream-200",children:T.jsx(xl,{className:"w-full h-full text-sunset-500"})}),
        T.jsx("h1",{className:"text-2xl font-brand text-foreground",children:"WirelessAgent"})
      ]}),
      T.jsx("h2",{className:"text-xl font-bold text-foreground mb-1",children:register?"注册账号":"欢迎回来"}),
      T.jsx("p",{className:"text-sm text-muted-foreground mb-6",children:register?"注册后可保存聊天记录与工作文档":"登录后继续你的无线学习与科研"}),
      expired && T.jsx("p",{className:"text-xs text-sunset-500 bg-white border border-cream-200 rounded-xl px-3 py-2 mb-3",children:"登录状态已过期，请重新登录"}),
      T.jsxs("form",{onSubmit:submit,noValidate:true,className:"space-y-3.5",children:[
        register && T.jsx("input",{type:"text",value:displayName,onChange:f=>setDisplayName(f.target.value),placeholder:"昵称（可选）",disabled:busy,className:fieldClass}),
        T.jsx("input",{type:"email",value:email,onChange:f=>setEmail(f.target.value),placeholder:"邮箱",required:true,autoComplete:"username",disabled:busy,className:fieldClass}),
        T.jsx("input",{type:"password",value:password,onChange:f=>setPassword(f.target.value),placeholder:"密码（至少 6 位）",required:true,minLength:6,autoComplete:register?"new-password":"current-password",disabled:busy,className:fieldClass}),
        register && T.jsx("input",{type:"password",value:confirm,onChange:f=>setConfirm(f.target.value),placeholder:"确认密码",required:true,minLength:6,autoComplete:"new-password",disabled:busy,className:fieldClass}),
        error && T.jsx("p",{className:"text-red-400 text-xs bg-red-50 rounded-xl px-3 py-2",role:"alert",children:error}),
        T.jsxs("button",{type:"submit",disabled:busy,className:"w-full flex items-center justify-center gap-2 bg-sunset-500 hover:bg-sunset-600 disabled:opacity-40 text-white rounded-2xl py-3 text-sm font-semibold transition-all duration-200 shadow-md shadow-orange-200 hover:shadow-lg active:scale-[0.98]",children:[
          busy && T.jsx(Mo,{className:"w-4 h-4 animate-spin"}),
          register?"注册并登录":"登录"
        ]})
      ]}),
      T.jsxs("p",{className:"text-center text-muted-foreground/60 text-xs mt-5",children:[register?"已有账号？":"还没有账号？",T.jsx("button",{onClick:swapMode,type:"button",className:"text-sunset-500 hover:text-sunset-600 font-medium ml-1.5 transition-colors",children:register?"去登录":"免费注册"})]}),
      T.jsx("div",{className:"mt-4 text-center",children:T.jsx("button",{type:"button",onClick:asGuest,disabled:busy,className:"text-muted-foreground/40 hover:text-sunset-500 text-xs transition-colors",children:"跳过登录，以游客身份使用"})}),
      T.jsxs("div",{className:"mt-8 flex items-center gap-2 justify-center",children:[
        T.jsx(Mo,{className:"w-3.5 h-3.5 text-lavender-400"}),
        T.jsx("span",{className:"text-xs text-muted-foreground/40",children:"登录态保存在本地浏览器（localStorage）"})
      ]})
    ]})})
  ]});
}
