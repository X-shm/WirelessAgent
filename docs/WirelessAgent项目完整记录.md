# WirelessAgent 项目完整会话记录

> 记录日期：2026-08-05 ~ 2026-08-07
> 本地路径：D:\资料\文件\opc-agent\无线智能体\网站\code\
> 服务器：root@<SERVER_IP>
> 网站：https://wirelessagent.plus

---

## 一、项目架构

用户浏览器 -> https://wirelessagent.plus (Cloudflare Tunnel) -> 阿里云 127.0.0.1:8000 (FastAPI + React) -> OpenClaw Gateway (127.0.0.1:18789) -> Kimi AI (kimi-k2.6)

## 二、服务器登录

SSH: root@<SERVER_IP>
密码: <REDACTED>...

本地隧道(开发调试):
ssh -L 8000:127.0.0.1:8000 root@<SERVER_IP>
然后浏览器打开 http://localhost:8000

## 三、方案B 部署 -- user字段会话隔离(2026-08-05)

### 问题
所有用户共用一个 OpenClaw agent session,AI 把所有人的对话当成同一个上下文,互相污染。

### 方案
利用 OpenClaw 的 user 字段,每个 session 在 Gateway 眼里是独立用户。

### 改动(两个文件)
1. backend/app/services/openclaw_client.py
   - chat() 和 chat_stream() 新增 user_id: str | None = None 参数
   - 非空时写入 payload["user"] = user_id

2. backend/app/routes/chat.py
   - 新增 WIRELESS_PROMPT 常量(WirelessAgent 系统提示词)
   - 调用 chat_stream 时传 system_prompt=WIRELESS_PROMPT, user_id=session.id
   - 新增 RECENT_ROUNDS = 10 滑动窗口(只发最近20条消息)

### 部署
本地改代码 -> npm run build 前端 -> scp 上传 2个py + dist -> systemctl restart wireless-agent

### 验证
Session A 告诉 AI "我姓李手机号8888" -> Session B 问 "我姓什么" -> AI 回答 "我没有你的个人信息"
结论: 跨会话隔离完全生效

## 四、P1 安全加固 + 性能优化(2026-08-05)

### P1-1 禁用 AI 高危工具
文件: /root/.openclaw/openclaw.json -> nodes.denyCommands

原列表: camera.snap, camera.clip, screen.record, contacts.add, calendar.add, reminders.add, sms.send, sms.search

追加: write, edit, apply_patch, exec
后来为了 Skill 运行移除了 exec,保留 write/edit/apply_patch

重启: systemctl --user restart openclaw-gateway.service

### P1-2 对话历史滑动窗口
chat.py 中: RECENT_ROUNDS = 10
messages = history[-(RECENT_ROUNDS * 2):]  # 只取最后20条

效果: Token 消耗恒定不膨胀, Gateway 重启后 AI 有历史消息兜底不会失忆

## 五、P2 功能完善(2026-08-05)

### P2-1 数据收集 Analytics
新建文件: backend/app/models/analytics.py
  - 字段: id, session_id, user_id, question, answer, timestamp
注册模型: models/__init__.py 加 Analytics
写入逻辑: chat.py 中保存 assistant 回复后同步写 analytics
导出接口: routes/analytics.py -> GET /api/analytics/export -> CSV 下载
路由注册: main.py 加 analytics.router

重要: export 接口需要 response_model=None,否则 FastAPI 会把 AsyncSession 当 Pydantic 类型报错

### P2-2 提示词外置
config.py: 新增 wireless_prompt: str 字段(含默认值)
.env: 新增 WIRELESS_PROMPT=... 变量
chat.py: 删除 WIRELESS_PROMPT 常量,改用 settings.wireless_prompt
效果: 老师编辑 .env 后重启即可改提示词,不用碰代码

### P2-3 限流 slowapi
安装: python3.11 -m pip install slowapi (约 60KB 轻量,无需 Redis)
新建 limiter.py: 自定义 get_real_ip() 从 Cloudflare CF-Connecting-IP 头取真实 IP
main.py: 初始化 Limiter, 注册 429 异常处理
chat.py: 路由加 @limiter.limit("1/second")
效果: 每 IP 每秒最多 1 条消息,超限返回 429

