function WkRagSearch() {
  const [q, setQ] = D.useState("");
  const [res, setRes] = D.useState(null);
  const [loading, setLoading] = D.useState(!1);
  const [err, setErr] = D.useState("");
  const run = async () => {
    const query = q.trim();
    if (!query) return;
    setLoading(!0);
    setErr("");
    setRes(null);
    try {
      const r = await Yt.search(query);
      if (r.ok) setRes(await r.json());
      else setErr("检索失败，请稍后重试");
    } catch {
      setErr("网络错误，请检查连接后重试");
    } finally {
      setLoading(!1);
    }
  };
  const items =
    res == null
      ? []
      : Array.isArray(res)
        ? res
        : res.results || res.data || res.chunks || [];
  return T.jsxs("div", {
    className: "flex-1 flex flex-col min-w-0",
    children: [
      T.jsxs("div", {
        className: "p-6 pb-4 border-b border-cream-200",
        children: [
          T.jsx("h2", {
            className: "font-brand text-2xl text-foreground",
            children: "标准检索",
          }),
          T.jsx("p", {
            className: "text-sm text-muted-foreground mt-1",
            children: "在知识库中语义检索 3GPP / ITU / IEEE 标准与课程知识点",
          }),
        ],
      }),
      T.jsx("div", {
        className: "px-6 py-4",
        children: T.jsxs("div", {
          className: "flex gap-2 max-w-2xl",
          children: [
            T.jsx("input", {
              value: q,
              onChange: (e) => setQ(e.target.value),
              onKeyDown: (e) => e.key === "Enter" && run(),
              placeholder: "输入关键词或问题，如：5G NR 子载波间隔",
              className:
                "flex-1 rounded-2xl border border-cream-300 bg-white px-4 py-3 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:border-sunset-400",
            }),
            T.jsxs("button", {
              onClick: run,
              disabled: loading,
              className:
                "px-5 py-3 rounded-2xl bg-sunset-500 hover:bg-sunset-600 disabled:opacity-40 text-white text-sm font-medium transition-all duration-200",
              children: [
                loading
                  ? T.jsx(nc, { className: "w-4 h-4 animate-spin" })
                  : T.jsx(WkSearch, { className: "w-4 h-4" }),
              ],
            }),
          ],
        }),
      }),
      T.jsx("div", {
        className: "flex-1 overflow-y-auto px-6 pb-6",
        children: err
          ? T.jsx("p", { className: "text-sm text-red-400", children: err })
          : res == null
            ? T.jsx("p", {
                className: "text-sm text-muted-foreground/50 mt-8 text-center",
                children: "输入查询后回车或点击搜索按钮",
              })
            : items.length === 0
              ? T.jsx("p", {
                  className: "text-sm text-muted-foreground/50 mt-8 text-center",
                  children: "未找到相关内容",
                })
              : T.jsxs("div", {
                  className: "space-y-3",
                  children: items.map((it, idx) => {
                    const title =
                      it.title || it.doc_id || it.id || it.source ||
                      "结果 " + (idx + 1);
                    const bodyText =
                      it.content || it.text || it.chunk || it.snippet || "";
                    return T.jsxs(
                      "div",
                      {
                        key: idx,
                        className:
                          "bg-white rounded-2xl border border-cream-200 p-4 shadow-sm",
                        children: [
                          T.jsxs("div", {
                            className: "flex items-center justify-between gap-3",
                            children: [
                              T.jsx("p", {
                                className: "text-sm font-medium text-foreground",
                                children: title,
                              }),
                              it.score != null &&
                                T.jsx("span", {
                                  className: "text-xs text-sunset-500 shrink-0",
                                  children:
                                    "相关度 " +
                                    Math.round(
                                      (it.score <= 1
                                        ? it.score
                                        : Math.min(1, it.score / 100)) * 100,
                                    ) +
                                    "%",
                                }),
                            ],
                          }),
                          bodyText &&
                            T.jsx("p", {
                              className:
                                "text-sm text-muted-foreground mt-2 leading-relaxed",
                              children: bodyText,
                            }),
                        ],
                      },
                      idx,
                    );
                  }),
                }),
      }),
    ],
  });
}
function WkFileUpload() {
  const [files, setFiles] = D.useState([]);
  const [uploading, setUploading] = D.useState(!1);
  const [results, setResults] = D.useState([]);
  const [err, setErr] = D.useState("");
  const pick = (e) => e.target.files && setFiles(Array.from(e.target.files));
  const run = async () => {
    if (files.length === 0) return;
    setUploading(!0);
    setErr("");
    setResults([]);
    try {
      const out = [];
      for (const f of files) {
        const r = await Yt.upload(f);
        if (r.ok) {
          const d = await r.json().catch(() => ({}));
          out.push({ name: f.name, ok: !0, msg: d.message || d.filename || "上传成功" });
        } else {
          out.push({ name: f.name, ok: !1, msg: "上传失败（" + r.status + "）" });
        }
      }
      setResults(out);
      setFiles([]);
    } catch {
      setErr("网络错误，请检查连接后重试");
    } finally {
      setUploading(!1);
    }
  };
  return T.jsxs("div", {
    className: "flex-1 flex flex-col min-w-0",
    children: [
      T.jsxs("div", {
        className: "p-6 pb-4 border-b border-cream-200",
        children: [
          T.jsx("h2", {
            className: "font-brand text-2xl text-foreground",
            children: "文件上传",
          }),
          T.jsx("p", {
            className: "text-sm text-muted-foreground mt-1",
            children: "上传课件 / 标准文档，供 AI 在对话中参考",
          }),
        ],
      }),
      T.jsx("div", {
        className: "flex-1 overflow-y-auto px-6 py-6",
        children: [
          T.jsxs("label", {
            className:
              "flex flex-col items-center justify-center gap-3 border-2 border-dashed border-cream-300 rounded-3xl p-10 cursor-pointer hover:border-sunset-400 transition-colors",
            children: [
              T.jsx(WkUpload, { className: "w-10 h-10 text-sunset-400" }),
              T.jsx("p", {
                className: "text-sm text-muted-foreground",
                children: "点击选择文件（支持多选）",
              }),
              T.jsx("input", {
                type: "file",
                multiple: !0,
                className: "hidden",
                onChange: pick,
              }),
            ],
          }),
          files.length > 0 &&
            T.jsxs("div", {
              className: "mt-4 space-y-2",
              children: [
                files.map((f, idx) =>
                  T.jsx("p", {
                    key: idx,
                    className: "text-sm text-muted-foreground",
                    children: f.name,
                  }),
                ),
                T.jsxs("button", {
                  onClick: run,
                  disabled: uploading,
                  className:
                    "px-5 py-2.5 rounded-2xl bg-sunset-500 hover:bg-sunset-600 disabled:opacity-40 text-white text-sm font-medium transition-all duration-200",
                  children: [uploading ? "上传中…" : "开始上传"],
                }),
              ],
            }),
          err &&
            T.jsx("p", { className: "text-sm text-red-400 mt-4", children: err }),
          results.length > 0 &&
            T.jsxs("div", {
              className: "mt-6 space-y-2",
              children: results.map((r, idx) =>
                T.jsx("p", {
                  key: idx,
                  className: Or("text-sm", r.ok ? "text-sunset-500" : "text-red-400"),
                  children: r.name + " — " + r.msg,
                }),
              ),
            }),
        ],
      }),
    ],
  });
}
function WkHomework() {
  const e = tc();
  const [text, setText] = D.useState("");
  const go = () => {
    wkPrefill = "请帮我解答这道题：\n" + (text.trim() ? text.trim() : "");
    e("/");
  };
  return T.jsxs("div", {
    className: "flex-1 flex flex-col min-w-0",
    children: [
      T.jsxs("div", {
        className: "p-6 pb-4 border-b border-cream-200",
        children: [
          T.jsx("h2", {
            className: "font-brand text-2xl text-foreground",
            children: "习题解答",
          }),
          T.jsx("p", {
            className: "text-sm text-muted-foreground mt-1",
            children: "粘贴题目，跳转到对话并自动带入，由 AI 分步解答",
          }),
        ],
      }),
      T.jsxs("div", {
        className: "flex-1 overflow-y-auto px-6 py-6",
        children: [
          T.jsx("textarea", {
            value: text,
            onChange: (e) => setText(e.target.value),
            placeholder:
              "在此粘贴要解答的习题，例如：\n某信道带宽 10MHz，SNR=20dB，求信道容量……",
            rows: 8,
            className:
              "w-full max-w-2xl rounded-2xl border border-cream-300 bg-white px-4 py-3 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:border-sunset-400 resize-none",
          }),
          T.jsx("div", {
            className: "mt-4",
            children: T.jsxs("button", {
              onClick: go,
              className:
                "px-5 py-2.5 rounded-2xl bg-sunset-500 hover:bg-sunset-600 text-white text-sm font-medium transition-all duration-200",
              children: [
                T.jsx(nw, { className: "w-4 h-4 inline mr-1.5" }),
                "去对话解答",
              ],
            }),
          }),
        ],
      }),
    ],
  });
}
function WkWorkPage() {
  const [v, setV] = D.useState("rag");
  return T.jsxs("div", {
    className: "flex h-screen overflow-hidden bg-cream-100",
    children: [
      T.jsx(Ww, { mode: "work", workView: v, onWorkView: setV }),
      T.jsxs("main", {
        className: "flex-1 flex flex-col min-w-0 bg-cream-50",
        children: [
          v === "rag"
            ? T.jsx(WkRagSearch, {})
            : v === "upload"
              ? T.jsx(WkFileUpload, {})
              : T.jsx(WkHomework, {}),
        ],
      }),
    ],
  });
}
