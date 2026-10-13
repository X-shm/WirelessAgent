"""Priority-aware LTE PRB allocation using converted MCS/TBS tables."""
from __future__ import annotations
import argparse
import json
import sys

from link_adaptation_optimizer import optimize_link
from lte_tbs import tbs


def allocate_resources(users, total_prbs, table="PDSCH", margin_db=2.0):
    if not isinstance(users, list) or not users or not 1 <= int(total_prbs) <= 110:
        raise ValueError("users must be nonempty and total_prbs 1..110")
    states = []
    for position, user in enumerate(users):
        if not isinstance(user, dict) or "snr_db" not in user:
            raise ValueError("each user requires snr_db")
        recommendation = optimize_link(user["snr_db"], 1, table, int(user.get("layers", 1)), margin_db)
        priority = float(user.get("priority", 1.0))
        demand = None if "demand_kbps" not in user else float(user["demand_kbps"])
        if priority <= 0 or (demand is not None and demand < 0):
            raise ValueError("priority must be positive and demand_kbps nonnegative")
        states.append({"id": str(user.get("id", position)), "priority": priority, "demand_kbps": demand, "layers": int(user.get("layers", 1)), "allocated_prbs": 0, "recommendation": recommendation})
    for _ in range(int(total_prbs)):
        best, best_utility = None, -1.0
        for state in states:
            current = state["allocated_prbs"]
            rec = state["recommendation"]
            before = 0 if current == 0 else tbs(current, rec["itbs"], state["layers"])
            after = tbs(current+1, rec["itbs"], state["layers"])
            remaining = float("inf") if state["demand_kbps"] is None else max(state["demand_kbps"]-before, 0.0)
            useful = min(after-before, remaining) if remaining != float("inf") else after-before
            utility = state["priority"]*(useful if useful > 0 else 0.01*(after-before))/(1+current)
            if utility > best_utility:
                best, best_utility = state, utility
        best["allocated_prbs"] += 1
    allocations = []
    for state, user in zip(states, users):
        count, rec = state["allocated_prbs"], state["recommendation"]
        bits = 0 if count == 0 else tbs(count, rec["itbs"], int(user.get("layers", 1)))
        demand = state["demand_kbps"]
        allocations.append({"id": state["id"], "allocated_prbs": count, "mcs": rec["recommended_mcs"], "modulation": rec["modulation"], "tbs_bits_per_subframe": bits, "estimated_kbps": bits, "demand_kbps": demand, "demand_met": None if demand is None else bits >= demand})
    return {"total_prbs": int(total_prbs), "allocated_prbs": sum(item["allocated_prbs"] for item in allocations), "allocations": allocations, "method": "weighted_marginal_tbs"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", required=True)
    parser.add_argument("--total_prbs", type=int, required=True)
    parser.add_argument("--table", choices=["PDSCH", "PDSCHTable2", "PDSCHTable3", "PUSCH"], default="PDSCH")
    parser.add_argument("--margin_db", type=float, default=2.0)
    args = parser.parse_args()
    try:
        print(json.dumps(allocate_resources(json.loads(args.users), args.total_prbs, args.table, args.margin_db), ensure_ascii=False))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
