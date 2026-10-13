"""Local SkillOpt workflow: prepare, smoke, preflight, train, evaluate, package."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import ROOT

DATA_DIR = ROOT / "skillopt_data" / "splits"
RUNS_DIR = ROOT / "skillopt_runs"
SEED_SKILL = ROOT / "skills" / "wireless_mcp" / "seed_skill.md"
CONFIG = ROOT / "skillopt_wireless" / "config.yaml"


def _require_dataset() -> dict:
    path = DATA_DIR / "manifest.json"
    if not path.is_file():
        raise SystemExit("Run 'python -m skillopt_wireless prepare' first")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not manifest["complete"]:
        raise SystemExit(f"Dataset is incomplete: {manifest['gaps']}")
    return manifest


def _require_key() -> None:
    if not os.environ.get("DEEPSEEK_API_KEY", "").strip():
        raise SystemExit("Set DEEPSEEK_API_KEY in the environment; never put it in YAML")


def _configure_deepseek_backend(cfg: dict) -> None:
    """Set both live SkillOpt clients, including configs imported earlier."""
    from skillopt.model import configure_openai_compatible

    key = os.environ["DEEPSEEK_API_KEY"].strip()
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    configure_openai_compatible(
        optimizer_base_url=base_url,
        optimizer_api_key=key,
        optimizer_model=cfg["optimizer_model"],
        target_base_url=base_url,
        target_api_key=key,
        target_model=cfg["target_model"],
    )


def _check_optimizer() -> dict:
    """Fail before paid rollouts if the reflection model cannot respond."""
    from skillopt.model.openai_compatible_backend import chat_optimizer
    from skillopt.utils.json_utils import extract_json

    answer, usage = chat_optimizer(
        system="Return a short JSON object and nothing else.",
        user='Return exactly {"ok": true}.',
        max_completion_tokens=1024,
        retries=1,
        stage="preflight_optimizer",
    )
    parsed = extract_json(answer)
    if not isinstance(parsed, dict) or parsed.get("ok") is not True:
        raise RuntimeError("Optimizer preflight did not return the expected JSON object")
    return usage


def _adapter(*, split_dir: Path = DATA_DIR, output_root: Path | None = None, reuse_root: Path | None = None):
    from .adapter import WirelessMCPAdapter

    return WirelessMCPAdapter(
        split_dir=str(split_dir),
        output_root=str(output_root) if output_root else None,
        reuse_root=str(reuse_root) if reuse_root else None,
    )


def _load_items(split: str) -> list[dict]:
    return json.loads((DATA_DIR / split / "items.json").read_text(encoding="utf-8"))


def _report(results: list[dict]) -> dict:
    by_type: dict[str, list[dict]] = {}
    by_kind: dict[str, list[dict]] = {}
    for item in results:
        by_type.setdefault(item["task_type"], []).append(item)
        by_kind.setdefault(item.get("kind", "tool_call"), []).append(item)
    def metrics(items: list[dict]) -> dict:
        return {
            "count": len(items),
            "hard": sum(item["hard"] for item in items) / len(items),
            "route": sum(item["route_ok"] for item in items) / len(items),
            "arguments": sum(item["arguments_ok"] for item in items) / len(items),
            "result": sum(item["result_ok"] for item in items) / len(items),
            "answer": sum(item["answer_ok"] for item in items) / len(items),
        }
    return {
        "overall": metrics(results),
        "by_product": {name: metrics(items) for name, items in sorted(by_type.items())},
        "by_kind": {name: metrics(items) for name, items in sorted(by_kind.items())},
        "failures": [
            {"id": row["id"], "reason": row["fail_reason"]}
            for row in results if not row["hard"]
        ],
    }


def prepare() -> None:
    from .build_dataset import build

    report = asyncio.run(build(DATA_DIR))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["complete"]:
        raise SystemExit(2)


def smoke() -> None:
    _require_dataset()
    from .cases import SPLITS
    from .rollout import run_batch

    reports = {}
    for split in SPLITS:
        results = run_batch(
            _load_items(split), SEED_SKILL.read_text(encoding="utf-8"),
            RUNS_DIR / "mock-smoke" / split, mock=True,
        )
        reports[split] = _report(results)
    print(json.dumps(
        {split: report["overall"] for split, report in reports.items()},
        ensure_ascii=False, indent=2,
    ))
    if any(report["overall"]["hard"] != 1.0 for report in reports.values()):
        print(json.dumps(
            {split: report["failures"] for split, report in reports.items() if report["failures"]},
            ensure_ascii=False, indent=2,
        ))
        raise SystemExit(2)


def preflight() -> None:
    _require_dataset()
    _require_key()
    from skillopt.config import flatten_config, load_config
    from mcp_server.catalog import load_catalog
    from .rollout import DeepSeekTarget

    cfg = flatten_config(load_config(str(CONFIG)))
    _configure_deepseek_backend(cfg)
    optimizer_usage = _check_optimizer()
    catalog = load_catalog()
    if len(catalog) != 144:
        raise SystemExit("Expected 144 registered tools")
    functions = [{
        "type": "function",
        "function": {
            "name": spec.name,
            "description": spec.description,
            "parameters": spec.input_schema,
        },
    } for spec in catalog.values()]
    item = _load_items("test")[0]
    response = DeepSeekTarget().complete(
        [
            {"role": "system", "content": "必须选择一个无线计算工具。"},
            {"role": "user", "content": item["question"]},
        ],
        functions, required=True, item=item,
    )
    print(json.dumps({
        "optimizer_model": cfg["optimizer_model"],
        "optimizer_usage": optimizer_usage,
        "functions_sent": len(functions),
        "tool_calls_received": len(response["tool_calls"]),
        "usage": response.get("usage"),
    }, ensure_ascii=False, indent=2))
    if not response["tool_calls"]:
        raise SystemExit("Provider accepted request but did not return a tool call")


def optimizer_preflight() -> None:
    _require_key()
    from skillopt.config import flatten_config, load_config

    cfg = flatten_config(load_config(str(CONFIG)))
    _configure_deepseek_backend(cfg)
    usage = _check_optimizer()
    print(json.dumps({
        "optimizer_model": cfg["optimizer_model"],
        "optimizer_responded": True,
        "usage": usage,
    }, ensure_ascii=False, indent=2))


def _reviewed_manifest(cases: Path) -> dict:
    manifest_path = cases / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Frozen dataset manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("kind") not in {"reviewed_business", "draft_experiment"}
            or not manifest.get("complete") or not manifest.get("holdout_frozen")):
        raise SystemExit("--cases must refer to a complete frozen reviewed or draft-experiment dataset")
    if manifest["kind"] == "draft_experiment" and (manifest.get("publishable") is not False or manifest.get("review_status") != "draft"):
        raise SystemExit("Draft experiment manifest must remain non-publishable and draft")
    registry_hash = hashlib.sha256((ROOT / "tool_registry.json").read_bytes()).hexdigest()
    if manifest.get("registry_sha256") != registry_hash:
        raise SystemExit("Tool registry changed since the reviewed dataset was frozen")
    for split in ("train", "val", "test"):
        item_path = cases / split / "items.json"
        if not item_path.is_file() or hashlib.sha256(item_path.read_bytes()).hexdigest() != manifest.get("split_sha256", {}).get(split):
            raise SystemExit(f"Frozen dataset content changed: {item_path}")
    return manifest


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal_selection(run: Path, cases: Path) -> dict:
    """Record the validation-selected candidate before opening the holdout."""
    run, cases = run.resolve(), cases.resolve()
    _reviewed_manifest(cases)
    config_path, summary_path = run / "config.json", run / "summary.json"
    selected_path = run / "best_skill.md"
    if not all(path.is_file() for path in (config_path, summary_path, selected_path)):
        raise SystemExit("Completed training config, summary, or best_skill.md is missing")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if Path(config.get("split_dir", "")).resolve() != cases or config.get("eval_test") is not False:
        raise SystemExit("This run did not train on the reviewed dataset with holdout evaluation disabled")
    seal = {
        "kind": "selection_seal",
        "run": str(run),
        "dataset_manifest_sha256": _sha256(cases / "manifest.json"),
        "candidate_sha256": _sha256(selected_path),
        "config_sha256": _sha256(config_path),
        "summary_sha256": _sha256(summary_path),
        "best_step": json.loads(summary_path.read_text(encoding="utf-8")).get("best_step"),
    }
    seal_path = run / "selection.json"
    if seal_path.exists():
        if json.loads(seal_path.read_text(encoding="utf-8")) != seal:
            raise SystemExit("Selection seal already exists with different content")
        return seal
    seal_path.write_text(json.dumps(seal, ensure_ascii=False, indent=2), encoding="utf-8")
    return seal


def _selection_provenance(skill: Path, cases: Path) -> dict:
    """Verify the candidate was selected by this dataset's validation split."""
    result = {"verified": False, "reason": "candidate is not a sealed best_skill.md"}
    if skill.name != "best_skill.md":
        return result
    run = skill.resolve().parent
    seal_path, config_path, summary_path = run / "selection.json", run / "config.json", run / "summary.json"
    if not all(path.is_file() for path in (seal_path, config_path, summary_path)):
        return result
    try:
        seal = json.loads(seal_path.read_text(encoding="utf-8"))
        config = json.loads(config_path.read_text(encoding="utf-8"))
        expected = {
            "run": str(run),
            "dataset_manifest_sha256": _sha256(cases / "manifest.json"),
            "candidate_sha256": _sha256(skill),
            "config_sha256": _sha256(config_path),
            "summary_sha256": _sha256(summary_path),
        }
        if (seal.get("kind") != "selection_seal"
                or any(seal.get(key) != value for key, value in expected.items())
                or Path(config.get("split_dir", "")).resolve() != cases.resolve()
                or config.get("eval_test") is not False):
            return {"verified": False, "reason": "selection seal, candidate, or dataset changed"}
    except (OSError, ValueError, TypeError, KeyError):
        return result
    return {"verified": True, "run": str(run), "best_step": seal.get("best_step")}


