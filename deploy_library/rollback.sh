#!/usr/bin/env bash
set -e
# 资料库回滚
BACKEND=/opt/wireless-agent/backend
echo "== 回滚 =="
# 用第 2 步备份的 tar 恢复旧代码：
# tar -xzf /tmp/wag_backend_20261016XXXXXX.tar.gz -C /opt/wireless-agent
systemctl restart wireless-agent
echo "完成"