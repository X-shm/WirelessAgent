"""SQLite task queue and append-only audit events shared by API and one worker."""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _encode(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


class TaskStore:
    def __init__(self, data_root: Path):
        self.root = data_root.expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.database = self.root / "simulation_tasks.sqlite3"
        with closing(self._connect()) as connection, connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress INTEGER NOT NULL DEFAULT 0,
                    attempt INTEGER NOT NULL DEFAULT 0,
                    result TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT
                );
                CREATE TABLE IF NOT EXISTS task_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL REFERENCES tasks(id),
                    created_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS task_events_by_task ON task_events(task_id, sequence);
                CREATE TABLE IF NOT EXISTS worker_heartbeat (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    seen_at REAL NOT NULL
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    @staticmethod
    def _task(row: sqlite3.Row) -> dict[str, Any]:
        task = dict(row)
        for key in ("parameters", "result", "error"):
            task[key] = json.loads(task[key]) if task[key] is not None else None
        return task

    def create(self, task_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        task_id, now = str(uuid.uuid4()), _now()
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO tasks(id,type,parameters,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                (task_id, task_type, _encode(parameters), "queued", now, now),
            )
            connection.execute(
                "INSERT INTO task_events(task_id,created_at,kind,payload) VALUES(?,?,?,?)",
                (task_id, now, "queued", _encode({"type": task_type})),
            )
        return self.get(task_id)  # type: ignore[return-value]

    def get(self, task_id: str) -> dict[str, Any] | None:
        with closing(self._connect()) as connection, connection:
            row = connection.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return self._task(row) if row else None

    def events(self, task_id: str, after_sequence: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        with closing(self._connect()) as connection, connection:
            rows = connection.execute(
                "SELECT sequence,created_at,kind,payload FROM task_events "
                "WHERE task_id=? AND sequence>? ORDER BY sequence LIMIT ?",
                (task_id, after_sequence, limit),
            ).fetchall()
        return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]

    def event(self, task_id: str, kind: str, payload: dict[str, Any]) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO task_events(task_id,created_at,kind,payload) VALUES(?,?,?,?)",
                (task_id, _now(), kind, _encode(payload)),
            )

    def heartbeat(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "INSERT INTO worker_heartbeat(id,seen_at) VALUES(1,?) "
                "ON CONFLICT(id) DO UPDATE SET seen_at=excluded.seen_at", (time.time(),),
            )

    def worker_alive(self, max_age_seconds: float = 15) -> bool:
        with closing(self._connect()) as connection, connection:
            row = connection.execute("SELECT seen_at FROM worker_heartbeat WHERE id=1").fetchone()
        return bool(row and time.time() - float(row["seen_at"]) <= max_age_seconds)

    def requeue_interrupted(self) -> None:
        with closing(self._connect()) as connection, connection:
            rows = connection.execute("SELECT id FROM tasks WHERE status='running'").fetchall()
            for row in rows:
                connection.execute("UPDATE tasks SET status='queued',progress=0,updated_at=? WHERE id=?", (_now(), row["id"]))
                connection.execute(
                    "INSERT INTO task_events(task_id,created_at,kind,payload) VALUES(?,?,?,?)",
                    (row["id"], _now(), "requeued", _encode({"reason": "worker_restart"})),
                )

    def claim_next(self) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM tasks WHERE status='queued' ORDER BY created_at,id LIMIT 1").fetchone()
            if row is None:
                connection.commit()
                return None
            now = _now()
            connection.execute(
                "UPDATE tasks SET status='running',attempt=attempt+1,progress=0,started_at=?,updated_at=?,"
                "finished_at=NULL,error=NULL,result=NULL WHERE id=?", (now, now, row["id"]),
            )
            connection.execute(
                "INSERT INTO task_events(task_id,created_at,kind,payload) VALUES(?,?,?,?)",
                (row["id"], now, "running", _encode({"attempt": row["attempt"] + 1})),
            )
            connection.commit()
            return self.get(row["id"])
        finally:
            connection.close()

    def progress(self, task_id: str, percent: int, payload: dict[str, Any]) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute("UPDATE tasks SET progress=?,updated_at=? WHERE id=?", (percent, _now(), task_id))
            connection.execute(
                "INSERT INTO task_events(task_id,created_at,kind,payload) VALUES(?,?,?,?)",
                (task_id, _now(), "progress", _encode(payload)),
            )

    def finish(self, task_id: str, *, result: dict[str, Any] | None = None,
               error: dict[str, Any] | None = None) -> None:
        status, now = ("succeeded" if error is None else "failed"), _now()
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "UPDATE tasks SET status=?,progress=?,result=?,error=?,updated_at=?,finished_at=? WHERE id=?",
                (status, 100 if error is None else 0, _encode(result) if result is not None else None,
                 _encode(error) if error is not None else None, now, now, task_id),
            )
            connection.execute(
                "INSERT INTO task_events(task_id,created_at,kind,payload) VALUES(?,?,?,?)",
                (task_id, now, status, _encode({"error": error} if error else {"validated": True})),
            )
