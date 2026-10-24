"""Exercise the BLE page, HTTP task API, persistent queue, and MCP worker locally."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DISTANCES = [1, 5, 10, 25, 50, 100]


def request_json(url: str, body: dict | None = None) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def free_loopback_port() -> int:
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        return server.getsockname()[1]


def verify(output: Path | None) -> None:
    with tempfile.TemporaryDirectory(prefix="ble-task-http-") as data_root:
        env = os.environ.copy()
        env["WIRELESS_SIM_DATA_ROOT"] = data_root
        base = f"http://127.0.0.1:{free_loopback_port()}"
        api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "services.api.simulation_app:app", "--host", "127.0.0.1",
             "--port", base.rsplit(":", 1)[1]],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            deadline = time.monotonic() + 20
            while True:
                if api.poll() is not None:
                    raise RuntimeError(f"API exited during startup: {api.returncode}")
                try:
                    status, _ = request_json(base + "/healthz")
                    if status == 200:
                        break
                except (URLError, TimeoutError):
                    pass
                if time.monotonic() >= deadline:
                    raise TimeoutError("API did not become healthy")
                time.sleep(0.2)

            with urlopen(base + "/simulations/ble-coverage", timeout=10) as page:
                if page.status != 200 or b"task_id" not in page.read():
                    raise AssertionError("standalone page or refresh recovery is unavailable")
            status, created = request_json(base + "/api/v1/simulation-tasks",
                                           {"type": "ble_power_distance_v1"})
            if status != 202 or created.get("status") != "queued":
                raise AssertionError(f"task submission failed: {status} {created}")
            task_id = created["id"]
            worker = subprocess.run(
                [sys.executable, "-m", "services.worker", "--once"],
                cwd=ROOT, env=env, capture_output=True, text=True, timeout=180,
            )
            if worker.returncode:
                raise RuntimeError(f"worker exited {worker.returncode}: {worker.stderr}")
            status, task = request_json(base + f"/api/v1/simulation-tasks/{task_id}")
            if status != 200 or task["status"] != "succeeded":
                raise AssertionError(f"task failed: {status} {task.get('error')}")
            result = task["result"]
            points = result["points"]
            if ([point["distance_m"] for point in points] != EXPECTED_DISTANCES or
                    [point["deliveries"] for point in points] != [20, 20, 20, 20, 20, 0] or
                    result["sampled_reach_m"] != 50 or not result["validation"]["passed"]):
                raise AssertionError("default six-point acceptance result changed")

            events = []
            sequence = 0
            while True:
                status, page = request_json(base + f"/api/v1/simulation-tasks/{task_id}/events"
                                            f"?after_sequence={sequence}&limit=50")
                if status != 200:
                    raise AssertionError(f"event pagination failed: {status}")
                events.extend(page["events"])
                if not page["events"]:
                    break
                if page["next_sequence"] <= sequence:
                    raise AssertionError("event cursor did not advance")
                sequence = page["next_sequence"]
            if sum(event["kind"] == "packet_event" for event in events) != 120:
                raise AssertionError("missing packet events")
            evidence = {"task_id": task_id, "input": task["parameters"], "result": result,
                        "events": events}
            if output is not None:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"ok": True, "task_id": task_id, "status": task["status"],
                              "point_count": len(points), "packet_event_count": 120,
                              "sampled_reach_m": result["sampled_reach_m"],
                              "code_commit_sha": result["code_commit_sha"],
                              "registry_sha256": result["registry_sha256"]}))
        finally:
            api.terminate()
            try:
                api.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api.kill()
                api.wait(timeout=5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write full local evidence JSON")
    verify(parser.parse_args().output)
