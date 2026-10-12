"""Build auditable 5QI-oriented QoS suggestions from service requirements."""
from __future__ import annotations
import argparse
import json
import sys


_SERVICE_DEFAULTS = {
    "voice": (1, "GBR", 100, 1e-2),
    "live_video": (2, "GBR", 150, 1e-3),
    "gaming": (3, "GBR", 50, 1e-3),
    "ims_signaling": (5, "Non-GBR", 100, 1e-6),
    "buffered_video": (6, "Non-GBR", 300, 1e-6),
    "web": (9, "Non-GBR", 300, 1e-6),
    "industrial": (80, "GBR", 10, 1e-6),
}


def build_qos_policy(services, link_capacity_kbps=None, reserve_fraction=0.9):
    if not isinstance(services, list) or not services:
        raise ValueError("services must be a nonempty array")
    if not 0 < float(reserve_fraction) <= 1 or (link_capacity_kbps is not None and float(link_capacity_kbps) < 0):
        raise ValueError("reserve_fraction must be in (0,1] and link capacity nonnegative")
    policies, total_gfbr = [], 0.0
    for position, service in enumerate(services):
        kind = str(service.get("service_type", "web")).lower()
        five_qi, resource_type, default_pdb, default_per = _SERVICE_DEFAULTS.get(kind, _SERVICE_DEFAULTS["web"])
        pdb = float(service.get("latency_ms", default_pdb))
        per = float(service.get("packet_error_rate", default_per))
        gfbr = float(service.get("guaranteed_kbps", 0 if resource_type == "Non-GBR" else service.get("max_kbps", 0)))
        mfbr = float(service.get("max_kbps", max(gfbr, 0)))
        if gfbr < 0 or mfbr < gfbr or pdb <= 0 or not 0 <= per <= 1:
            raise ValueError("invalid rate, latency or packet-error requirement")
        total_gfbr += gfbr
        policies.append({"service_id": str(service.get("id", position)), "service_type": kind, "five_qi": int(service.get("five_qi", five_qi)), "resource_type": resource_type, "priority": int(service.get("priority", 5)), "packet_delay_budget_ms": pdb, "packet_error_rate": per, "gfbr_kbps": gfbr, "mfbr_kbps": mfbr, "decision_basis": "service_template_with_explicit_overrides"})
    capacity = None if link_capacity_kbps is None else float(link_capacity_kbps)
    feasible = capacity is None or total_gfbr <= capacity*float(reserve_fraction)
    return {"qos_data": policies, "total_gfbr_kbps": total_gfbr, "link_capacity_kbps": capacity, "reserve_fraction": float(reserve_fraction), "capacity_feasible": feasible, "warning": None if feasible else "GBR 总和超过链路可承诺容量；降低 GBR、扩容或分流"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--services", required=True)
    parser.add_argument("--link_capacity_kbps", type=float)
    parser.add_argument("--reserve_fraction", type=float, default=0.9)
    args = parser.parse_args()
    try:
        print(json.dumps(build_qos_policy(json.loads(args.services), args.link_capacity_kbps, args.reserve_fraction), ensure_ascii=False))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