def train(output: Path | None, reuse_from: Path | None = None, cases: Path | None = None) -> None:
    manifest = _reviewed_manifest(cases) if cases else _require_dataset()
    if sys.platform == "win32" and not sys.flags.utf8_mode:
        raise SystemExit("On Windows, run Python with -X utf8 for SkillOpt training")
    _require_key()
    from skillopt.config import flatten_config, load_config
    from skillopt.engine.trainer import ReflACTTrainer

    raw = load_config(str(CONFIG))
    cfg = flatten_config(raw)
    split_dir = cases.resolve() if cases else DATA_DIR
    cfg["split_dir"] = str(split_dir)
    if cases:
        # The holdout remains unavailable to SkillOpt's training-time evaluations.
        cfg["eval_test"] = False
        cfg["sel_env_num"] = manifest["cases_by_split"]["selection"]
        cfg["test_env_num"] = 0
        cfg["train_size"] = manifest["cases_by_split"]["train"]
        cfg["batch_size"] = min(cfg["batch_size"], cfg["train_size"])
        cfg["max_turns"] = max(cfg["max_turns"], manifest.get("max_workflow_steps", 0) + 1)
    cfg["skill_init"] = str(SEED_SKILL)
    cfg["out_root"] = str((output or RUNS_DIR / datetime.now().strftime("train-%Y%m%d-%H%M%S")).resolve())
    if (Path(cfg["out_root"]) / "summary.json").is_file():
        raise SystemExit("Training is already complete in this output directory; choose a new --output")
    reuse_root = reuse_from.resolve() if reuse_from else None
    if reuse_root is not None:
        if not reuse_root.is_dir() or not (reuse_root / "config.json").is_file():
            raise SystemExit("--reuse-from must point to a previous SkillOpt run directory")
        if reuse_root == Path(cfg["out_root"]):
            raise SystemExit("--reuse-from and --output must be different directories")
    _configure_deepseek_backend(cfg)
    _check_optimizer()
    adapter = _adapter(split_dir=split_dir, output_root=Path(cfg["out_root"]), reuse_root=reuse_root)
    summary = ReflACTTrainer(cfg, adapter).train()
    if cases:
        seal_selection(Path(cfg["out_root"]), split_dir)
    print(json.dumps({
        "output": cfg["out_root"],
        "summary": summary,
    }, ensure_ascii=False, indent=2, default=str))


