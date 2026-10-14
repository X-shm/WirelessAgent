/* ---------------------------------------------------------------------------
 * 工作模式 · 文档库（可读副本）—— 由 _build/_extract_readable.mjs 生成，真正生效的代码在 _build/index.js 的 WkDocsView()。
 * Issue #11：文档列表 / 刷新 / 查看，后端接口未就绪时退回本地记录。
 * 别名对照：w→T（jsx 运行时）、R→D（React）、vt→Or（className 合并）、Mt→Yt（API client）、
 *           Va→tc（useNavigate）、WkAuth（_build/_auth_store.js 注入的全局对象）。
 * --------------------------------------------------------------------------- */

function WkDocsView(){
  const [docs, setDocs] = D.useState(WkAuth.loadDocs());
  const [loading, setLoading] = D.useState(false);
  const [error, setError] = D.useState("");
  const [notice, setNotice] = D.useState("");
  const [viewing, setViewing] = D.useState(null);
  const load = D.useCallback(async () => {
    setLoading(true); setError(""); setNotice("");
    try {
      const res = await WkAuth.API.listFiles();
      if (res.ok) {
        const body = await res.json().catch(() => ({}));
        const list = Array.isArray(body) ? body : (body.files || body.items || body.data || []);
        setDocs(WkAuth.mergeDocs(list));
      } else if (res.status === 404) {
        setDocs(WkAuth.loadDocs());
        setNotice("后端 /api/files 尚未提供（404），当前显示本地记录");
      } else {
        setError("文档列表加载失败（HTTP " + res.status + "）");
      }
    } catch (e) {
      setDocs(WkAuth.loadDocs());
      setNotice("无法连接服务器，当前显示本地记录");
    } finally {
      setLoading(false);
    }
  }, []);
  D.useEffect(() => { load(); }, [load]);
  const open = async doc => {
    if (doc.id == null) { setViewing({ name: doc.name, text: "该记录来自本地缓存，后端未返回文档 ID，暂时无法查看内容。", loading: false }); return; }
    setViewing({ name: doc.name, text: "", loading: true });
    try {
      const res = await WkAuth.API.fileContent(doc.id);
      if (res.ok) {
        const text = await res.text();
        setViewing({ name: doc.name, text: text || "（空文档）", loading: false });
      } else {
        setViewing({ name: doc.name, text: "查看失败（HTTP " + res.status + "），后端 /api/files/{id}/content 可能尚未提供。", loading: false });
      }
    } catch (e) {
      setViewing({ name: doc.name, text: "无法连接服务器，暂时无法查看文档内容。", loading: false });
    }
  };
  return T.jsxs("div",{className:"flex-1 flex flex-col min-w-0",children:[
    T.jsxs("div",{className:"p-6 pb-4 border-b border-cream-200 flex items-start gap-4",children:[
      T.jsxs("div",{className:"flex-1 min-w-0",children:[
        T.jsx("h2",{className:"font-brand text-2xl text-foreground",children:"文档库"}),
        T.jsx("p",{className:"text-sm text-muted-foreground mt-1",children:"上传的课件 / 标准文档，支持刷新列表与查看内容"})
      ]}),
      T.jsxs("button",{type:"button",onClick:load,disabled:loading,className:"flex items-center gap-1.5 px-4 py-2.5 rounded-2xl bg-white border border-cream-200 text-sm text-muted-foreground hover:text-sunset-500 disabled:opacity-40 transition-all",children:[T.jsx(WkRefresh,{className:"w-4 h-4"}),"刷新"]})
    ]}),
    T.jsxs("div",{className:"flex-1 overflow-y-auto px-6 py-6 space-y-3",children:[
      notice && T.jsx("p",{className:"text-xs text-sunset-500 bg-white border border-cream-200 rounded-xl px-3 py-2",children:notice}),
      error && T.jsx("p",{className:"text-xs text-red-400 bg-red-50 rounded-xl px-3 py-2",children:error}),
      docs.length === 0 && T.jsx("p",{className:"text-sm text-muted-foreground/50 mt-8 text-center",children:"还没有文档，切换到「文件上传」上传课件或标准文档"}),
      docs.map((d,i)=>{
        const meta = [WkAuth.formatSize(d.size), d.uploaded_at ? new Date(d.uploaded_at).toLocaleString("zh-CN") : "本地记录"].filter(Boolean).join(" · ");
        return T.jsxs("div",{className:"bg-white rounded-2xl border border-cream-200 p-4 shadow-sm flex items-center gap-3",children:[
          T.jsx(WkFileText,{className:"w-5 h-5 text-sunset-400 shrink-0"}),
          T.jsxs("div",{className:"flex-1 min-w-0",children:[
            T.jsx("p",{className:"text-sm font-medium text-foreground truncate",children:d.name}),
            T.jsx("p",{className:"text-xs text-muted-foreground/50",children:meta})
          ]}),
          T.jsxs("button",{type:"button",onClick:()=>open(d),className:"flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs text-sunset-500 hover:bg-cream-100 transition-all",children:[T.jsx(WkEye,{className:"w-3.5 h-3.5"}),"查看"]})
        ]}, (d.id!=null?String(d.id):d.name) + "-" + i);
      })
    ]}),
    viewing && T.jsx("div",{className:"fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/40",onClick:()=>setViewing(null),children:T.jsxs("div",{className:"bg-white rounded-3xl border border-cream-200 shadow-xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden",onClick:e=>e.stopPropagation(),children:[
      T.jsxs("div",{className:"p-5 border-b border-cream-200 flex items-center gap-3",children:[
        T.jsx("p",{className:"flex-1 min-w-0 text-sm font-medium text-foreground truncate",children:viewing.name}),
        T.jsx("button",{type:"button",onClick:()=>setViewing(null),className:"p-1.5 rounded-lg text-muted-foreground/40 hover:text-red-400 hover:bg-red-50 transition-all",children:T.jsx(WkClose,{className:"w-4 h-4"})})
      ]}),
      T.jsx("div",{className:"flex-1 overflow-y-auto p-5 text-sm text-muted-foreground whitespace-pre-wrap",children:viewing.loading ? "加载中…" : viewing.text})
    ]})})
  ]});
}
