#!/usr/bin/env bash
set -euo pipefail

# WirelessAgent 生产部署脚本（由 GitHub Actions 调用，也可手动执行）。
#
# 目录映射（仓库 -> 服务器 /opt/wireless-agent）：
#   services/api/app/                 -> backend/app/
#   services/api/requirements-app.txt -> backend/requirements.txt
#   services/api/scripts/             -> backend/scripts/
#   apps/web/assets/                  -> frontend/dist/assets/
#   apps/web/index.html               -> frontend/dist/index.html
#
# 敏感文件（backend/.env、backend/*.db、backend/uploads/、
# backend/chroma_data/）**绝不覆盖**，只动上面的白名单路径。

BASE="/opt/wireless-agent"
RELEASE="${BASE}/_release"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${BASE}/backups"

# 0. 校验 release 结构
if [[ ! -d "${RELEASE}/services/api/app" || ! -d "${RELEASE}/apps/web/assets" ]]; then
  echo "ERROR: release 目录结构不完整（缺 services/api/app 或 apps/web/assets）" >&2
  exit 2
fi

# 1. 备份当前线上代码
mkdir -p "${BACKUP_DIR}"
tar -czf "${BACKUP_DIR}/backend-${TS}.tar.gz" -C "${BASE}" backend/app backend/scripts 2>/dev/null || true
tar -czf "${BACKUP_DIR}/frontend-${TS}.tar.gz" -C "${BASE}" frontend/dist 2>/dev/null || true
echo "backup -> ${BACKUP_DIR}/backend-${TS}.tar.gz"

# 2. 同步后端（整体替换 app/，从而清掉已删除的文件；scripts/ 增量覆盖）
rm -rf "${BASE}/backend/app"
cp -r "${RELEASE}/services/api/app" "${BASE}/backend/app"
mkdir -p "${BASE}/backend/scripts"
cp -f "${RELEASE}/services/api/scripts/"*.py "${BASE}/backend/scripts/" 2>/dev/null || true
cp -f "${RELEASE}/services/api/requirements-app.txt" "${BASE}/backend/requirements.txt" 2>/dev/null || true

# 3. 同步前端
mkdir -p "${BASE}/frontend/dist/assets"
cp -f "${RELEASE}/apps/web/assets/"* "${BASE}/frontend/dist/assets/" 2>/dev/null || true
cp -f "${RELEASE}/apps/web/index.html" "${BASE}/frontend/dist/index.html"

# 4. 清理缓存目录
find "${BASE}/backend/app" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# 5. 重启服务
systemctl restart wireless-agent

# 6. 健康检查（最多重试 10 次，每次间隔 2s）
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if curl -sf http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
    echo "OK: $(curl -s http://127.0.0.1:8000/api/health)"
    exit 0
  fi
  sleep 2
done

echo "ERROR: 健康检查失败，服务可能未正常启动（备份见 ${BACKUP_DIR}）" >&2
systemctl status wireless-agent --no-pager -l >&2 || true
exit 1