def evaluate(skill: Path, output: Path | None, cases: Path | None = None, *, mock: bool = False, repeats: int = 1) -> None:
    if repeats < 1:
        raise SystemExit("--repeats must be at least 1")
    manifest = _reviewed_manifest(cases) if cases else _require_dataset()
    if not mock:
        _require_key()
    from .rollout import run_batch

    if not skill.is_file():
        raise SystemExit(f"Skill not found: {skill}")
    root = (output or RUNS_DIR / datetime.now().strftime("eval-%Y%m%d-%H%M%S")).resolve()
    if cases and root.exists() and any(root.iterdir()):
        raise SystemExit("Frozen holdout evaluation output already exists; choose a new --output")
    split_dir = cases.resolve() if cases else DATA_DIR
    items = json.loads((split_dir / "test" / "items.json").read_text(encoding="utf-8"))
    if not items:
        raise SystemExit("Holdout is empty")
    max_turns = max(3, manifest.get("max_workflow_steps", 0) + 1)
    all_baseline, all_candidate, paired_cases, rounds = [], [], [], []
    directions: dict[str, set[int]] = {}
    for repeat in range(1, repeats + 1):
        repeat_root = root if repeats == 1 else root / f"repeat-{repeat:02d}"
        baseline = run_batch(items, SEED_SKILL.read_text(encoding="utf-8"), repeat_root / "seed", mock=mock, max_turns=max_turns)
        candidate = run_batch(items, skill.read_text(encoding="utf-8"), repeat_root / "candidate", mock=mock, max_turns=max_turns)
        before_round, after_round = _report(baseline), _report(candidate)
        round_no_regression = all(
            after_round["by_product"][name]["hard"] >= before_round["by_product"][name]["hard"]
            for name in before_round["by_product"]
        )
        rounds.append({
            "repeat": repeat, "baseline": before_round["overall"],
            "candidate": after_round["overall"],
            "overall_improved": after_round["overall"]["hard"] > before_round["overall"]["hard"],
            "no_category_regression": round_no_regression,
        })
        for before_row, after_row in zip(baseline, candidate):
            if before_row["id"] != after_row["id"]:
                raise RuntimeError("Paired evaluation case order changed")
            direction = int(after_row["hard"]) - int(before_row["hard"])
            directions.setdefault(before_row["id"], set()).add(direction)
            paired_cases.append({
                "repeat": repeat, "id": before_row["id"],
                "task_type": before_row["task_type"], "kind": before_row.get("kind", "tool_call"),
                "seed_hard": before_row["hard"], "candidate_hard": after_row["hard"],
                "seed_failure": before_row["fail_reason"],
                "candidate_failure": after_row["fail_reason"],
            })
        all_baseline.extend(baseline)
        all_candidate.extend(candidate)
    before, after = _report(all_baseline), _report(all_candidate)
    no_category_regression = all(row["no_category_regression"] for row in rounds)
    overall_improved_each_round = all(row["overall_improved"] for row in rounds)
    unstable_direction_ids = sorted(case_id for case_id, values in directions.items() if len(values) > 1)
    required_products = {entry["product"] for entry in json.loads(
        (ROOT / "tool_registry.json").read_text(encoding="utf-8")
    )["tools"]}
    covered_products = set(before["by_product"])
    covered_kinds = {item.get("kind", "tool_call") for item in items}
    required_kinds = {"tool_call", "ask_clarification"}
    if cases and any(manifest.get("coverage", {}).get(split, {}).get("workflow_count", 0)
                     for split in ("train", "selection", "holdout")):
        required_kinds.add("tool_workflow")
    coverage_missing = {
        "products": sorted(required_products - covered_products),
        "kinds": sorted(required_kinds - covered_kinds),
    }
    coverage_ok = not coverage_missing["products"] and not coverage_missing["kinds"]
    provenance = _selection_provenance(skill, split_dir) if cases else {"verified": False, "reason": "viewed synthetic diagnostic"}
    pass_gate = (
        overall_improved_each_round
        and no_category_regression
        and repeats >= 2 and not unstable_direction_ids
        and skill.stat().st_size <= 8_000
        and coverage_ok and provenance["verified"]
        and cases is not None and not mock
        and manifest.get("kind") == "reviewed_business"
        and manifest.get("publishable", True) is True
    )
    report = {
        "registry_sha256": manifest["registry_sha256"],
        "dataset_manifest_sha256": hashlib.sha256(
            (split_dir / "manifest.json").read_bytes()
        ).hexdigest(),
        "evaluation_kind": (
            "draft_experiment" if cases and manifest.get("kind") == "draft_experiment" else
            "frozen_holdout" if cases else "viewed_synthetic_diagnostic"
        ),
        "dataset_kind": manifest.get("kind", "synthetic"),
        "mock": mock,
        "candidate_path": str(skill.resolve()),
        "seed_sha256": hashlib.sha256(SEED_SKILL.read_bytes()).hexdigest(),
        "candidate_sha256": hashlib.sha256(skill.read_bytes()).hexdigest(),
        "target_model": os.environ.get("DEEPSEEK_TARGET_MODEL", "deepseek-flash"),
        "baseline": before,
        "candidate": after,
        "no_category_regression": no_category_regression,
        "overall_improved_each_round": overall_improved_each_round,
        "repeats": repeats,
        "rounds": rounds,
        "unstable_direction_ids": unstable_direction_ids,
        "coverage": manifest.get("coverage", {}).get("holdout"),
        "coverage_missing": coverage_missing,
        "coverage_ok": coverage_ok,
        "selection_provenance": provenance,
        "publishable": pass_gate,
        "paired_cases": paired_cases,
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "comparison.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "output": str(root),
        "baseline": before["overall"],
        "candidate": after["overall"],
        "publishable": pass_gate,
    }, ensure_ascii=False, indent=2))


