#!/usr/bin/env bash
set -e
# WirelessAgent 资料库部署脚本
# 在服务器执行：cd /opt/wireless-agent && bash deploy_library/deploy.sh
BACKEND=/opt/wireless-agent/backend

echo "== 1) 备份数据库 =="
pg_dump -h 127.0.0.1 -U wag -d wirelessagent > /tmp/wag_backup_$(date +%Y%m%d%H%M%S).sql

echo "== 2) 备份旧代码 =="
tar -czf /tmp/wag_backend_$(date +%Y%m%d%H%M%S).tar.gz -C /opt/wireless-agent backend

echo "== 3) 复制新文件 =="
cp deploy_library/app/routes/file.py            $BACKEND/app/routes/file.py
cp deploy_library/app/models/file.py            $BACKEND/app/models/file.py
cp deploy_library/app/services/file_preview.py  $BACKEND/app/services/file_preview.py
cp deploy_library/library.html                  $BACKEND/library.html
cp deploy_library/patch/app/models/__init__.py  $BACKEND/app/models/__init__.py
cp deploy_library/patch/app/main.py             $BACKEND/app/main.py

echo "== 4) 重启后端（自动建 files 表） =="
systemctl restart wireless-agent

echo "== 完成，请访问 /library 验证 =="