"""Validate QoS/steering decisions against link capacity and observed KPIs."""
from __future__ import annotations
import argparse
import json
import sys


def validate_policy(qos_data, link_capacity_kbps, observed=None, reserve_fraction=0.9):
    if not isinstance(qos_data, list):
        raise ValueError("qos_data must be an array")
    if float(link_capacity_kbps) < 0 or not 0 < float(reserve_fraction) <= 1:
        raise ValueError("link capacity must be nonnegative and reserve_fraction in (0,1]")
    capacity = float(link_capacity_kbps)*float(reserve_fraction)
    violations, identifiers, total_gfbr = [], set(), 0.0
    observed = {} if observed is None else observed
    for position, item in enumerate(qos_data):
        identifier = str(item.get("service_id", position))
        if identifier in identifiers:
            violations.append({"service_id": identifier, "type": "duplicate_service_id"})
        identifiers.add(identifier)
        gfbr, mfbr = float(item.get("gfbr_kbps", 0)), float(item.get("mfbr_kbps", 0))
        if gfbr < 0 or mfbr < gfbr:
            violations.append({"service_id": identifier, "type": "invalid_rate_order", "gfbr_kbps": gfbr, "mfbr_kbps": mfbr})
        total_gfbr += max(gfbr, 0)
        actual = observed.get(identifier, {})
        if "latency_ms" in actual and float(actual["latency_ms"]) > float(item.get("packet_delay_budget_ms", float("inf"))):
            violations.append({"service_id": identifier, "type": "latency_budget_exceeded", "actual": float(actual["latency_ms"]), "limit": float(item["packet_delay_budget_ms"])})
        if "packet_error_rate" in actual and float(actual["packet_error_rate"]) > float(item.get("packet_error_rate", 1)):
            violations.append({"service_id": identifier, "type": "packet_error_rate_exceeded", "actual": float(actual["packet_error_rate"]), "limit": float(item["packet_error_rate"])})
    if total_gfbr > capacity:
        violations.append({"type": "aggregate_gfbr_exceeds_reserved_capacity", "total_gfbr_kbps": total_gfbr, "reserved_capacity_kbps": capacity})
    return {"accepted": not violations, "violations": violations, "total_gfbr_kbps": total_gfbr, "reserved_capacity_kbps": capacity, "rollback_recommended": bool(violations)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qos_data", required=True)
    parser.add_argument("--link_capacity_kbps", type=float, required=True)
    parser.add_argument("--observed", default="{}")
    parser.add_argument("--reserve_fraction", type=float, default=0.9)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_policy(json.loads(args.qos_data), args.link_capacity_kbps, json.loads(args.observed), args.reserve_fraction), ensure_ascii=False))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
