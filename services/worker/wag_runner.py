"""Single-consumer worker that executes queued tasks from the shared database."""
import argparse
import asyncio
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "services" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from wag.config import settings  # noqa: E402
from wag.database import async_session, engine  # noqa: E402
from wag.models.base import Base  # noqa: E402
from wag.models.task import Task  # noqa: E402
from wag.task_status import TaskStatus  # noqa: E402
from sqlalchemy import select  # noqa: E402

from .wag_handlers import REGISTRY  # noqa: E402


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def ensure_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _claim_next():
    async with async_session() as db:
        row = (
            await db.execute(
                select(Task).where(Task.status == TaskStatus.queued.value).order_by(Task.created_at).limit(1)
            )
        ).scalar_one_or_none()
        if row is None:
            return None
        row.status = TaskStatus.running.value
        row.started_at = _now()
        row.updated_at = _now()
        await db.commit()
        await db.refresh(row)
        return row


async def _is_cancelled(task_id: str) -> bool:
    async with async_session() as db:
        row = await db.get(Task, task_id)
        return row is not None and row.status == TaskStatus.cancelled.value


async def _update(task_id: str, *, progress=None, stage=None):
    async with async_session() as db:
        row = await db.get(Task, task_id)
        if row is None:
            return
        if progress is not None:
            row.progress = progress
        if stage is not None:
            row.stage = stage
        row.updated_at = _now()
        await db.commit()


async def _execute(task: Task):
    handler = REGISTRY.get(task.type)
    if handler is None:
        async with async_session() as db:
            row = await db.get(Task, task.id)
            if row is not None:
                row.status = TaskStatus.failed.value
                row.error = f"unsupported task type: {task.type}"
                row.finished_at = _now()
                row.updated_at = _now()
                await db.commit()
        return

    async def update_progress(percent, stage):
        await _update(task.id, progress=percent, stage=stage)

    try:
        result = await handler(task.id, task.parameters or {}, update_progress, _is_cancelled)
    except asyncio.CancelledError:
        result, status_value, error = None, TaskStatus.cancelled.value, None
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        result, status_value, error = None, TaskStatus.failed.value, str(exc)
    else:
        if await _is_cancelled(task.id):
            result, status_value, error = None, TaskStatus.cancelled.value, None
        else:
            status_value, error = TaskStatus.succeeded.value, None

    async with async_session() as db:
        row = await db.get(Task, task.id)
        if row is not None:
            row.status = status_value
            if status_value == TaskStatus.succeeded.value:
                row.progress = 100
            row.result = result
            row.error = error
            row.finished_at = _now()
            row.updated_at = _now()
            await db.commit()


async def run_once() -> bool:
    try:
        task = await _claim_next()
        if task is None:
            return False
        await _execute(task)
        return True
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="WirelessAgent task worker")
    parser.add_argument("--once", action="store_true", help="run at most one queued task")
    parser.add_argument("--poll-interval", type=float, default=None)
    args = parser.parse_args()
    interval = args.poll_interval if args.poll_interval is not None else settings.task_poll_interval

    async def loop():
        await ensure_schema()
        if args.once:
            await run_once()
            return
        while True:
            if not await run_once():
                await asyncio.sleep(interval)

    asyncio.run(loop())


if __name__ == "__main__":
    main()