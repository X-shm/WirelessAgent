"""Compare before/after radio KPIs and enforce optimization acceptance constraints."""
from __future__ import annotations
import argparse
import json
import math
import sys


_LOWER_IS_BETTER = {"ber", "bler", "evm", "evm_percent", "latency_ms", "delay_ms", "packet_loss", "prb_usage", "power_w", "frequency_offset_hz", "timing_offset_samples"}


def validate_closed_loop(before, after, constraints=None, weights=None):
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise ValueError("before and after must be metric objects")
    common = sorted(set(before)&set(after))
    if not common:
        raise ValueError("before and after have no common metrics")
    weights = {} if weights is None else weights
    comparisons, weighted, weight_sum = {}, 0.0, 0.0
    for metric in common:
        old, new = float(before[metric]), float(after[metric])
        if not math.isfinite(old) or not math.isfinite(new):
            raise ValueError("metrics must be finite")
        lower = metric.lower() in _LOWER_IS_BETTER
        signed_change = (old-new) if lower else (new-old)
        normalized = signed_change/max(abs(old), 1e-12)
        weight = float(weights.get(metric, 1.0))
        weighted += weight*normalized
        weight_sum += abs(weight)
        comparisons[metric] = {"before": old, "after": new, "direction": "lower" if lower else "higher", "improvement_fraction": normalized, "result": "improved" if signed_change > 0 else "unchanged" if signed_change == 0 else "degraded"}
    violations = []
    for metric, rule in (constraints or {}).items():
        if metric not in after or not isinstance(rule, dict):
            continue
        value = float(after[metric])
        if "min" in rule and value < float(rule["min"]):
            violations.append({"metric": metric, "rule": "min", "required": float(rule["min"]), "actual": value})
        if "max" in rule and value > float(rule["max"]):
            violations.append({"metric": metric, "rule": "max", "required": float(rule["max"]), "actual": value})
    score = weighted/weight_sum if weight_sum else 0.0
    return {"accepted": not violations and score >= 0, "score": score, "comparisons": comparisons, "constraint_violations": violations, "rollback_recommended": bool(violations or score < 0)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--constraints", default="{}")
    parser.add_argument("--weights", default="{}")
    args = parser.parse_args()
    try:
        result = validate_closed_loop(json.loads(args.before), json.loads(args.after), json.loads(args.constraints), json.loads(args.weights))
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
