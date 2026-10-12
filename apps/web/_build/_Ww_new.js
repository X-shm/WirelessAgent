function Ww({
  mode = "chat",
  sessions = [],
  activeId,
  onSelect,
  onCreate,
  onDelete,
  workView = "rag",
  onWorkView,
}) {
  const e = tc();
  const toggle = (m) => (m === "chat" ? e("/") : e("/work"));
  const workItems = [
    { key: "rag", label: "标准检索", icon: WkSearch },
    { key: "upload", label: "文件上传", icon: WkUpload },
    { key: "homework", label: "习题解答", icon: nw },
  ];
  const body =
    mode === "chat"
      ? [
          T.jsx("div", {
            className: "px-3 pt-2 pb-2",
            children: T.jsxs("button", {
              onClick: onCreate,
              className:
                "w-full flex items-center gap-2 px-3 py-2.5 rounded-2xl bg-accent hover:bg-orange-200 text-accent-foreground text-sm font-medium transition-all duration-200",
              children: [T.jsx(ow, { className: "w-4 h-4" }), "New Chat"],
            }),
          }),
          T.jsxs("div", {
            className: "flex-1 overflow-y-auto px-2",
            children: [
              sessions.length === 0 &&
                T.jsx("p", {
                  className:
                    "text-muted-foreground/40 text-xs text-center mt-12 leading-relaxed",
                  children: "No conversations yet.",
                }),
              sessions.map((o) => {
                const l = o.id === activeId;
                return T.jsxs(
                  "div",
                  {
                    onClick: () => onSelect(o.id),
                    className: Or(
                      "flex items-center gap-2.5 px-3 py-2.5 mb-1 cursor-pointer group rounded-2xl transition-all duration-200",
                      l
                        ? "bg-white shadow-sm border border-cream-200"
                        : "hover:bg-white/60 border border-transparent",
                    ),
                    children: [
                      T.jsx(rw, {
                        className: Or(
                          "w-4 h-4 shrink-0",
                          l ? "text-sunset-500" : "text-muted-foreground/40",
                        ),
                      }),
                      T.jsxs("div", {
                        className: "flex-1 min-w-0",
                        children: [
                          T.jsx("p", {
                            className: Or(
                              "text-sm truncate font-medium",
                              l ? "text-foreground" : "text-muted-foreground",
                            ),
                            children: o.title,
                          }),
                          T.jsx("p", {
                            className: "text-xs text-muted-foreground/50",
                            children: jw(o.updated_at),
                          }),
                        ],
                      }),
                      T.jsx("button", {
                        onClick: (a) => {
                          a.stopPropagation();
                          onDelete(o.id);
                        },
                        className:
                          "p-1 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-50 transition-all text-muted-foreground/40 hover:text-red-400",
                        children: T.jsx(aw, { className: "w-3.5 h-3.5" }),
                      }),
                    ],
                  },
                  o.id,
                );
              }),
            ],
          }),
        ]
      : [
          T.jsxs("div", {
            className: "flex-1 overflow-y-auto px-2 pt-2",
            children: workItems.map((it) => {
              const Icon = it.icon;
              const active = workView === it.key;
              return T.jsxs(
                "button",
                {
                  key: it.key,
                  onClick: () => onWorkView(it.key),
                  className: Or(
                    "w-full flex items-center gap-2.5 px-3 py-2.5 mb-1 cursor-pointer rounded-2xl transition-all duration-200",
                    active
                      ? "bg-white shadow-sm border border-cream-200"
                      : "hover:bg-white/60 border border-transparent",
                  ),
                  children: [
                    T.jsx(Icon, {
                      className: Or(
                        "w-4 h-4 shrink-0",
                        active ? "text-sunset-500" : "text-muted-foreground/40",
                      ),
                    }),
                    T.jsx("span", {
                      className: Or(
                        "text-sm font-medium",
                        active ? "text-foreground" : "text-muted-foreground",
                      ),
                      children: it.label,
                    }),
                  ],
                },
                it.key,
              );
            }),
          }),
        ];
  return T.jsxs("aside", {
    className:
      "w-64 flex flex-col h-full shrink-0 bg-gradient-to-b from-white via-white to-cream-50 border-r border-cream-200",
    children: [
      T.jsxs("div", {
        className: "p-4 border-b border-cream-200",
        children: [
          T.jsxs("div", {
            className: "flex items-center gap-2.5 mb-1",
            children: [
              T.jsx("div", {
                className:
                  "w-8 h-8 rounded-xl bg-gradient-to-br from-sunset-400 to-lavender-500 flex items-center justify-center shadow-sm",
                children: T.jsx(xl, { className: "w-4.5 h-4.5 text-white" }),
              }),
              T.jsx("span", {
                className: "font-brand text-lg text-foreground",
                children: "WAgent",
              }),
            ],
          }),
          T.jsx("p", {
            className: "text-xs text-muted-foreground/60 pl-10",
            children: "Wireless AI Assistant",
          }),
        ],
      }),
      T.jsx("div", {
        className: "px-3 pt-3 pb-2",
        children: T.jsxs("div", {
          className:
            "grid grid-cols-2 gap-1 p-1 rounded-2xl bg-cream-100 border border-cream-200",
          children: [
            T.jsxs("button", {
              onClick: () => toggle("chat"),
              className: Or(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                mode === "chat"
                  ? "bg-white shadow-sm text-sunset-600"
                  : "text-muted-foreground hover:text-foreground",
              ),
              children: [T.jsx(rw, { className: "w-4 h-4" }), "对话"],
            }),
            T.jsxs("button", {
              onClick: () => toggle("work"),
              className: Or(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                mode === "work"
                  ? "bg-white shadow-sm text-sunset-600"
                  : "text-muted-foreground hover:text-foreground",
              ),
              children: [T.jsx(WkBriefcase, { className: "w-4 h-4" }), "工作"],
            }),
          ],
        }),
      }),
      ...body,
      T.jsxs("div", {
        className: "p-3 border-t border-cream-200 space-y-2",
        children: [
          T.jsx("a", {
            href: "/login",
            className:
              "block text-center text-xs text-muted-foreground/40 hover:text-sunset-500 transition-colors",
            children: "Login / Register",
          }),
          T.jsx("p", {
            className: "text-xs text-muted-foreground/30 text-center",
            children: "Powered by OpenClaw",
          }),
        ],
      }),
    ],
  });
}
