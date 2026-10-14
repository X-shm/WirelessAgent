"""Local-first simulation task API and standalone task page."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse

from .models import CreateSimulationTask
from .store import TaskStore


TEAM_ROOT = Path(__file__).resolve().parents[2]
PAGE = TEAM_ROOT / "apps" / "web" / "simulations" / "ble_coverage.html"


def create_app(data_root: Path | None = None) -> FastAPI:
    root = data_root or Path(os.environ.get("WIRELESS_SIM_DATA_ROOT", str(TEAM_ROOT / ".runtime")))
    store = TaskStore(root)
    app = FastAPI(title="WirelessAgent Simulation API", version="1.0.0")
    app.state.store = store

    @app.get("/")
    def home() -> RedirectResponse:
        return RedirectResponse("/simulations/ble-coverage")

    @app.get("/simulations/ble-coverage")
    def simulation_page() -> FileResponse:
        return FileResponse(PAGE, media_type="text/html; charset=utf-8")

    @app.get("/healthz")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/readyz")
    def ready() -> dict:
        if not store.worker_alive():
            raise HTTPException(status_code=503, detail="worker heartbeat is stale")
        return {"status": "ready"}

    @app.post("/api/v1/simulation-tasks", status_code=202)
    def create_task(request: CreateSimulationTask) -> dict:
        task = store.create(request.type, request.parameters.model_dump())
        return {"id": task["id"], "status": task["status"],
                "status_url": f"/api/v1/simulation-tasks/{task['id']}",
                "events_url": f"/api/v1/simulation-tasks/{task['id']}/events"}

    @app.get("/api/v1/simulation-tasks/{task_id}")
    def get_task(task_id: str) -> dict:
        task = store.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="task not found")
        return task

    @app.get("/api/v1/simulation-tasks/{task_id}/events")
    def get_events(task_id: str, after_sequence: int = Query(default=0, ge=0),
                   limit: int = Query(default=100, ge=1, le=200)) -> dict:
        if store.get(task_id) is None:
            raise HTTPException(status_code=404, detail="task not found")
        events = store.events(task_id, after_sequence, limit)
        return {"events": events, "next_sequence": events[-1]["sequence"] if events else after_sequence}

    return app


app = create_app()
