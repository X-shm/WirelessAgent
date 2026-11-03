"""轻量启动迁移：为既有数据库表补齐新增列。

生产环境不会重建已存在的表（create_all 不修改既有表结构），
模型新增字段后需在此登记幂等迁移，随应用启动自动执行。
"""
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import NoSuchTableError


def apply_migrations(conn: Connection) -> None:
    """补齐缺失的列。幂等，可随每次启动重复执行。"""
    inspector = inspect(conn)
    try:
        existing = {c["name"] for c in inspector.get_columns("projects")}
    except NoSuchTableError:
        return
    if "pinned" not in existing:
        # SQLite 用 0/1，PostgreSQL 用 FALSE/TRUE
        default = "FALSE" if conn.dialect.name == "postgresql" else "0"
        conn.execute(text(
            f"ALTER TABLE projects ADD COLUMN pinned BOOLEAN NOT NULL DEFAULT {default}"
        ))