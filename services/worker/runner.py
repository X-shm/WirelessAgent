"""Single-consumer persistent queue worker for BLE simulation tasks."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
import traceback
from pathlib import Path

from packages.agent.ble_coverage import SimulationFailure, run_ble_power_distance
from services.api.store import TaskStore


TEAM_ROOT = Path(__file__).resolve().parents[2]


def data_root() -> Path:
    return Path(os.environ.get("WIRELESS_SIM_DATA_ROOT", str(TEAM_ROOT / ".runtime")))


async def _keep_heartbeat(store: TaskStore, stopped: asyncio.Event) -> None:
    while not stopped.is_set():
        store.heartbeat()
        try:
            await asyncio.wait_for(stopped.wait(), timeout=5)
        except TimeoutError:
            pass


async def _execute(store: TaskStore, task: dict) -> None:
    task_id = task["id"]
    attempt_dir = store.root / "tasks" / task_id / f"attempt_{task['attempt']:03d}"

    def emit(kind: str, payload: dict) -> None:
        store.event(task_id, kind, payload)
        store.heartbeat()

    def progress(percent: int, payload: dict) -> None:
        store.progress(task_id, percent, payload)
        store.heartbeat()

    stopped = asyncio.Event()
    heartbeat_task = asyncio.create_task(_keep_heartbeat(store, stopped))
    try:
        if task["type"] != "ble_power_distance_v1":
            raise SimulationFailure("UNSUPPORTED_TASK", f"unsupported task type: {task['type']}")
        result = await run_ble_power_distance(task_id, task["parameters"], attempt_dir, emit, progress)
    except Exception as exc:
        cause = exc
        while isinstance(cause, ExceptionGroup) and cause.exceptions:
            cause = cause.exceptions[0]
        if isinstance(cause, SimulationFailure):
            store.finish(task_id, error={"code": cause.code, "message": str(cause)})
        else:
            traceback.print_exc()
            store.finish(task_id, error={"code": "EXECUTION_FAILED", "message": str(cause)})
    else:
        store.finish(task_id, result=result)
    finally:
        stopped.set()
        await heartbeat_task


def run_once(store: TaskStore) -> bool:
    store.heartbeat()
    task = store.claim_next()
    if task is None:
        return False
    asyncio.run(_execute(store, task))
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="WirelessAgent simulation worker")
    parser.add_argument("--once", action="store_true", help="run at most one queued task")
    parser.add_argument("--healthcheck", action="store_true", help="exit nonzero if heartbeat is stale")
    parser.add_argument("--poll-interval", type=float, default=1.0)
    args = parser.parse_args()
    if args.poll_interval <= 0:
        parser.error("--poll-interval must be positive")
    store = TaskStore(data_root())
    if args.healthcheck:
        sys.exit(0 if store.worker_alive() else 1)
    store.requeue_interrupted()
    if args.once:
        run_once(store)
        return
    while True:
        if not run_once(store):
            time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
