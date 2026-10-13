"""Deterministic agent workflow for a BLE power-versus-distance task."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters


TOOLBOX_ROOT = Path(__file__).resolve().parents[1] / "wireless_tools"
TOOLS = "bluetooth_path_loss,bluetooth_session"
MODEL = {
    "environment": "Industrial",
    "path_loss_exponent": 2.0,
    "standard_deviation": 0.0,
    "transmitter_antenna_gain": 0.0,
    "receiver_antenna_gain": 0.0,
    "transmitter_cable_loss": 0.0,
    "receiver_cable_loss": 0.0,
    "mobility": "stationary",
    "traffic_interval_seconds": 0.020,
    "payload_length_bytes": 16,
}


class SimulationFailure(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise SimulationFailure("VALIDATION_FAILED", message)


async def run_ble_power_distance(
    task_id: str,
    parameters: dict[str, Any],
    attempt_dir: Path,
    emit: Callable[[str, dict[str, Any]], None],
    progress: Callable[[int, dict[str, Any]], None],
) -> dict[str, Any]:
    """Call only the two allowed toolbox tools and independently check results."""
    attempt_dir.mkdir(parents=True, exist_ok=False)
    distances = parameters["distances_m"]
    tx_power = parameters["tx_power_dbm"]
    sensitivity = parameters["receiver_sensitivity_dbm"]
    packet_count = parameters["packets_per_distance"]
    registry_sha256 = hashlib.sha256((TOOLBOX_ROOT / "tool_registry.json").read_bytes()).hexdigest()
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server", "--tools", TOOLS, "--data-root", str(attempt_dir), "--timeout", "30"],
        cwd=str(TOOLBOX_ROOT),
    )
    async with Client(server, read_timeout_seconds=45) as client:
        available = {tool.name for tool in (await client.list_tools()).tools}
        _check(available == set(TOOLS.split(",")), "MCP did not expose the expected tool subset")

        async def call(name: str, request: dict[str, Any]) -> dict[str, Any]:
            response = await client.call_tool(name, {"input": json.dumps(request, ensure_ascii=False, separators=(",", ":"))})
            if response.is_error:
                message = response.content[0].text if response.content else "unknown MCP error"
                raise SimulationFailure("TOOL_ERROR", f"{name}: {message}")
            body = response.structured_content
            if not isinstance(body, dict) or body.get("ok") is not True or not isinstance(body.get("result"), dict):
                raise SimulationFailure("TOOL_ERROR", f"{name} returned an invalid result envelope")
            emit("tool_call", {"tool": name, "request": request, "result": body["result"]})
            return body["result"]

        propagation = await call("bluetooth_path_loss", {
            "distance": distances,
            "environment": MODEL["environment"],
            "path_loss_exponent": MODEL["path_loss_exponent"],
            "standard_deviation": MODEL["standard_deviation"],
            "transmitter_antenna_gain": 0,
            "receiver_antenna_gain": 0,
            "transmitter_cable_loss": 0,
            "receiver_cable_loss": 0,
        })
        losses = propagation.get("path_loss_db")
        _check(isinstance(losses, list) and len(losses) == len(distances), "path-loss vector length mismatch")
        _check(all(isinstance(value, (int, float)) and math.isfinite(value) for value in losses),
               "path-loss values must be finite")
        _check(all(right > left for left, right in zip(losses, losses[1:])),
               "path loss must increase with distance for this fixed model")

        points: list[dict[str, Any]] = []
        for index, (distance, loss) in enumerate(zip(distances, losses), start=1):
            session_file = f"point_{index:02d}.sqlite"
            common = {"session_file": session_file}
            await call("bluetooth_session", {**common, "operation": "create_session"})
            await call("bluetooth_session", {**common, "operation": "create_object",
                "object_type": "bluetoothLENode", "new_object_id": "tx",
                "properties": {"role": "central", "position": [0, 0, 0], "start_id": 1,
                               "properties": {"transmitter_power": tx_power}}})
            await call("bluetooth_session", {**common, "operation": "create_object",
                "object_type": "bluetoothLENode", "new_object_id": "rx",
                "properties": {"role": "peripheral", "position": [distance, 0, 0], "start_id": 2,
                               "properties": {"receiver_sensitivity": sensitivity}}})
            subscribed = await call("bluetooth_session", {**common, "operation": "subscribe",
                "object_id": "rx", "event_types": ["PacketReceived", "PacketDropped"]})
            await call("bluetooth_session", {**common, "operation": "invoke", "object_id": "tx",
                "method": "addTrafficSource", "arguments": {"payload_length": MODEL["payload_length_bytes"],
                    "interval": MODEL["traffic_interval_seconds"], "start_time": 0,
                    "destination_ids": [2], "max_packets": packet_count}})
            ran = await call("bluetooth_session", {**common, "operation": "run",
                "duration": (packet_count - 0.5) * MODEL["traffic_interval_seconds"]})
            observed = await call("bluetooth_session", {**common, "operation": "events",
                "subscription_id": subscribed["subscription_id"], "limit": 1000})
            summary, events = ran.get("simulation"), observed.get("events")
            _check(isinstance(summary, dict) and isinstance(events, list), "missing simulation summary or events")
            predicted_power = float(tx_power - loss)
            deliveries, drops = summary.get("deliveries"), summary.get("drops")
            _check(summary.get("transmissions") == packet_count, f"distance {distance}: transmission count mismatch")
            _check(isinstance(deliveries, int) and isinstance(drops, int) and deliveries + drops == packet_count,
                   f"distance {distance}: delivery accounting mismatch")
            _check(len(events) == packet_count, f"distance {distance}: packet event count mismatch")
            expected_deliveries = packet_count if predicted_power >= sensitivity else 0
            _check(deliveries == expected_deliveries, f"distance {distance}: sensitivity decision mismatch")
            _check(sum(event.get("event_type") == "PacketReceived" for event in events) == deliveries and
                   sum(event.get("event_type") == "PacketDropped" for event in events) == drops,
                   f"distance {distance}: packet events disagree with simulation summary")
            for event in events:
                _check(event.get("event_type") in {"PacketReceived", "PacketDropped"},
                       f"distance {distance}: unexpected packet event")
                measured_power = event.get("payload", {}).get("received_power_dbm")
                _check(isinstance(measured_power, (int, float)) and math.isclose(
                    measured_power, predicted_power, rel_tol=0, abs_tol=1e-6),
                    f"distance {distance}: received-power mismatch")
                emit("packet_event", {"distance_m": distance, "event_type": event["event_type"],
                                      "received_power_dbm": measured_power, "simulation_time": event["simulation_time"]})
            point = {"distance_m": distance, "path_loss_db": float(loss),
                     "received_power_dbm": predicted_power, "transmissions": packet_count,
                     "deliveries": deliveries, "drops": drops,
                     "delivery_ratio": deliveries / packet_count,
                     "above_sensitivity": predicted_power >= sensitivity}
            points.append(point)
            progress(round(100 * index / len(distances)), {"completed_points": index,
                "total_points": len(distances), "distance_m": distance})

    reachable = [point["distance_m"] for point in points if point["deliveries"] > 0]
    return {
        "task_id": task_id, "scenario": "ble_power_distance_v1", "parameters": parameters,
        "model": MODEL, "registry_sha256": registry_sha256, "points": points,
        "sampled_reach_m": max(reachable) if reachable else None,
        "validation": {"passed": True, "checks": ["monotonic_path_loss", "packet_accounting",
            "sensitivity_threshold", "received_power_matches_session_events"]},
        "explanation": ("在固定工业路径损耗、无阴影衰落和静止节点模型下，接收功率随距离降低；"
                        "接收功率达到灵敏度时所有测试包均被接收，否则全部丢弃。"
                        "表中的最远可接收距离仅指已测试距离点。"),
        "limitations": ["确定性灵敏度门限模型，不是实测或随机 PER 曲线",
                        "不覆盖完整 BLE 链路层、干扰、碰撞、重传或移动过程"],
    }
