-- 资料库 files 表（备注：重启后端时 create_all 会自动创建，此文件为手动兜底）
CREATE TABLE IF NOT EXISTS files (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    size INTEGER NOT NULL DEFAULT 0,
    content_type VARCHAR(120),
    storage_path VARCHAR(512) NOT NULL,
    created_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_files_user_id ON files (user_id);