def package(skill: Path, comparison: Path, output: Path) -> None:
    report = json.loads(comparison.read_text(encoding="utf-8"))
    if (not report.get("publishable") or report.get("evaluation_kind") != "frozen_holdout"
            or report.get("dataset_kind") != "reviewed_business"
            or report.get("mock") or not report.get("dataset_manifest_sha256")
            or not report.get("selection_provenance", {}).get("verified")
            or not report.get("coverage_ok") or report.get("repeats", 0) < 2
            or report.get("unstable_direction_ids")):
        raise SystemExit("The independent evaluation did not pass the publication gate")
    if report.get("registry_sha256") != hashlib.sha256((ROOT / "tool_registry.json").read_bytes()).hexdigest():
        raise SystemExit("Tool registry differs from the evaluated version")
    body = skill.read_text(encoding="utf-8")
    digest = hashlib.sha256(skill.read_bytes()).hexdigest()
    if digest != report["candidate_sha256"]:
        raise SystemExit("Skill content differs from the evaluated candidate")
    output.mkdir(parents=True, exist_ok=False)
    frontmatter = (
        "---\nname: wireless_mcp\n"
        "description: 无线通信 MCP 工具路由与参数填写技能。\n"
        "user-invocable: true\n---\n\n"
    )
    (output / "SKILL.md").write_text(frontmatter + body, encoding="utf-8")
    release = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "skill_sha256": digest,
        "registry_sha256": report["registry_sha256"],
        "dataset_manifest_sha256": report["dataset_manifest_sha256"],
        "selection_provenance": report["selection_provenance"],
        "holdout_origin": (report.get("coverage") or {}).get("by_origin", {}),
        "target_model": report["target_model"],
        "baseline_hard": report["baseline"]["overall"]["hard"],
        "candidate_hard": report["candidate"]["overall"]["hard"],
        "repeats": report["repeats"],
        "requires_manual_approval": True,
    }
    (output / "manifest.json").write_text(
        json.dumps(release, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(release, ensure_ascii=False, indent=2))


def review_run(run: Path, output: Path | None) -> None:
    from .review_run import build_review

    report = build_review(run, output)
    print(json.dumps({
        "review": str((output or run / "review").resolve()),
        "initial": report["metrics"]["initial"]["overall"],
        "selected": report["metrics"]["selected"]["overall"],
        "last": report["metrics"]["last"]["overall"],
        "changed_cases": len(report["changes"]),
    }, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "smoke", "preflight", "optimizer-preflight"):
        commands.add_parser(name)
    train_parser = commands.add_parser("train")
    train_parser.add_argument("--output", type=Path)
    train_parser.add_argument("--reuse-from", type=Path)
    train_parser.add_argument("--cases", type=Path, help="Frozen reviewed or draft-experiment dataset; never use its holdout during training")
    eval_parser = commands.add_parser("evaluate")
    eval_parser.add_argument("--skill", type=Path, required=True)
    eval_parser.add_argument("--output", type=Path)
    eval_parser.add_argument("--cases", type=Path, help="Frozen reviewed dataset or non-publishable draft experiment")
    eval_parser.add_argument("--mock", action="store_true", help="Offline plumbing check; cannot pass release gate")
    eval_parser.add_argument("--repeats", type=int, default=1, help="Use at least 2 for release stability gate")
    freeze_parser = commands.add_parser("freeze-reviewed")
    freeze_parser.add_argument("--input", type=Path, required=True)
    freeze_parser.add_argument("--output", type=Path, required=True)
    draft_parser = commands.add_parser("freeze-draft", help="Freeze expert-authored draft cases for non-publishable local experiments")
    draft_parser.add_argument("--input", type=Path, required=True)
    draft_parser.add_argument("--output", type=Path, required=True)
    seal_parser = commands.add_parser("seal-selection")
    seal_parser.add_argument("--run", type=Path, required=True)
    seal_parser.add_argument("--cases", type=Path, required=True)
    package_parser = commands.add_parser("package")
    package_parser.add_argument("--skill", type=Path, required=True)
    package_parser.add_argument("--comparison", type=Path, required=True)
    package_parser.add_argument("--output", type=Path, required=True)
    review_parser = commands.add_parser("review-run")
    review_parser.add_argument("--run", type=Path, required=True)
    review_parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "smoke":
        smoke()
    elif args.command == "preflight":
        preflight()
    elif args.command == "optimizer-preflight":
        optimizer_preflight()
    elif args.command == "train":
        train(args.output, args.reuse_from, args.cases)
    elif args.command == "evaluate":
        evaluate(args.skill, args.output, args.cases, mock=args.mock, repeats=args.repeats)
    elif args.command == "freeze-reviewed":
        from .reviewed_cases import freeze
        try:
            result = freeze(args.input, args.output)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "freeze-draft":
        from .reviewed_cases import freeze_draft
        try:
            result = freeze_draft(args.input, args.output)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "seal-selection":
        print(json.dumps(seal_selection(args.run, args.cases), ensure_ascii=False, indent=2))
    elif args.command == "review-run":
        review_run(args.run, args.output)
    else:
        package(args.skill, args.comparison, args.output)


if __name__ == "__main__":
    main()
