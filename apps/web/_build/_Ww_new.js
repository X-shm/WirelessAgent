function Ww({ mode = "talk", sessions = [], activeId, onSelect, onCreate, onDelete, projects = [], activeProjectId, onSelectProject, onCreateProject, onDeleteProject, onRenameProject, onPinProject, onRenameSession, onPinSession, onMoveSession }) {
  const navigate = tc();
  const chatActive = mode === "talk" || mode === "work";
  const [expanded, setExpanded] = D.useState({});
  const [projectMenu, setProjectMenu] = D.useState(null);
  const [sessionMenu, setSessionMenu] = D.useState(null);
  const [moveMenu, setMoveMenu] = D.useState(null);
  const workSessions = Array.isArray(sessions) ? sessions : [];
  const unassigned = workSessions.filter((s) => !s.project_id);

  const projectSessions = (id) => workSessions.filter((s) => s.project_id === id);

  const sessionRow = (session) =>
    T.jsxs("div", {
      className: "relative",
      children: [
        T.jsxs("div", {
          className: Or("group flex items-center gap-1 px-3 py-2.5 mb-1 rounded-2xl cursor-pointer transition-all duration-200", session.id === activeId ? "bg-white shadow-sm border border-cream-200" : "hover:bg-white/60 border border-transparent"),
          onClick: () => onSelect(session.id),
          children: [
            T.jsxs("div", { className: "min-w-0 flex-1", children: [T.jsx("p", { className: "text-sm text-foreground truncate", children: session.title || "新对话" }), T.jsx("p", { className: "text-[10px] text-muted-foreground/50 mt-0.5", children: jw(session.updated_at || session.created_at) })] }),
            T.jsx("button", { type: "button", onClick: (e) => { e.stopPropagation(); setSessionMenu(sessionMenu === session.id ? null : session.id); }, className: "w-5 h-5 rounded-lg text-muted-foreground/40 hover:bg-cream-100 hover:text-foreground opacity-0 group-hover:opacity-100 transition-all", children: "···" }),
          ],
        }),
        sessionMenu === session.id &&
          T.jsxs("div", {
            className: "absolute right-2 top-9 z-30 w-44 rounded-2xl border border-cream-200 bg-white p-1.5 shadow-xl",
            children: [
              T.jsx("button", { type: "button", onClick: () => { const name = window.prompt("重命名对话", session.title || ""); if (name && name.trim()) onRenameSession(session.id, name.trim()); setSessionMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-cream-100", children: "重命名" }),
              T.jsx("button", { type: "button", onClick: () => { onPinSession(session.id); setSessionMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-cream-100", children: "置顶 / 取消置顶" }),
              mode === "work" && T.jsx("button", { type: "button", onClick: () => { setMoveMenu(moveMenu === session.id ? null : session.id); setSessionMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-cream-100", children: "添加到项目" }),
              T.jsx("button", { type: "button", onClick: () => { onDelete(session.id); setSessionMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs text-red-400 hover:bg-red-50", children: "删除" }),
            ],
          }),
        moveMenu === session.id &&
          T.jsxs("div", { className: "absolute right-2 top-9 z-30 w-48 rounded-2xl border border-cream-200 bg-white p-1.5 shadow-xl", children: projects.map((project) => T.jsx("button", { type: "button", onClick: () => { onMoveSession(session.id, project.id); setMoveMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-cream-100 truncate", children: "移动到：" + project.name }, project.id)) }),
      ],
    }, session.id);

  return T.jsxs("aside", {
    className: "w-64 flex flex-col h-full shrink-0 bg-gradient-to-b from-white via-white to-cream-50 border-r border-cream-200",
    children: [
      T.jsxs("div", { className: "p-4 border-b border-cream-200", children: [T.jsxs("div", { className: "flex items-center gap-2.5 mb-1", children: [T.jsx("div", { className: "w-8 h-8 rounded-xl bg-gradient-to-br from-sunset-400 to-lavender-500 flex items-center justify-center shadow-sm", children: T.jsx("span", { className: "text-white text-xs font-bold", children: "W" }) }), T.jsx("span", { className: "font-brand text-lg text-foreground", children: "WAgent" })] }), T.jsx("p", { className: "text-xs text-muted-foreground/60 pl-10", children: "Wireless AI Assistant" })] }),
      T.jsx("div", { className: "px-3 pt-3 pb-2", children: T.jsxs("div", { className: "grid gap-1 p-1 rounded-2xl bg-cream-100 border border-cream-200", style: { gridTemplateColumns: "repeat(3, minmax(0, 1fr))" }, children: [T.jsx(WkChatModeSwitch, { mode }), T.jsx("button", { type: "button", onClick: () => navigate("/library"), className: Or("flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200", mode === "library" ? "bg-white shadow-sm text-sunset-600" : "text-muted-foreground hover:text-foreground"), children: "资料库" }), T.jsx("button", { type: "button", onClick: () => navigate("/papers"), className: Or("flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-all duration-200", mode === "papers" ? "bg-white shadow-sm text-sunset-600" : "text-muted-foreground hover:text-foreground"), children: "速递" })] }) }),
      chatActive && T.jsx("div", { className: "px-3 pt-2 pb-2", children: T.jsx("button", { type: "button", onClick: () => onCreate(mode === "work" ? activeProjectId : null), className: "w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-2xl bg-accent border border-orange-200 text-accent-foreground text-sm font-medium transition-all duration-200 hover:bg-orange-200", children: "＋ 新对话" }) }),
      mode === "work" && T.jsxs("div", { className: "flex-1 overflow-y-auto px-2", children: [
        T.jsxs("div", { className: "px-1 py-2 flex items-center justify-between", children: [T.jsx("p", { className: "text-xs font-medium text-muted-foreground", children: "项目" }), T.jsx("button", { type: "button", onClick: onCreateProject, className: "px-2.5 py-1.5 rounded-lg bg-white border border-cream-200 text-xs font-medium text-sunset-600 hover:bg-accent", children: "＋ 新建项目" })] }),
        T.jsxs("button", { type: "button", onClick: () => onSelectProject(null), className: Or("w-full text-left px-3 py-2 rounded-xl text-xs mb-1", !activeProjectId ? "bg-white border border-cream-200 text-foreground" : "text-muted-foreground hover:bg-white/60"), children: "未归档对话" }),
        unassigned.map(sessionRow),
        projects.map((project) => T.jsxs("div", { className: "relative", children: [
          T.jsxs("div", { className: Or("group flex items-center gap-1 px-3 py-2 rounded-xl text-xs mb-1 cursor-pointer", activeProjectId === project.id ? "bg-white border border-cream-200 text-foreground" : "text-muted-foreground hover:bg-white/60"), onClick: () => { setExpanded((p) => ({ ...p, [project.id]: !p[project.id] })); onSelectProject(project.id); }, children: [T.jsx("button", { type: "button", onClick: (e) => { e.stopPropagation(); setExpanded((p) => ({ ...p, [project.id]: !p[project.id] })); }, className: "shrink-0 text-xs", children: expanded[project.id] ? "▾" : "▸" }), T.jsx("span", { className: "truncate flex-1", children: project.name }), T.jsx("button", { type: "button", onClick: (e) => { e.stopPropagation(); onCreate(project.id); }, className: "shrink-0 text-sunset-600 hover:bg-accent rounded px-1", children: "＋" }), T.jsx("button", { type: "button", onClick: (e) => { e.stopPropagation(); setProjectMenu(projectMenu === project.id ? null : project.id); }, className: "shrink-0 text-muted-foreground/60 hover:text-foreground opacity-0 group-hover:opacity-100", children: "···" })] }),
          projectMenu === project.id && T.jsxs("div", { className: "absolute right-2 top-9 z-30 w-44 rounded-2xl border border-cream-200 bg-white p-1.5 shadow-xl", children: [T.jsx("button", { type: "button", onClick: () => { const name = window.prompt("重命名项目", project.name); if (name && name.trim()) onRenameProject(project.id, name.trim()); setProjectMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-cream-100", children: "重命名" }), T.jsx("button", { type: "button", onClick: () => { onPinProject(project.id, !project.pinned); setProjectMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-cream-100", children: project.pinned ? "取消置顶" : "置顶" }), T.jsx("button", { type: "button", onClick: () => { window.prompt("项目文件地址", "/projects/" + project.id); setProjectMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-cream-100", children: "查看文件地址" }), T.jsx("button", { type: "button", onClick: () => { if (window.confirm("确定删除项目吗？")) onDeleteProject(project.id); setProjectMenu(null); }, className: "w-full text-left px-3 py-2 rounded-lg text-xs text-red-400 hover:bg-red-50", children: "删除项目" })] }),
          expanded[project.id] && projectSessions(project.id).map(sessionRow),
        ] }, project.id)),
      ] }),
      mode === "talk" && T.jsx("div", { className: "flex-1 overflow-y-auto px-2", children: [workSessions.length === 0 ? T.jsx("p", { className: "text-muted-foreground/40 text-xs text-center mt-12", children: "还没有对话" }) : workSessions.map(sessionRow)] }),
      mode === "library" && T.jsx("div", { className: "flex-1" }),
      T.jsxs("div", { className: "p-3 border-t border-cream-200 space-y-2", children: [T.jsx(WkUserPanel, {}), T.jsx("p", { className: "text-xs text-muted-foreground/30 text-center", children: "Powered by OpenClaw" })] }),
    ],
  });
}
