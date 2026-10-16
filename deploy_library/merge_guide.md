# 资料库部署说明

## 一、先安装 LibreOffice 与中文字体（只做一次）
```bash
dnf install -y libreoffice
dnf install -y wqy-zenhei-fonts wqy-microhei-fonts
```

## 二、复制文件（deploy.sh 已包含）
- app/routes/file.py        -> backend/app/routes/file.py   （覆盖）
- app/models/file.py        -> backend/app/models/file.py   （新增）
- app/services/file_preview.py -> backend/app/services/file_preview.py（新增）
- library.html              -> backend/library.html          （新增）
- patch/app/models/__init__.py -> backend/app/models/__init__.py（覆盖，已加 File）
- patch/app/main.py         -> backend/app/main.py           （覆盖，已加 /library 路由）

## 三、重启后端
files 表由 create_all 自动创建。

## 四、验证
打开 https://wirelessagent.plus/library