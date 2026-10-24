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
  const [selected, setSelected] = D.useState([]);
  const [uploading, setUploading] = D.useState(!1);
  const [drag, setDrag] = D.useState(!1);
  const [libraryFiles, setLibraryFiles] = D.useState([]);
  const [loadingFiles, setLoadingFiles] = D.useState(!0);
  const [error, setError] = D.useState("");
  const [preview, setPreview] = D.useState(null);

  const loadFiles = D.useCallback(async () => {
    setLoadingFiles(!0);
    setError("");
    try {
      const response = await Yt.listFiles();
      if (!response.ok) throw new Error("无法读取资料库");
      const data = await response.json();
      setLibraryFiles(Array.isArray(data) ? data : []);
    } catch {
      setError("资料库加载失败，请稍后重试");
    } finally {
      setLoadingFiles(!1);
    }
  }, []);

  D.useEffect(() => { loadFiles(); }, [loadFiles]);

  const patchSelected = (id, patch) => {
    setSelected((prev) => prev.map((item) => (item.id === id ? { ...item, ...patch } : item)));
  };

  const add = (list) => {
    const incoming = Array.from(list || []);
    if (incoming.length === 0) return;
    setSelected((prev) => {
      const seen = new Set(prev.map((item) => item.file.name + ":" + item.file.size));
      const next = [];
      for (const file of incoming) {
        const key = file.name + ":" + file.size;
        if (seen.has(key)) continue;
        seen.add(key);
        next.push({ id: Date.now().toString(36) + "-" + Math.random().toString(36).slice(2), file, status: "ready", message: "等待上传" });
      }
      return [...prev, ...next];
    });
  };

  const upload = async () => {
    const pending = selected.filter((item) => item.status === "ready" || item.status === "error");
    if (pending.length === 0 || uploading) return;
    setUploading(!0);
    setError("");
    for (const item of pending) {
      patchSelected(item.id, { status: "uploading", message: "上传中…" });
      try {
        const response = await Yt.upload(item.file);
        if (response.ok) {
          patchSelected(item.id, { status: "success", message: "已上传" });
          await loadFiles();
        } else {
          patchSelected(item.id, { status: "error", message: "上传失败（" + response.status + "）" });
        }
      } catch {
        patchSelected(item.id, { status: "error", message: "网络错误，请重试" });
      }
    }
    setUploading(!1);
  };

  const removeLibraryFile = async (file) => {
    if (!window.confirm("确定删除“" + file.filename + "”吗？")) return;
    try {
      const response = await Yt.deleteFile(file.id);
      if (response.ok) setLibraryFiles((prev) => prev.filter((item) => item.id !== file.id));
      else setError("删除失败，请稍后重试");
    } catch {
      setError("删除失败，请稍后重试");
    }
  };

  const formatSize = (size) => {
    if (!size) return "0 B";
    if (size < 1024) return size + " B";
    if (size < 1024 * 1024) return (size / 1024).toFixed(1) + " KB";
    return (size / (1024 * 1024)).toFixed(1) + " MB";
  };
  const pendingCount = selected.filter((item) => item.status === "ready" || item.status === "error").length;
  const successCount = selected.filter((item) => item.status === "success").length;

  return T.jsxs("div", {
    className: "flex-1 flex flex-col min-w-0 h-full",
    children: [
      T.jsxs("div", {
        className: "p-6 pb-4 border-b border-cream-200",
        children: [
          T.jsx("h2", { className: "font-brand text-2xl text-foreground", children: "资料库" }),
          T.jsx("p", { className: "text-sm text-muted-foreground mt-1", children: "聊天中的附件和从本地上传的资料都会显示在这里" }),
        ],
      }),
      T.jsx("div", {
        className: "flex-1 overflow-y-auto px-4 pb-6 pt-4",
        children: T.jsxs("div", {
          className: "max-w-4xl mx-auto w-full flex flex-col gap-5",
          children: [
            T.jsxs("div", {
              className: "rounded-3xl border border-cream-300 bg-white p-4 shadow-sm",
              children: [
                T.jsx("p", { className: "text-sm font-medium text-foreground mb-3", children: "从本地上传资料" }),
                T.jsxs("div", {
                  className: Or("rounded-2xl bg-cream-50 px-4 py-4 text-center transition-colors", drag ? "bg-accent" : "bg-cream-50"),
                  onDragOver: (event) => { event.preventDefault(); setDrag(!0); },
                  onDragLeave: () => setDrag(!1),
                  onDrop: (event) => { event.preventDefault(); setDrag(!1); add(event.dataTransfer.files); },
                  children: [
                    T.jsxs("label", {
                      className: "inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-white border border-cream-300 text-sm font-medium text-foreground cursor-pointer hover:bg-accent transition-colors",
                      children: [
                        T.jsx(WkUpload, { className: "w-4 h-4 text-sunset-500" }),
                        "选择文件",
                        T.jsx("input", {
                          type: "file",
                          multiple: !0,
                          className: "hidden",
                          onChange: (event) => { add(event.target.files); event.target.value = ""; },
                        }),
                      ],
                    }),
                    T.jsx("p", { className: "text-xs text-muted-foreground mt-2", children: "支持拖拽、多选；上传完成后会立即出现在下方资料列表" }),
                  ],
                }),
                selected.length > 0 &&
                  T.jsxs("div", {
                    className: "space-y-2 mt-3",
                    children: [
                      selected.map((item) =>
                        T.jsxs("div", {
                          className: "flex items-center gap-2 rounded-2xl border border-cream-200 px-3 py-2",
                          children: [
                            T.jsx("p", { className: "text-xs text-foreground truncate flex-1", children: item.file.name }),
                            T.jsx("span", { className: Or("text-xs", item.status === "error" ? "text-red-400" : item.status === "success" ? "text-sunset-500" : "text-muted-foreground"), children: item.message }),
                            item.status !== "uploading" && T.jsx("button", { type: "button", onClick: () => setSelected((prev) => prev.filter((current) => current.id !== item.id)), className: "text-muted-foreground hover:text-foreground", children: "×" }),
                          ],
                        }, item.id),
                      ),
                      T.jsx("button", {
                        type: "button",
                        onClick: upload,
                        disabled: uploading || pendingCount === 0,
                        className: "px-4 py-2.5 rounded-2xl bg-sunset-500 hover:bg-sunset-600 disabled:opacity-40 text-white text-sm font-medium",
                        children: uploading ? "上传中…" : pendingCount > 0 ? "上传 " + pendingCount + " 个文件" : successCount > 0 ? "已上传" : "上传文件",
                      }),
                    ],
                  }),
                error && T.jsx("p", { className: "text-sm text-red-400 mt-3", children: error }),
              ],
            }),
            T.jsxs("div", {
              className: "rounded-3xl border border-cream-300 bg-white p-4 shadow-sm",
              children: [
                T.jsxs("div", {
                  className: "flex items-center justify-between gap-3 mb-3",
                  children: [
                    T.jsx("p", { className: "text-sm font-medium text-foreground", children: "全部资料" }),
                    T.jsxs("button", { type: "button", onClick: loadFiles, className: "text-xs text-sunset-600 hover:underline", children: ["刷新", loadingFiles ? "中…" : ""] }),
                  ],
                }),
                loadingFiles
                  ? T.jsx("p", { className: "text-sm text-muted-foreground text-center py-8", children: "正在加载…" })
                  : libraryFiles.length === 0
                    ? T.jsx("p", { className: "text-sm text-muted-foreground text-center py-8", children: "暂无资料，先上传一个文件吧" })
                    : T.jsx("div", {
                        className: "space-y-2",
                        children: libraryFiles.map((file) =>
                          T.jsxs("div", {
                            className: "flex items-center gap-3 rounded-2xl border border-cream-200 px-3 py-3",
                            children: [
                              T.jsxs("div", {
                                className: "min-w-0 flex-1",
                                children: [
                                  T.jsx("p", { className: "text-sm font-medium text-foreground truncate", children: file.filename }),
                                  T.jsx("p", { className: "text-xs text-muted-foreground mt-0.5", children: formatSize(file.size) + " · " + new Date(file.created_at).toLocaleString("zh-CN") }),
                                ],
                              }),
                              T.jsx("button", { type: "button", onClick: () => setPreview({ id: file.id, name: file.filename, content_type: file.content_type }), className: "px-3 py-1.5 rounded-xl bg-accent text-accent-foreground text-xs font-medium hover:bg-orange-200", children: "预览" }),
                              T.jsx("button", { type: "button", onClick: () => removeLibraryFile(file), className: "px-3 py-1.5 rounded-xl text-red-400 text-xs hover:bg-red-50", children: "删除" }),
                            ],
                          }, file.id),
                        ),
                      }),
              ],
            }),
          ],
        }),
      }),
      preview && T.jsx(WkPreviewModal, { file: preview, onClose: () => setPreview(null) }),
    ],
  });
}