### P2-4 错误提示优化
chat.py except 块根据异常类型返回中文:
  - timeout/timed out -> "回复生成超时,请缩短问题或稍后重试"
  - connection refused -> "AI 服务暂时不可用,请稍后重试"
  - 401/unauthorized -> "AI 服务认证失败,请检查 Gateway 配置"
  - 其他 -> "服务异常: {具体原因}"

useChat.ts: SSE error 显示在对话气泡中(前缀图标),而非静默 console.log
连接失败时在对话中显示错误消息

## 六、中文乱码修复(2026-08-05)

问题: 注册页面昵称/邮箱/密码显示为乱码
原因: LoginPage.tsx 被 GBK 编码保存, TypeScript 编译器按 UTF-8 读
修复: 在二进制层面替换 5 处损坏的中文字节序列为正确 UTF-8,重建部署

## 七、Skill 安装(2026-08-05)

### Wireless Homework Solver
安装路径: /root/.openclaw/workspace/skills/wirelesshomeworksolver/
依赖: numpy 2.4.6, scipy 1.17.1 (Python 3.11,已预装)

安装命令:
  scp -r wirelesshomeworksolver root@<SERVER_IP>:/root/.openclaw/skills/
  openclaw skills install /root/.openclaw/skills/wirelesshomeworksolver

核心脚本:
  telecom_calc.py      -- Q函数/BER/信道容量/衰落/MRC/编码纠错(精确数值)
  formula_lookup.py    -- 30+条公式查询+数值计算
  unit_convert.py      -- dB/dBm/dBW/Hz-kHz-MHz-GHz/W-mW
  question_recommend.py -- TF-IDF 相似题目推荐(28道种子题,9领域)
  error_book.py        -- SM-2 间隔重复错题本
  evaluate.py          -- 四维评分(公式35%+数值25%+单位20%+逻辑20%)

自动触发配置:
  1. SKILL.md 删除 user-invocable: true(改为自动注册)
  2. openclaw.json denyCommands 移除 exec(Skill 需要命令执行)
  3. .env WIRELESS_PROMPT 末尾追加触发规则(通信计算题自动调用)
  4. Skill 评分卡改为条件触发(仅当用户提交答案时输出)

## 八、DeepSeek -> Kimi 模型切换(2026-08-05)

使用 OpenClaw CLI 操作(非手动编辑 JSON):
  1. openclaw models auth add -> custom -> moonshot -> 粘贴 API Key
  2. openclaw configure --section model -> Moonshot AI -> .cn -> npm 安装插件
  3. openclaw models set moonshot/kimi-k2.6
  4. systemctl --user restart openclaw-gateway.service

验证: curl 测试 -> 回复 "我是 moonshot/kimi-k2.6"

不影响: Gateway 令牌 <REDACTED> 不变, FastAPI .env 不变, 所有网站功能不变

回滚 DeepSeek:
  openclaw models set deepseek/deepseek-chat
  systemctl --user restart openclaw-gateway.service

## 九、KaTeX 公式渲染(2026-08-05 ~ 08-06)

最终方案:
  index.html: 引入 KaTeX CSS + JS + auto-render.min.js(CDN)
  index.css: KaTeX overflow 约束 + html,body{overflow:hidden;height:100%}
  ChatBubble.tsx: useMemo + parseContent() 拆成 markdown段 + 数学段
    关键: 不用 renderMathInElement(避免 React 渲染后改 DOM 导致滚动跳动)

滚动修复历程:
  1. renderMathInElement -> 滚动跳动
  2. 改用 react-markdown components -> 公式不好看
  3. 多次修补后发现: html/body 没 overflow:hidden
  4. index.css 加 html,body{overflow:hidden;height:100%} -> 解决
  5. SessionSidebar.tsx: h-screen -> h-full(避免双倍 100vh)
  6. ChatList.tsx: 智能自动滚动(用户离开底部时不强制)

401 Token 自动恢复:
  api.ts: 拦截 401 -> 清 token -> 自动刷新页面
  ChatPage.tsx: 无 token 时自动创建 guest 账号

