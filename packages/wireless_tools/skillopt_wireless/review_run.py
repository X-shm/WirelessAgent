"""Offline, paired review of a completed SkillOpt training run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


VARIANTS = {
    "initial": "test_eval_baseline",
    "selected": "test_eval",
    "last": "test_eval_final",
}
SIGNALS = ("route_ok", "arguments_ok", "result_ok", "answer_ok")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _case_view(row: dict[str, Any]) -> dict[str, Any]:
    calls = row.get("tool_calls") or []
    return {
        "hard": row["hard"],
        "first_tool": calls[0].get("name") if calls else None,
        "signals": {name: bool(row.get(name)) for name in SIGNALS},
        "failure": row.get("fail_reason", ""),
    }


def _metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {"overall": rows}
    for row in rows:
        buckets.setdefault(row["task_type"], []).append(row)
    return {
        name: {
            "correct": sum(int(row["hard"]) for row in cases),
            "total": len(cases),
            "hard": sum(int(row["hard"]) for row in cases) / len(cases),
        }
        for name, cases in sorted(buckets.items())
    }


def build_review(run_dir: Path, output_dir: Path | None = None) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    summary_path = run_dir / "summary.json"
    if not summary_path.is_file():
        raise ValueError(f"completed run summary not found: {summary_path}")
    summary = _read_json(summary_path)
    last_skill = run_dir / "skills" / f"skill_v{summary['total_steps']:04d}.md"
    skill_paths = {
        "initial": Path(summary["config"]["skill_init"]),
        "selected": run_dir / "best_skill.md",
        "last": last_skill,
    }
    rows_by_variant: dict[str, list[dict[str, Any]]] = {}
    by_id: dict[str, dict[str, dict[str, Any]]] = {}
    for name, folder in VARIANTS.items():
        rows = _read_json(run_dir / folder / "rollouts.json")
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"empty or invalid rollout: {folder}")
        indexed = {str(row["id"]): row for row in rows}
        if len(indexed) != len(rows):
            raise ValueError(f"duplicate task IDs: {folder}")
        rows_by_variant[name] = rows
        by_id[name] = indexed
    ids = set(by_id["initial"])
    if any(set(items) != ids for items in by_id.values()):
        raise ValueError("initial, selected, and last rollouts do not cover identical task IDs")

    metrics = {name: _metrics(rows) for name, rows in rows_by_variant.items()}
    changes = []
    for task_id in sorted(ids):
        before = by_id["initial"][task_id]
        selected = by_id["selected"][task_id]
        last = by_id["last"][task_id]
        if before["task_type"] != selected["task_type"] or before["task_type"] != last["task_type"]:
            raise ValueError(f"task type changed for {task_id}")
        if before["hard"] == selected["hard"] == last["hard"]:
            continue
        changes.append({
            "id": task_id,
            "task_type": before["task_type"],
            "initial": _case_view(before),
            "selected": _case_view(selected),
            "last": _case_view(last),
            "selected_delta": int(selected["hard"]) - int(before["hard"]),
            "last_delta": int(last["hard"]) - int(before["hard"]),
            "attribution": "unverified; repeat the same case before attributing a change to skill text",
        })

    gates = {}
    for name in ("selected", "last"):
        gates[name] = {
            "overall_improved": metrics[name]["overall"]["hard"] > metrics["initial"]["overall"]["hard"],
            "no_category_regression": all(
                metrics[name][category]["hard"] >= baseline["hard"]
                for category, baseline in metrics["initial"].items() if category != "overall"
            ),
            "skill_under_8kb": skill_paths[name].stat().st_size <= 8_000,
        }
        gates[name]["passes_existing_gate"] = all(gates[name].values())

    artifact_hashes = {"summary.json": _sha256(summary_path)}
    for name, path in skill_paths.items():
        artifact_hashes[f"skill:{name}"] = _sha256(path)
    for name, folder in VARIANTS.items():
        artifact_hashes[f"rollout:{name}"] = _sha256(run_dir / folder / "rollouts.json")
    report = {
        "run": str(run_dir),
        "summary": {
            key: summary[key] for key in (
                "total_steps", "total_accepts", "total_rejects", "total_skips",
                "baseline_selection_hard", "best_selection_hard", "best_step",
            )
        },
        "skills": {name: str(path.resolve()) for name, path in skill_paths.items()},
        "artifact_sha256": artifact_hashes,
        "metrics": metrics,
        "gates_on_viewed_synthetic_test": gates,
        "changes": changes,
        "caution": "The existing synthetic test split has been inspected. This report diagnoses the run; it is not a fresh release holdout or evidence of causal improvement.",
    }
    destination = output_dir or run_dir / "review"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "review.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (destination / "review.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _markdown(report: dict[str, Any]) -> str:
    m = report["metrics"]
    lines = [
        "# SkillOpt 运行复核",
        "",
        f"运行目录：`{report['run']}`",
        "",
        "此表用于诊断已查看的合成 test 题，不能作为新的独立发布验收。逐题变化尚不能直接归因于技能文本。",
        "",
        "| 版本 | 正确/总数 | hard | 现有发布门槛 |",
        "|---|---:|---:|---|",
    ]
    for name, label in (("initial", "初始"), ("selected", "验证集选中"), ("last", "最后技能")):
        metric = m[name]["overall"]
        gate = "—" if name == "initial" else ("通过" if report["gates_on_viewed_synthetic_test"][name]["passes_existing_gate"] else "未通过")
        lines.append(f"| {label} | {metric['correct']}/{metric['total']} | {metric['hard']:.4f} | {gate} |")
    lines += ["", "## 各领域", "", "| 领域 | 初始 | 选中 | 最后 |", "|---|---:|---:|---:|"]
    for category in sorted(m["initial"]):
        if category == "overall":
            continue
        values = [f"{m[name][category]['correct']}/{m[name][category]['total']}" for name in ("initial", "selected", "last")]
        lines.append(f"| {category} | {' | '.join(values)} |")
    lines += ["", "## 有变化的题", "", "| ID | 领域 | 初始→选中→最后 | 首次失败信号（初始 / 选中 / 最后） |", "|---|---|---|---|"]
    for row in report["changes"]:
        grades = "→".join(str(row[name]["hard"]) for name in ("initial", "selected", "last"))
        failures = " / ".join(row[name]["failure"] or "无" for name in ("initial", "selected", "last"))
        lines.append(f"| {row['id']} | {row['task_type']} | {grades} | {failures} |")
    lines += ["", "详细首个工具与四项评分信号见 `review.json`。对变化题做重复调用后再判断技能作用。", ""]
    return "\n".join(lines)
