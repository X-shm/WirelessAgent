"""End-to-end checks for the BLE task API, persistent queue, and MCP worker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import ValidationError

from services.api.app import create_app
from services.api.models import BlePowerDistanceParameters
from services.api.store import TaskStore
from packages.agent.ble_coverage import SimulationFailure
from services.worker.runner import run_once


class SimulationTaskTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = TaskStore(self.root)
        self.client = TestClient(create_app(self.root))
        self.addCleanup(self.client.close)

    def test_api_worker_and_cross_validation(self) -> None:
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertEqual(self.client.get("/readyz").status_code, 503)
        page = self.client.get("/simulations/ble-coverage")
        self.assertEqual(page.status_code, 200)
        self.assertIn("BLE 发射功率与距离扫描", page.text)

        created = self.client.post("/api/v1/simulation-tasks", json={
            "type": "ble_power_distance_v1",
            "parameters": {"tx_power_dbm": 0, "receiver_sensitivity_dbm": -75,
                           "distances_m": [1, 100], "packets_per_distance": 2},
        })
        self.assertEqual(created.status_code, 202, created.text)
        task_id = created.json()["id"]
        self.assertEqual(self.client.get(f"/api/v1/simulation-tasks/{task_id}").json()["status"], "queued")

        self.assertTrue(run_once(self.store))
        self.assertEqual(self.client.get("/readyz").status_code, 200)
        task = self.client.get(f"/api/v1/simulation-tasks/{task_id}").json()
        self.assertEqual(task["status"], "succeeded", task.get("error"))
        result = task["result"]
        self.assertTrue(result["validation"]["passed"])
        self.assertEqual([point["distance_m"] for point in result["points"]], [1, 100])
        self.assertEqual([point["deliveries"] for point in result["points"]], [2, 0])
        self.assertEqual([point["drops"] for point in result["points"]], [0, 2])
        self.assertEqual(result["sampled_reach_m"], 1)
        self.assertEqual(task["attempt"], 1)

        events = self.client.get(f"/api/v1/simulation-tasks/{task_id}/events", params={"limit": 200}).json()["events"]
        self.assertEqual(sum(event["kind"] == "packet_event" for event in events), 4)
        self.assertTrue(any(event["kind"] == "tool_call" and
                            event["payload"]["tool"] == "bluetooth_path_loss" for event in events))
        self.assertEqual(events[-1]["kind"], "succeeded")
        self.assertTrue((self.root / "tasks" / task_id / "attempt_001" / "point_01.sqlite").exists())

    def test_input_contract_and_missing_tasks(self) -> None:
        base = {"type": "ble_power_distance_v1", "parameters": {"distances_m": [1, 10]}}
        for values in ([10, 10], [0, 10], [1, 1001]):
            with self.subTest(values=values):
                response = self.client.post("/api/v1/simulation-tasks", json={
                    "type": base["type"], "parameters": {"distances_m": values}})
                self.assertEqual(response.status_code, 422)
        with self.assertRaises(ValidationError):
            BlePowerDistanceParameters(distances_m=[1, float("nan")])
        self.assertEqual(self.client.post("/api/v1/simulation-tasks", json={
            "type": "other", "parameters": {}}).status_code, 422)
        self.assertEqual(self.client.get("/api/v1/simulation-tasks/missing").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/simulation-tasks/missing/events").status_code, 404)

    def test_default_six_point_scenario(self) -> None:
        response = self.client.post("/api/v1/simulation-tasks", json={"type": "ble_power_distance_v1"})
        self.assertEqual(response.status_code, 202, response.text)
        task_id = response.json()["id"]
        self.assertTrue(run_once(self.store))
        task = self.store.get(task_id)
        self.assertEqual(task["status"], "succeeded", task["error"])
        points = task["result"]["points"]
        self.assertEqual([point["distance_m"] for point in points], [1, 5, 10, 25, 50, 100])
        self.assertTrue(all(point["transmissions"] == 20 for point in points))
        self.assertTrue(all(point["deliveries"] + point["drops"] == 20 for point in points))
        self.assertEqual([point["deliveries"] for point in points], [20, 20, 20, 20, 20, 0])
        self.assertEqual(task["result"]["sampled_reach_m"], 50)
        self.assertTrue(all(a["received_power_dbm"] > b["received_power_dbm"]
                            for a, b in zip(points, points[1:])))
        events = self.store.events(task_id, limit=200)
        self.assertEqual(sum(event["kind"] == "packet_event" for event in events), 120)
        self.assertTrue(task["result"]["validation"]["passed"])

    def test_worker_restart_requeues_without_overwriting_attempt(self) -> None:
        task = self.store.create("ble_power_distance_v1", {
            "tx_power_dbm": 0, "receiver_sensitivity_dbm": -75,
            "distances_m": [1, 100], "packets_per_distance": 2})
        claimed = self.store.claim_next()
        self.assertEqual(claimed["attempt"], 1)
        first_attempt = self.root / "tasks" / task["id"] / "attempt_001"
        first_attempt.mkdir(parents=True)
        (first_attempt / "partial.txt").write_text("preserved", encoding="utf-8")
        self.store.requeue_interrupted()
        self.assertEqual(self.store.get(task["id"])["status"], "queued")
        self.assertTrue(run_once(self.store))
        again = self.store.get(task["id"])
        self.assertEqual(again["attempt"], 2)
        self.assertEqual(again["status"], "succeeded", again["error"])
        self.assertEqual((first_attempt / "partial.txt").read_text(encoding="utf-8"), "preserved")
        self.assertTrue((self.root / "tasks" / task["id"] / "attempt_002" / "point_01.sqlite").exists())
        self.assertIn("requeued", [event["kind"] for event in self.store.events(task["id"])])

    def test_failed_task_has_terminal_error_and_event(self) -> None:
        task = self.store.create("ble_power_distance_v1", {
            "tx_power_dbm": 0, "receiver_sensitivity_dbm": -75,
            "distances_m": [1, 100], "packets_per_distance": 2})

        async def fail(*_args):
            raise SimulationFailure("VALIDATION_FAILED", "forced validation failure")

        with patch("services.worker.runner.run_ble_power_distance", fail):
            self.assertTrue(run_once(self.store))
        result = self.store.get(task["id"])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["code"], "VALIDATION_FAILED")
        self.assertEqual(self.store.events(task["id"])[-1]["kind"], "failed")


if __name__ == "__main__":
    unittest.main()
