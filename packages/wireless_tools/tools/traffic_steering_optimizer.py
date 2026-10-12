"""Capacity/latency/quality-aware traffic steering with assignment hysteresis."""
from __future__ import annotations
import argparse
import json
import math
import sys


def steer_traffic(flows, accesses, hysteresis=0.05):
    if not isinstance(flows, list) or not isinstance(accesses, list) or not accesses:
        raise ValueError("flows/accesses must be arrays and at least one access is required")
    if float(hysteresis) < 0:
        raise ValueError("hysteresis must be nonnegative")
    state = {}
    for index, access in enumerate(accesses):
        identifier = str(access.get("id", index))
        capacity = float(access.get("capacity_kbps", 0))
        if capacity < 0:
            raise ValueError("access capacity must be nonnegative")
        state[identifier] = {**access, "id": identifier, "remaining_kbps": capacity}
    assignments = []
    ordered = sorted(enumerate(flows), key=lambda pair: (-float(pair[1].get("priority", 1)), pair[0]))
    for position, flow in ordered:
        demand = float(flow.get("required_kbps", 0))
        max_latency = float(flow.get("max_latency_ms", float("inf")))
        if demand < 0:
            raise ValueError("flow demand must be nonnegative")
        candidates = []
        for access in state.values():
            latency = float(access.get("latency_ms", float("inf")))
            loss = float(access.get("packet_loss", 0))
            snr = float(access.get("snr_db", 0))
            cost = float(access.get("cost", 0))
            feasible = latency <= max_latency and access["remaining_kbps"] >= demand
            score = 0.08*snr-0.02*latency-5*loss-cost
            candidates.append({"access": access, "score": score, "feasible": feasible})
        feasible = [item for item in candidates if item["feasible"]]
        selected = max(feasible, key=lambda item: item["score"], default=max(candidates, key=lambda item: item["score"]))
        current = str(flow.get("current_access", ""))
        current_item = next((item for item in feasible if item["access"]["id"] == current), None)
        if current_item and selected["score"]-current_item["score"] <= abs(selected["score"])*float(hysteresis):
            selected = current_item
        allocated = min(demand, selected["access"]["remaining_kbps"])
        selected["access"]["remaining_kbps"] -= allocated
        assignments.append({"flow_id": str(flow.get("id", position)), "access_id": selected["access"]["id"], "requested_kbps": demand, "allocated_kbps": allocated, "fully_served": allocated >= demand, "score": selected["score"], "switched": bool(current and current != selected["access"]["id"])})
    return {"assignments": assignments, "remaining_capacity_kbps": {key: value["remaining_kbps"] for key, value in state.items()}, "unserved_flow_count": sum(not item["fully_served"] for item in assignments), "hysteresis": float(hysteresis)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flows", required=True)
    parser.add_argument("--accesses", required=True)
    parser.add_argument("--hysteresis", type=float, default=0.05)
    args = parser.parse_args()
    try:
        print(json.dumps(steer_traffic(json.loads(args.flows), json.loads(args.accesses), args.hysteresis), ensure_ascii=False))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
