(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const API = '/api';
  const TOKEN_KEY = 'wa_preview_token_v2';
  const CONV_KEY = 'wa_preview_conversations_v2';
  const ACTIVE_KEY = 'wa_preview_active_v2';
  const PROJECT_KEY = 'wa_preview_projects_v1';
  const now = () => Date.now();
  const loadJSON = (key, fallback) => {
    try { const value = JSON.parse(localStorage.getItem(key)); return value ?? fallback; }
    catch (_) { return fallback; }
  };
  const state = {
    token: localStorage.getItem(TOKEN_KEY),
    conversations: loadJSON(CONV_KEY, []),
    active: loadJSON(ACTIVE_KEY, { chat: null, work: null }),
    projects: localStorage.getItem(PROJECT_KEY) === null ? [{ id: 'project-demo', title: '5G NR 标准调研', pinned: false, createdAt: now(), updatedAt: now() }] : loadJSON(PROJECT_KEY, []),
    activeProject: null,
    activeWorkspaceProject: null,
    projectsCollapsed: false,
    historyCollapsed: false,
    currentView: 'chat',
    secondaryMode: 'chat'
  };
  if (!Array.isArray(state.conversations)) state.conversations = [];
  if (!state.active || typeof state.active !== 'object') state.active = { chat: null, work: null };
  const modes = {
    chat: {
      view: $('#view-chat'), input: $('#view-chat textarea'), send: $('#view-chat .send'),
      messages: $('#chatMessages'), title: $('#chatConversationTitle'), menuBtn: $('#chatMenuBtn'), menu: $('#chatMenu')
    },
    work: {
      view: $('#view-work'), input: $('#view-work textarea'), send: $('#view-work .send'),
      messages: $('#workMessages'), title: $('#workConversationTitle'), menuBtn: $('#workMenuBtn'), menu: $('#workMenu')
    }
  };
  const ui = {
    sidebar: $('#sidebar'), secondary: $('#secondarySidebar'), secondaryTitle: $('#secondaryTitle'),
    secondarySub: $('.secondary-sub'), history: $('#historyList'), togglePrimary: $('#togglePrimary'),
    toggleSecondary: $('#toggleSecondary'), openSecondaryRail: $('#openSecondaryRail'), overlay: $('#mobileOverlay'),
    menuBtn: $('#menuBtn'), pageTitle: $('#pageTitle'), newChat: $('#newChatBtn'), projectSection: $('#projectSection'), projectList: $('#projectList'), newProjectBtn: $('#newProjectBtn'), historyLabel: $('#historyLabel'), toggleProjectsAll: $('#toggleProjectsAll'), toggleHistoryAll: $('#toggleHistoryAll')
  };
  function saveState() {
    localStorage.setItem(CONV_KEY, JSON.stringify(state.conversations));
    localStorage.setItem(ACTIVE_KEY, JSON.stringify(state.active));
  }
  function saveProjects() {
    localStorage.setItem(PROJECT_KEY, JSON.stringify(state.projects));
  }
  function renderProjectDetail(projectId) {
    const project = state.projects.find(item => item.id === projectId);
    if (!project) { show('workspace'); return; }
    state.activeProject = project.id;
    const title = $('#projectDetailTitle');
    const desc = $('#projectDetailDesc');
    const count = $('#projectConvCount');
    const updated = $('#projectUpdatedAt');
    const list = $('#projectConversationList');
    if (title) title.textContent = project.title;
    if (desc) desc.textContent = '项目下的工作对话、文件和任务会集中在这里。';
    const conversations = state.conversations
      .filter(conv => conv.mode === 'work' && conv.projectId === project.id && conv.messages.length > 0)
      .sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.updatedAt - a.updatedAt);
    if (count) count.textContent = conversations.length + ' 个对话';
    if (updated) updated.textContent = '更新于 ' + formatTime(project.updatedAt);
    if (!list) return;
    list.innerHTML = '';
    if (!conversations.length) {
      const empty = document.createElement('div');
      empty.className = 'workspace-empty';
      empty.textContent = '这个项目下还没有对话，请点击项目旁的 + 新建。';
      list.appendChild(empty);
      return;
    }
    conversations.forEach(conv => {
      const row = document.createElement('div');
      row.className = 'project-detail-row';
      const main = document.createElement('div');
      main.className = 'project-detail-main';
      const name = document.createElement('div');
      name.className = 'project-detail-title';
      name.textContent = (conv.pinned ? '📌 ' : '') + conv.title;
      const meta = document.createElement('div');
      meta.className = 'project-detail-meta';
      meta.textContent = (conv.messages.length) + ' 条消息 · ' + formatTime(conv.updatedAt);
      main.appendChild(name);
      main.appendChild(meta);
      const open = document.createElement('button');
      open.className = 'project-detail-open';
      open.textContent = '继续对话';
      open.addEventListener('click', () => {
        state.active.work = conv.id;
        saveState();
        show('work');
      });
      row.appendChild(main);
      row.appendChild(open);
      list.appendChild(row);
    });
  }
  function showProject(projectId) {
    show('project');
    renderProjectDetail(projectId);
  }
    function renderWorkspace() {
    const list = $('#workspaceProjectList');
    const count = $('#workspaceProjectCount');
    const detail = $('#workspaceProjectDetail');
    if (!list || !detail) return;
    const projects = [...state.projects].sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.updatedAt - a.updatedAt);
    if (count) count.textContent = projects.length + ' 个项目';
    list.innerHTML = '';
    detail.innerHTML = '';
    if (!projects.length) {
      const empty = document.createElement('div');
      empty.className = 'workspace-empty';
      empty.textContent = '还没有项目。请在工作次侧栏中新建项目。';
      list.appendChild(empty);
      detail.style.display = 'none';
      return;
    }
    detail.style.display = 'block';
    let selected = projects.find(project => project.id === state.activeWorkspaceProject) || projects[0];
    state.activeWorkspaceProject = selected.id;
    projects.forEach(project => {
      const row = document.createElement('div');
      row.className = 'workspace-project-row' + (project.id === selected.id ? ' active' : '');
      const icon = document.createElement('div');
      icon.className = 'workspace-project-icon';
      icon.textContent = '项';
      const info = document.createElement('div');
      info.className = 'workspace-project-info';
      const title = document.createElement('div');
      title.className = 'workspace-project-title';
      title.textContent = (project.pinned ? '📌 ' : '') + project.title;
      const meta = document.createElement('div');
      meta.className = 'workspace-project-meta';
      const convCount = state.conversations.filter(conv => conv.mode === 'work' && conv.projectId === project.id).length;
      meta.textContent = convCount + ' 个对话 · ' + formatTime(project.updatedAt);
      info.appendChild(title);
      info.appendChild(meta);
      const view = document.createElement('button');
      view.className = 'workspace-project-open';
      view.textContent = '详情';
      view.addEventListener('click', () => {
        state.activeWorkspaceProject = project.id;
        renderWorkspace();
        detail.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      });
      row.appendChild(icon);
      row.appendChild(info);
      row.appendChild(view);
      list.appendChild(row);
    });
    const conversations = state.conversations
      .filter(conv => conv.mode === 'work' && conv.projectId === selected.id)
      .sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.updatedAt - a.updatedAt);
    const projectFiles = selected.files || [];
    const generatedFiles = selected.conversationFiles || [];
    const head = document.createElement('div');
    head.className = 'workspace-detail-head';
    head.innerHTML = '<div><div class="workspace-detail-title">' + escapeHtml((selected.pinned ? '📌 ' : '') + selected.title) + '</div><div class="workspace-detail-sub">项目文件与相关数据 · 更新于 ' + formatTime(selected.updatedAt) + '</div></div><span class="workspace-detail-badge">项目数据</span>';
    const grid = document.createElement('div');
    grid.className = 'workspace-detail-grid';
    grid.innerHTML = '<div class="workspace-detail-stat"><strong>' + conversations.length + '</strong><span>关联对话</span></div><div class="workspace-detail-stat"><strong>' + projectFiles.length + '</strong><span>项目文件</span></div>';
    const files = document.createElement('div');
    files.className = 'workspace-detail-section';
    const filesHead = document.createElement('div');
    filesHead.className = 'workspace-detail-section-head';
    filesHead.innerHTML = '<h4>项目文件</h4>';
    const addFile = document.createElement('button');
    addFile.className = 'workspace-add-file';
    addFile.textContent = '添加文件';
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.multiple = true;
    fileInput.style.display = 'none';
    addFile.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
      if (!selected.files) selected.files = [];
      [...fileInput.files].forEach(file => {
        selected.files.push({ id: 'file-' + crypto.randomUUID(), name: file.name, size: file.size, type: file.type || '未知类型', addedAt: now() });
      });
      selected.updatedAt = now();
      saveProjects();
      renderWorkspace();
    });
    filesHead.appendChild(addFile);
    files.appendChild(filesHead);
    files.appendChild(fileInput);
    if (!projectFiles.length) {
      const empty = document.createElement('div');
      empty.className = 'workspace-detail-empty';
      empty.textContent = '当前项目暂无文件。可添加本地文件，用于项目内工作引用。';
      files.appendChild(empty);
    } else {
      projectFiles.forEach(file => {
        const row = document.createElement('div');
        row.className = 'workspace-file-row';
        const type = document.createElement('div');
        type.className = 'workspace-file-type';
        type.textContent = (file.name.split('.').pop() || 'FILE').slice(0, 4).toUpperCase();
        const info = document.createElement('div');
        info.style.minWidth = '0';
        info.style.flex = '1';
        const name = document.createElement('div');
        name.className = 'workspace-file-name';
        name.textContent = file.name;
        const meta = document.createElement('div');
        meta.className = 'workspace-file-meta';
        meta.textContent = formatBytes(file.size) + ' · ' + formatTime(file.addedAt);
        info.appendChild(name);
        info.appendChild(meta);
        row.appendChild(type);
        row.appendChild(info);
        files.appendChild(row);
      });
    }
    const data = document.createElement('div');
    data.className = 'workspace-detail-section';
    const dataHead = document.createElement('div');
    dataHead.className = 'workspace-detail-section-head';
    dataHead.innerHTML = '<h4>对话数据</h4>';
    data.appendChild(dataHead);
    if (!generatedFiles.length) {
      const empty = document.createElement('div');
      empty.className = 'workspace-detail-empty';
      empty.textContent = '对话产生的文件会保存在这里。当前暂无对话文件。';
      data.appendChild(empty);
    } else {
      generatedFiles.forEach(file => {
        const row = document.createElement('div');
        row.className = 'workspace-file-row';
        const type = document.createElement('div');
        type.className = 'workspace-file-type';
        type.textContent = 'OUT';
        const name = document.createElement('div');
        name.className = 'workspace-file-name';
        name.textContent = file.name;
        row.appendChild(type);
        row.appendChild(name);
        data.appendChild(row);
      });
    }
    detail.appendChild(head);
    detail.appendChild(grid);
    detail.appendChild(files);
    detail.appendChild(data);
  }
    function renderProjects() {
    renderWorkspace();
    const isWork = state.currentView === 'work';
    ui.projectSection.classList.toggle('hidden', !isWork);
    if (!isWork) return;
    if (ui.toggleProjectsAll) ui.toggleProjectsAll.setAttribute('aria-expanded', String(!state.projectsCollapsed));
    ui.projectList.classList.toggle('hidden', state.projectsCollapsed);
    ui.projectList.innerHTML = '';
    const projects = [...state.projects].sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.updatedAt - a.updatedAt);
    if (!projects.length) {
      const empty = document.createElement('div');
      empty.className = 'project-empty';
      empty.textContent = '还没有项目';
      ui.projectList.appendChild(empty);
      return;
    }
    projects.forEach(project => {
      const row = document.createElement('div');
      row.className = 'project-row' + (state.activeProject === project.id ? ' active' : '') + (project.collapsed ? ' project-collapsed' : '');
      const toggle = document.createElement('button');
      toggle.className = 'project-toggle';
      toggle.title = project.collapsed ? '展开项目对话' : '收起项目对话';
      toggle.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>';
      toggle.addEventListener('click', event => {
        event.stopPropagation();
        project.collapsed = !project.collapsed;
        saveProjects();
        renderProjects();
      });
      const main = document.createElement('button');
      main.className = 'project-main';
      main.title = project.title;
      main.textContent = (project.pinned ? '📌 ' : '') + project.title;
      main.addEventListener('click', () => {
        state.activeProject = project.id;
        renderProjects();
      });
      const add = document.createElement('button');
      add.className = 'project-add';
      add.title = '在项目下新建对话';
      add.textContent = '＋';
      add.addEventListener('click', event => {
        event.stopPropagation();
        startNewConversation('work', project.id);
      });
      const menuBtn = document.createElement('button');
      menuBtn.className = 'project-menu-btn';
      menuBtn.title = '项目设置';
      menuBtn.textContent = '•••';
      const menu = document.createElement('div');
      menu.className = 'project-menu';
      menu.innerHTML = '<button data-project-action="rename">编辑名称</button><button data-project-action="pin">' + (project.pinned ? '取消置顶' : '置顶') + '</button><button data-project-action="delete">删除</button>';
      menuBtn.addEventListener('click', event => {
        event.stopPropagation();
        closeMenus();
        menu.classList.add('open');
      });
      menu.addEventListener('click', event => {
        const action = event.target.dataset.projectAction;
        if (!action) return;
        if (action === 'rename') {
          const value = prompt('编辑项目名称', project.title);
          if (value !== null && value.trim()) {
            project.title = value.trim();
            project.updatedAt = now();
            saveProjects();
          }
        }
        if (action === 'pin') {
          project.pinned = !project.pinned;
          saveProjects();
        }
        if (action === 'delete' && confirm('确定删除这个项目吗？项目下的对话会移到普通对话中。')) {
          state.projects = state.projects.filter(item => item.id !== project.id);
          state.conversations.forEach(conv => { if (conv.projectId === project.id) conv.projectId = null; });
          if (state.activeProject === project.id) state.activeProject = null;
          saveProjects();
          saveState();
          renderHistory('work');
        }
        closeMenus();
        renderProjects();
      });
      row.appendChild(toggle);
      row.appendChild(main);
      row.appendChild(add);
      row.appendChild(menuBtn);
      row.appendChild(menu);
      ui.projectList.appendChild(row);
      const conversations = state.conversations
        .filter(conv => conv.mode === 'work' && conv.projectId === project.id && (conv.messages.length > 0 || conv.id === state.active.work))
        .sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.updatedAt - a.updatedAt);
      const tree = document.createElement('div');
      tree.className = 'project-conversations';
      if (!conversations.length) {
        const empty = document.createElement('div');
        empty.className = 'project-empty';
        empty.textContent = '暂无对话';
        tree.appendChild(empty);
      } else {
        conversations.forEach(conv => tree.appendChild(createSidebarConversationRow(conv, 'work', 'project-conversation-row', 'project-conversation-main', 'conversation-side-menu-btn')));
      }
      ui.projectList.appendChild(tree);
    });
  }
    function activeConversation(mode) {
    const id = state.active[mode];
    return state.conversations.find(item => item.id === id) || null;
  }
  function truncate(text, length = 28) {
    return text.length > length ? text.slice(0, length) + '…' : text;
  }
  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
  }
  function renderText(text) {
    return escapeHtml(text).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
  }
  function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    return (bytes / Math.pow(1024, index)).toFixed(index ? 1 : 0) + ' ' + units[index];
  }
    function formatTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const today = new Date();
    const hm = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
    return date.toDateString() === today.toDateString() ? hm : (date.getMonth() + 1) + '/' + date.getDate() + ' ' + hm;
  }
  function appendMessage(container, message, options = {}) {
    const row = document.createElement('div');
    row.className = 'message ' + message.role;
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = message.role === 'user' ? '你' : 'W';
    const content = document.createElement('div');
    content.className = 'message-content';
    let status = null;
    if (message.role === 'assistant' && options.statusText) {
      status = document.createElement('div');
      status.className = 'message-status';
      status.textContent = options.statusText;
      content.appendChild(status);
    }
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    if (message.role === 'assistant' && options.thinking) bubble.classList.add('thinking');
    bubble.innerHTML = renderText(message.content || '');
    content.appendChild(bubble);
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = formatTime(message.time);
    content.appendChild(time);
    row.appendChild(avatar);
    row.appendChild(content);
    container.appendChild(row);
    container.classList.add('has-messages');
    return { row, bubble, status, time };
  }
  function renderMode(mode) {
    const cfg = modes[mode];
    const conv = activeConversation(mode);
    cfg.title.textContent = conv ? conv.title : '新对话';
    cfg.menuBtn.disabled = !conv;
    cfg.messages.innerHTML = '';
    if (conv && conv.messages.length) {
      cfg.view.classList.add('chatting');
      conv.messages.forEach(message => appendMessage(cfg.messages, message));
      cfg.messages.classList.add('has-messages');
    } else {
      cfg.view.classList.remove('chatting');
      cfg.messages.classList.remove('has-messages');
    }
    updateMenuLabel(mode);
  }
  function createSidebarConversationRow(conv, mode, rowClass, mainClass, menuClass) {
    const row = document.createElement('div');
    row.className = rowClass + (conv.id === state.active[mode] ? ' active' : '');
    const main = document.createElement('button');
    main.className = mainClass;
    main.title = conv.title;
    if (rowClass === 'history-row') {
      const title = document.createElement('span');
      title.className = 'history-title';
      title.textContent = (conv.pinned ? '📌 ' : '') + conv.title;
      const meta = document.createElement('span');
      meta.className = 'history-meta';
      meta.textContent = formatTime(conv.updatedAt);
      main.appendChild(title);
      main.appendChild(meta);
    } else {
      main.textContent = (conv.pinned ? '📌 ' : '') + conv.title;
    }
    main.addEventListener('click', () => {
      state.active[mode] = conv.id;
      saveState();
      show(mode);
    });
    const menuBtn = document.createElement('button');
    menuBtn.className = menuClass;
    menuBtn.title = '对话设置';
    menuBtn.textContent = '•••';
    const menu = document.createElement('div');
    menu.className = 'project-menu';
    menu.innerHTML = '<button data-conversation-action="rename">编辑对话</button><button data-conversation-action="pin">' + (conv.pinned ? '取消置顶' : '置顶') + '</button><button data-conversation-action="delete">删除</button>';
    menuBtn.addEventListener('click', event => {
      event.stopPropagation();
      closeMenus();
      menu.classList.add('open');
    });
    menu.addEventListener('click', event => {
      const action = event.target.dataset.conversationAction;
      if (!action) return;
      if (action === 'rename') {
        const value = prompt('编辑对话名称', conv.title);
        if (value !== null && value.trim()) {
          conv.title = value.trim();
          conv.updatedAt = now();
          saveState();
        }
      }
      if (action === 'pin') {
        conv.pinned = !conv.pinned;
        saveState();
      }
      if (action === 'delete' && confirm('确定删除这个对话吗？')) {
        state.conversations = state.conversations.filter(item => item.id !== conv.id);
        if (state.active[mode] === conv.id) state.active[mode] = null;
        saveState();
        if (conv.sessionId && state.token) {
          fetch(API + '/sessions/' + conv.sessionId, { method: 'DELETE', headers: { Authorization: 'Bearer ' + state.token } }).catch(() => {});
        }
      }
      closeMenus();
      renderMode(mode);
      renderHistory(mode);
      renderProjects();
    });
    row.appendChild(main);
    row.appendChild(menuBtn);
    row.appendChild(menu);
    return row;
  }
  function renderHistory(mode) {
    if (ui.secondaryTitle) ui.secondaryTitle.textContent = mode === 'chat' ? '对话' : '工作';
    if (ui.secondarySub) ui.secondarySub.textContent = mode === 'chat' ? '对话记录' : '工作记录';
    if (ui.historyLabel) ui.historyLabel.textContent = '对话';
    if (ui.toggleHistoryAll) ui.toggleHistoryAll.setAttribute('aria-expanded', String(!state.historyCollapsed));
    if (ui.history) ui.history.classList.toggle('hidden', state.historyCollapsed);
    const list = ui.history;
    if (!list) return;
    list.innerHTML = '';
    const items = state.conversations
      .filter(item => item.mode === mode && (mode === 'chat' || !item.projectId) && (item.messages.length > 0 || item.id === state.active[mode]))
      .sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.updatedAt - a.updatedAt);
    if (!items.length) {
      const empty = document.createElement('div');
      empty.className = 'history-empty';
      empty.textContent = '还没有对话';
      list.appendChild(empty);
      return;
    }
    items.forEach(conv => list.appendChild(createSidebarConversationRow(conv, mode, 'history-row', 'history-entry', 'history-menu-btn')));
  }
    function updateMenuLabel(mode) {
    const conv = activeConversation(mode);
    const pin = modes[mode].menu.querySelector('[data-action="pin"]');
    if (pin) pin.textContent = conv && conv.pinned ? '取消置顶' : '置顶';
  }
  async function ensureToken(force = false) {
    if (force) { state.token = null; localStorage.removeItem(TOKEN_KEY); }
    if (state.token) return state.token;
    const res = await fetch(API + '/auth/guest', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
    if (!res.ok) throw new Error('游客登录失败');
    const data = await res.json();
    state.token = data.access_token;
    localStorage.setItem(TOKEN_KEY, state.token);
    return state.token;
  }
  async function createServerSession() {
    await ensureToken();
    let res = await fetch(API + '/sessions/', { method: 'POST', headers: { Authorization: 'Bearer ' + state.token, 'Content-Type': 'application/json' }, body: '{}' });
    if (res.status === 401) {
      await ensureToken(true);
      res = await fetch(API + '/sessions/', { method: 'POST', headers: { Authorization: 'Bearer ' + state.token, 'Content-Type': 'application/json' }, body: '{}' });
    }
    if (!res.ok) throw new Error('创建会话失败');
    return (await res.json()).id;
  }
  async function ensureConversationSession(conv) {
    if (conv.sessionId) return conv.sessionId;
    const sessionId = await createServerSession();
    const oldId = conv.id;
    conv.id = sessionId;
    conv.sessionId = sessionId;
    ['chat', 'work'].forEach(mode => { if (state.active[mode] === oldId) state.active[mode] = sessionId; });
    saveState();
    return sessionId;
  }
  function setActiveNav(name) {
    $$('.nav-item').forEach(item => {
      const nav = item.dataset.nav;
      const active = nav === name || (name === 'papers' && nav === 'functions') || (name === 'project' && nav === 'workspace');
      item.classList.toggle('active', active);
    });
  }
  function setPrimaryCollapsed(collapsed) {
    document.body.classList.toggle('sidebar-collapsed', collapsed);
    ui.togglePrimary.title = collapsed ? '展开主侧栏' : '收起主侧栏';
    ui.togglePrimary.setAttribute('aria-pressed', String(!collapsed));
  }
  function syncOverlay() {
    const mobileOpen = innerWidth <= 900 && (ui.sidebar.classList.contains('open') || ui.secondary.classList.contains('open'));
    ui.overlay.classList.toggle('open', mobileOpen);
  }
  function setSecondaryOpen(open) {
    const conversationView = state.currentView === 'chat' || state.currentView === 'work';
    if (!conversationView) {
      ui.secondary.classList.add('hidden');
      ui.secondary.classList.remove('collapsed', 'open');
      syncOverlay();
      return;
    }
    ui.secondary.classList.remove('hidden');
    ui.secondary.classList.toggle('collapsed', !open);
    ui.secondary.classList.toggle('open', open && innerWidth <= 900);
    ui.toggleSecondary.title = open ? '收起对话侧栏' : '打开对话侧栏';
    ui.toggleSecondary.setAttribute('aria-pressed', String(open));
    syncOverlay();
  }
  function show(name) {
    state.currentView = name;
    renderProjects();
    const titles = { chat: '对话', work: '工作', functions: '功能', papers: '论文速递', settings: '设置', appearance: '外观', login: '登录', library: '资料库', workspace: '工作空间', project: '项目' };
    const viewName = name;
    $$('.view').forEach(view => view.classList.toggle('active', view.id === 'view-' + viewName));
    ui.pageTitle.textContent = titles[name] || 'WirelessAgent';
    setActiveNav(name);
    const conversationView = name === 'chat' || name === 'work';
    if (conversationView) {
      state.secondaryMode = name;
      renderHistory(name);
      renderMode(name);
      setPrimaryCollapsed(true);
      setSecondaryOpen(true);
    } else {
      setSecondaryOpen(false);
      setPrimaryCollapsed(false);
    }
    ui.sidebar.classList.remove('open');
    syncOverlay();
    $('.main-scroll').scrollTop = 0;
  }
  function startNewConversation(mode, projectId = null) {
    show(mode);
    const existing = activeConversation(mode);
    if (existing && existing.messages.length === 0 && (existing.projectId || null) === projectId) {
      modes[mode].input.focus();
      return;
    }
    const conv = {
      id: 'draft-' + crypto.randomUUID(), sessionId: null, mode, title: '新对话',
      projectId: mode === 'work' ? projectId : null,
      pinned: false, createdAt: now(), updatedAt: now(), messages: []
    };
    state.conversations.push(conv);
    state.active[mode] = conv.id;
    if (projectId) {
      const project = state.projects.find(item => item.id === projectId);
      if (project) { project.collapsed = false; saveProjects(); }
    }
    saveState();
    renderMode(mode);
    renderHistory(mode);
    renderProjects();
    modes[mode].input.focus();
  }
  function closeMenus() {
    Object.values(modes).forEach(cfg => cfg.menu.classList.remove('open'));
    $$('.project-menu').forEach(menu => menu.classList.remove('open'));
  }
  function setupConversationMenu(mode) {
    const cfg = modes[mode];
    cfg.menuBtn.addEventListener('click', event => {
      event.stopPropagation();
      closeMenus();
      if (!cfg.menuBtn.disabled) cfg.menu.classList.add('open');
    });
    cfg.menu.addEventListener('click', async event => {
      const action = event.target.dataset.action;
      if (!action) return;
      const conv = activeConversation(mode);
      if (!conv) return;
      if (action === 'rename') {
        const value = prompt('编辑对话名称', conv.title);
        if (value !== null && value.trim()) {
          conv.title = value.trim();
          conv.updatedAt = now();
          saveState();
          renderMode(mode);
          renderHistory(mode);
          renderProjects();
        }
      }
      if (action === 'pin') {
        conv.pinned = !conv.pinned;
        saveState();
        updateMenuLabel(mode);
        renderHistory(mode);
        renderProjects();
      }
      if (action === 'delete') {
        if (confirm('确定删除这个对话吗？')) {
          const sessionId = conv.sessionId;
          state.conversations = state.conversations.filter(item => item.id !== conv.id);
          state.active[mode] = null;
          saveState();
          renderMode(mode);
          renderHistory(mode);
          renderProjects();
          if (sessionId && state.token) {
            fetch(API + '/sessions/' + sessionId, { method: 'DELETE', headers: { Authorization: 'Bearer ' + state.token } }).catch(() => {});
          }
        }
      }
      closeMenus();
    });
  }
  async function sendMessage(mode) {
    const cfg = modes[mode];
    const text = cfg.input.value.trim();
    if (!text || cfg.send.disabled) return;
    if (!activeConversation(mode)) startNewConversation(mode);
    let conv = activeConversation(mode);
    if (!conv) return;
    cfg.send.disabled = true;
    cfg.input.value = '';
    if (conv.title === '新对话') conv.title = truncate(text, 28);
    const userMessage = { role: 'user', content: text, time: now() };
    conv.messages.push(userMessage);
    conv.updatedAt = userMessage.time;
    saveState();
    cfg.view.classList.add('chatting');
    cfg.messages.classList.add('has-messages');
    appendMessage(cfg.messages, userMessage);
    cfg.title.textContent = conv.title;
    cfg.menuBtn.disabled = false;
    renderHistory(mode);
    renderProjects();
    const live = appendMessage(cfg.messages, { role: 'assistant', content: '正在思考…', time: null }, { statusText: '思考中', thinking: true });
    const startedAt = performance.now();
    let answer = '';
    let finished = false;
    const seconds = () => ((performance.now() - startedAt) / 1000).toFixed(1);
    const setStatus = label => { live.status.innerHTML = label + ' · <span class="elapsed">' + seconds() + 's</span>'; };
    const timer = setInterval(() => setStatus(answer ? '正在回复' : '思考中'), 100);
    const finish = label => {
      if (finished) return;
      finished = true;
      clearInterval(timer);
      setStatus(label);
      live.time.textContent = formatTime(now());
    };
    cfg.messages.scrollTop = cfg.messages.scrollHeight;
    try {
      await ensureConversationSession(conv);
      let res = await fetch(API + '/chat/stream', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + state.token, 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: conv.sessionId, message: text })
      });
      if (res.status === 401) {
        await ensureToken(true);
        const newSession = await createServerSession();
        const oldId = conv.id;
        conv.id = newSession;
        conv.sessionId = newSession;
        if (state.active[mode] === oldId) state.active[mode] = newSession;
        saveState();
        res = await fetch(API + '/chat/stream', {
          method: 'POST',
          headers: { Authorization: 'Bearer ' + state.token, 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: conv.sessionId, message: text })
        });
      }
      if (!res.ok || !res.body) throw new Error('对话接口不可用');
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data:')) continue;
          const payload = trimmed.slice(5).trim();
          if (!payload) continue;
          try {
            const item = JSON.parse(payload);
            if (item.token) {
              answer += item.token;
              live.bubble.classList.remove('thinking');
              live.bubble.innerHTML = renderText(answer);
              setStatus('正在回复');
              live.bubble.scrollIntoView({ block: 'end', behavior: 'smooth' });
            }
            if (item.error) {
              answer += (answer ? '\n\n' : '') + '⚠️ ' + item.error;
              live.bubble.classList.remove('thinking');
              live.bubble.innerHTML = renderText(answer);
              finish('回复失败');
            }
          } catch (_) {}
        }
      }
      if (answer) {
        const assistantMessage = { role: 'assistant', content: answer, time: now() };
        conv.messages.push(assistantMessage);
        conv.updatedAt = assistantMessage.time;
        saveState();
        live.time.textContent = formatTime(assistantMessage.time);
        finish('思考已完成');
        renderHistory(mode);
        renderProjects();
      } else {
        live.bubble.classList.remove('thinking');
        live.bubble.innerHTML = '⚠️ 未收到回复，请稍后重试。';
        finish('未收到回复');
      }
    } catch (error) {
      console.error(error);
      live.bubble.classList.remove('thinking');
      live.bubble.innerHTML = '⚠️ 对话服务暂时不可用，请稍后重试。';
      finish('回复失败');
    } finally {
      clearInterval(timer);
      cfg.send.disabled = false;
      cfg.input.focus();
    }
  }
  $$('[data-nav]').forEach(el => el.addEventListener('click', event => {
    event.preventDefault();
    show(el.dataset.nav);
  }));
  $$('[data-function]').forEach(el => el.addEventListener('click', () => {
    show('work');
    const chip = $('#workFeature');
    if (chip) chip.textContent = '当前功能：' + el.dataset.function;
    const input = modes.work.input;
    input.value = { '习题解答': '请帮我解答这道题：', '标准检索': '请帮我检索相关标准：' }[el.dataset.function] || '';
    input.focus();
  }));
  $$('#view-chat .prompt').forEach(button => button.addEventListener('click', () => {
    modes.chat.input.value = button.textContent.trim();
    sendMessage('chat');
  }));
  Object.keys(modes).forEach(mode => {
    const cfg = modes[mode];
    cfg.send.addEventListener('click', () => sendMessage(mode));
    cfg.input.addEventListener('keydown', event => {
      if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); sendMessage(mode); }
    });
    setupConversationMenu(mode);
  });
  ui.newChat.addEventListener('click', () => startNewConversation(state.currentView === 'work' ? 'work' : 'chat'));
  ui.toggleProjectsAll.addEventListener('click', () => {
    state.projectsCollapsed = !state.projectsCollapsed;
    renderProjects();
  });
  ui.toggleHistoryAll.addEventListener('click', () => {
    state.historyCollapsed = !state.historyCollapsed;
    renderHistory(state.secondaryMode);
  });  ui.newProjectBtn.addEventListener('click', () => {
    const value = prompt('新建项目名称', '');
    if (value !== null && value.trim()) {
      const project = { id: 'project-' + crypto.randomUUID(), title: value.trim(), pinned: false, createdAt: now(), updatedAt: now() };
      state.projects.push(project);
      state.activeProject = project.id;
      saveProjects();
      renderProjects();
    }
  });
  ui.togglePrimary.addEventListener('click', () => setPrimaryCollapsed(!document.body.classList.contains('sidebar-collapsed')));
  ui.toggleSecondary.addEventListener('click', () => setSecondaryOpen(false));
  ui.openSecondaryRail.addEventListener('click', () => setSecondaryOpen(true));
  ui.menuBtn.addEventListener('click', () => { ui.sidebar.classList.toggle('open'); syncOverlay(); });
  ui.overlay.addEventListener('click', () => { ui.sidebar.classList.remove('open'); if (state.currentView === 'chat' || state.currentView === 'work') setSecondaryOpen(false); syncOverlay(); });
  document.addEventListener('click', event => {
    if (!event.target.closest('.conversation-actions')) closeMenus();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      closeMenus();
      ui.sidebar.classList.remove('open');
      if (state.currentView === 'chat' || state.currentView === 'work') setSecondaryOpen(false);
      syncOverlay();
    }
  });
  $$('[data-setting]').forEach(el => el.addEventListener('click', () => {
    $$('[data-setting]').forEach(btn => btn.classList.toggle('active', btn === el));
    $$('.settings-section').forEach(section => section.classList.toggle('active', section.dataset.settingPanel === el.dataset.setting));
  }));
  const modal = $('#apiModal');
  const openApi = $('#openApiBtn');
  const closeApi = $('#closeApiBtn');
  if (openApi) openApi.addEventListener('click', () => modal.classList.add('open'));
  if (closeApi) closeApi.addEventListener('click', () => modal.classList.remove('open'));
  if (modal) modal.addEventListener('click', event => { if (event.target === modal) modal.classList.remove('open'); });
  $$('[data-theme-choice]').forEach(el => el.addEventListener('click', () => {
    $$('[data-theme-choice]').forEach(btn => btn.classList.toggle('active', btn === el));
    let theme = el.dataset.themeChoice;
    if (theme === 'system') theme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.dataset.theme = theme;
  }));
  $$('.auth-tabs button').forEach(el => el.addEventListener('click', () => $$('.auth-tabs button').forEach(btn => btn.classList.toggle('active', btn === el))));
  window.addEventListener('resize', () => {
    if (innerWidth > 900) ui.secondary.classList.remove('open');
    else if (!ui.secondary.classList.contains('collapsed') && !ui.secondary.classList.contains('hidden')) ui.secondary.classList.add('open');
    syncOverlay();
  });
  setPrimaryCollapsed(true);
  show('chat');
  if (innerWidth <= 900) setSecondaryOpen(false);
})();

