## 十、部署注意事项(重要!!)

### 永远不要上传 .env
本地 .env 和服务器 .env 不一样。只传 .py 和 dist/,绝不传 .env。

### 标准部署流程
  1. 本地改代码
  2. cd frontend && npm run build (仅当前端改动时)
  3. scp backend/app/routes/chat.py root@<SERVER_IP>:/opt/wireless-agent/backend/app/routes/chat.py
  4. scp -r frontend/dist root@<SERVER_IP>:/opt/wireless-agent/frontend/
  5. ssh root@<SERVER_IP> "systemctl restart wireless-agent"
  6. curl 验证: ssh root@<SERVER_IP> "curl -s http://127.0.0.1:8000/api/health"

### 用户浏览器 401 处理
F12 Console: localStorage.clear(); location.reload()

### Gateway 是用户级 systemd
systemctl --user restart openclaw-gateway.service
注意是 --user,不是 systemctl

## 十一、当前故障(2026-08-07)

问题: https://wirelessagent.plus 返回 Error 1033 (Cloudflare Tunnel error)
原因: 阿里云服务器连不上 Cloudflare 境外端点
诊断: region1.v2.argotunnel.com unreachable, UDP/TCP 连接均失败

DNS 状态: 域名仍指向 Cloudflare NS (解析 IP: 172.67.159.191)
Cloudflare 配置: /etc/cloudflared/config.yml 已恢复原始版本

临时方案: 阿里云安全组开放 8000 端口 -> http://<SERVER_IP>:8000
长期方案: ICP 备案通过(约一周) -> DNS 改回阿里云 -> 80/443 + Nginx Proxy Manager

## 十二、关键文件路径

### 服务器 /opt/wireless-agent/
  backend/app/main.py               # FastAPI 入口
  backend/app/config.py             # 配置(含 wireless_prompt)
  backend/app/limiter.py            # slowapi 限流器
  backend/app/models/analytics.py   # 数据收集模型
  backend/app/models/__init__.py    # 模型注册
  backend/app/routes/chat.py        # 核心聊天逻辑
  backend/app/routes/analytics.py   # CSV 导出
  backend/app/services/openclaw_client.py  # Gateway 客户端
  backend/.env                      # 环境变量(勿覆盖!)

### 服务器 /root/.openclaw/
  openclaw.json                    # Gateway 配置(模型/工具/认证)
  workspace/IDENTITY.md            # AI 身份定义
  workspace/USER.md                # 用户画像
  workspace/skills/wirelesshomeworksolver/  # Skill

### systemd 服务
  /etc/systemd/system/wireless-agent.service     # 后端(Python3.11)
  /etc/systemd/system/cloudflared.service         # Tunnel
  /root/.config/systemd/user/openclaw-gateway.service  # Gateway

## 十三、验证命令

# 各服务状态
systemctl status wireless-agent
systemctl --user status openclaw-gateway.service
systemctl status cloudflared

# API
curl -s http://127.0.0.1:8000/api/health
curl -s https://wirelessagent.plus/api/health

# 数据库
sqlite3 /opt/wireless-agent/backend/wirelessagent.db ".tables"

# AI 模型
grep primary /root/.openclaw/openclaw.json

# Skill 列表
openclaw skills list

# Cloudflare 连接
curl -s http://127.0.0.1:20241/metrics | grep tunnel_ha_connections

# DNS
python3 -c "import socket; print(socket.gethostbyname('wirelessagent.plus'))"

# Gateway 日志
journalctl --user -xeu openclaw-gateway.service --no-pager -n 20

# 最近错误
journalctl -xeu wireless-agent.service --no-pager -n 20 | grep -i error

## 十四、待推进 P3

- Gateway session 自动清理机制
- 老师管理后台(在线改提示词/查看对话数据)
- 会话归档与主题检索
- 正式用户注册优化(密码重置/邮箱验证)
- ICP 备案通过 -> DNS 改回阿里云 -> Nginx Proxy Manager 配 HTTPS

---

更多细节见本地文件: 部署信息汇总.md, CloudflareTunnel部署方案.md, 快速上手.md, 多用户会话隔离方案.md