function WkHomework({ onUse } = {}) {
  const navigate = tc();
  const [text, setText] = D.useState("");
  const submit = () => {
    const prompt = "请帮我解答这道题：\n" + (text.trim() ? text.trim() : "");
    if (onUse) {
      onUse(prompt);
      return;
    }
    Cu = prompt;
    navigate("/");
  };
  return T.jsxs("div", {
    className: "flex-1 flex flex-col min-w-0",
    children: [
      T.jsxs("div", {
        className: "p-6 pb-4 border-b border-cream-200",
        children: [
          T.jsx("h2", { className: "font-brand text-2xl text-foreground", children: "习题解答" }),
          T.jsx("p", { className: "text-sm text-muted-foreground mt-1", children: "粘贴题目后发送到工作对话，由 AI 分步解答" }),
        ],
      }),
      T.jsxs("div", {
        className: "flex-1 overflow-y-auto px-6 py-6",
        children: [
          T.jsx("textarea", {
            value: text,
            onChange: (event) => setText(event.target.value),
            placeholder: "在此粘贴要解答的习题，例如：\n某信道带宽 10MHz，SNR=20dB，求信道容量……",
            rows: 8,
            className: "w-full max-w-2xl rounded-2xl border border-cream-300 bg-white px-4 py-3 text-sm placeholder:text-muted-foreground/50 focus:outline-none resize-none",
          }),
          T.jsx("div", {
            className: "mt-4",
            children: T.jsx("button", {
              type: "button",
              onClick: submit,
              className: "px-5 py-2.5 rounded-2xl bg-sunset-500 hover:bg-sunset-600 text-white text-sm font-medium transition-all duration-200",
              children: "带入工作对话",
            }),
          }),
        ],
      }),
    ],
  });
}

function WkWorkPage() {
  return T.jsxs("div", {
    className: "flex h-screen overflow-hidden bg-cream-100",
    children: [
      T.jsx(Ww, { mode: "library" }),
      T.jsx("main", {
        className: "flex-1 flex flex-col min-w-0 bg-cream-50",
        children: T.jsx(WkFileUpload, {}),
      }),
    ],
  });
}