function Ww({ mode = "talk", sessions = [], activeId, onSelect, onCreate, onDelete }) {
  const navigate = tc();
  const chatActive = mode === "talk" || mode === "work";
  return T.jsxs("aside", {
    className: "w-64 flex flex-col h-full shrink-0 bg-gradient-to-b from-white via-white to-cream-50 border-r border-cream-200",
    children: [
      T.jsxs("div", {
        className: "p-4 border-b border-cream-200",
        children: [
          T.jsxs("div", {
            className: "flex items-center gap-2.5 mb-1",
            children: [
              T.jsx("div", {
                className: "w-8 h-8 rounded-xl bg-gradient-to-br from-sunset-400 to-lavender-500 flex items-center justify-center shadow-sm",
                children: T.jsx("span", { className: "text-white text-xs font-bold", children: "W" }),
              }),
              T.jsx("span", { className: "font-brand text-lg text-foreground", children: "WAgent" }),
            ],
          }),
          T.jsx("p", { className: "text-xs text-muted-foreground/60 pl-10", children: "Wireless AI Assistant" }),
        ],
      }),
      T.jsx("div", {
        className: "px-3 pt-3 pb-2",
        children: T.jsxs("div", {
          className: "grid gap-1 p-1 rounded-2xl bg-cream-100 border border-cream-200",
          style: { gridTemplateColumns: "repeat(3, minmax(0, 1fr))" },
          children: [
            T.jsx(WkChatModeSwitch, { mode }),
            T.jsx("button", {
              type: "button",
              onClick: () => navigate("/library"),
              className: Or(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                mode === "library" ? "bg-white shadow-sm text-sunset-600" : "text-muted-foreground hover:text-foreground",
              ),
              children: "资料库",
            }),
            T.jsx("button", {
              type: "button",
              onClick: () => navigate("/papers"),
              className: Or(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                mode === "papers" ? "bg-white shadow-sm text-sunset-600" : "text-muted-foreground hover:text-foreground",
              ),
              children: "速递",
            }),
          ],
        }),
      }),
      chatActive &&
        T.jsx("div", {
          className: "px-3 pt-2 pb-2",
          children: T.jsx("button", {
            type: "button",
            onClick: onCreate,
            className: "w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-2xl bg-accent hover:bg-orange-200 text-accent-foreground text-sm font-medium transition-all duration-200",
            children: "＋ 新对话",
          }),
        }),
      chatActive &&
        T.jsxs("div", {
          className: "flex-1 overflow-y-auto px-2",
          children: [
            sessions.length === 0 &&
              T.jsx("p", { className: "text-muted-foreground/40 text-xs text-center mt-12 leading-relaxed", children: "还没有对话" }),
            sessions.map((session) =>
              T.jsxs(
                "div",
                {
                  className: Or(
                    "group flex items-center gap-2 px-3 py-2.5 mb-1 rounded-2xl cursor-pointer transition-all duration-200",
                    session.id === activeId ? "bg-white shadow-sm border border-cream-200" : "hover:bg-white/60 border border-transparent",
                  ),
                  onClick: () => onSelect(session.id),
                  children: [
                    T.jsxs("div", {
                      className: "min-w-0 flex-1",
                      children: [
                        T.jsx("p", { className: "text-sm text-foreground truncate", children: session.title || "新对话" }),
                        T.jsx("p", { className: "text-[10px] text-muted-foreground/50 mt-0.5", children: jw(session.updated_at || session.created_at) }),
                      ],
                    }),
                    T.jsx("button", {
                      type: "button",
                      onClick: (event) => { event.stopPropagation(); onDelete(session.id); },
                      className: "w-5 h-5 rounded-lg text-muted-foreground/40 hover:text-red-400 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all",
                      "aria-label": "删除对话",
                      children: "×",
                    }),
                  ],
                },
                session.id,
              ),
            ),
          ],
        }),
      !chatActive && T.jsx("div", { className: "flex-1" }),
      T.jsxs("div", {
        className: "p-3 border-t border-cream-200 space-y-2",
        children: [
          T.jsx(WkUserPanel, {}),
          T.jsx("p", { className: "text-xs text-muted-foreground/30 text-center", children: "Powered by OpenClaw" }),
        ],
      }),
    ],
  });
}
