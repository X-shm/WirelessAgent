"""Offline regression checks for the non-publishable draft experiment path."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skillopt_wireless.__main__ import SEED_SKILL, _reviewed_manifest, evaluate, package, seal_selection
from skillopt_wireless.adapter import WirelessMCPDataLoader
from skillopt_wireless.reviewed_cases import freeze, freeze_draft
from skillopt_wireless.rollout import run_batch


def draft_rows() -> list[dict]:
    common = {"source_ref": "unit_test_only", "reviewer": "PENDING_PRODUCT_REVIEW",
              "review_status": "draft", "origin_type": "expert_authored", "tool": "q_function"}
    return [
        {**common, "id": "draft_train", "split": "train", "scenario_id": "draft_scenario_train",
         "question": "标准高斯右尾函数在零点取什么数值？", "kind": "tool_call",
         "arguments": {"mode": "qfunc", "values": "[0]"},
         "expected": {"output": [0.5]}, "answer_paths": ["/output"]},
        {**common, "id": "draft_selection", "split": "selection", "scenario_id": "draft_scenario_selection",
         "question": "请计算标准正态变量超过一的概率，并给出 Q 函数结果。", "kind": "tool_call",
         "arguments": {"mode": "qfunc", "values": "[1]"},
         "expected": {"output": [0.15865525393145707]}, "answer_paths": ["/output"]},
        {**common, "id": "draft_holdout", "split": "holdout", "scenario_id": "draft_scenario_holdout",
         "question": "要算 Q 函数，但还没有告诉你输入。", "kind": "ask_clarification",
         "answer_terms": ["输入值"]},
    ]


def write_rows(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


class DraftExperimentTest(unittest.TestCase):
    def test_draft_freeze_mock_and_release_guard(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wireless-draft-test-") as temp:
            root = Path(temp).resolve()
            source = root / "draft.jsonl"
            write_rows(source, draft_rows())
            frozen = root / "frozen"
            manifest = freeze_draft(source, frozen)
            self.assertEqual(manifest["kind"], "draft_experiment")
            self.assertFalse(manifest["publishable"])
            self.assertEqual(manifest["review_status"], "draft")
            self.assertEqual(manifest["cases_by_split"], {"train": 1, "selection": 1, "holdout": 1})
            self.assertTrue(all(row["review_status"] == "draft" for row in draft_rows()))
            self.assertTrue(all(json.loads(line)["review_status"] == "draft"
                                for line in source.read_text(encoding="utf-8").splitlines()))
            loader = WirelessMCPDataLoader(split_dir=str(frozen), split_mode="split_dir", seed=42)
            loader.setup({"train_size": 1})
            self.assertEqual(loader.train_items[0]["source"], "expert_draft")
            result = run_batch(loader.train_items, SEED_SKILL.read_text(encoding="utf-8"),
                               root / "mock-train", mock=True)
            self.assertEqual(result[0]["hard"], 1)
            run = root / "training"
            run.mkdir()
            (run / "config.json").write_text(json.dumps({"split_dir": str(frozen), "eval_test": False}), encoding="utf-8")
            (run / "summary.json").write_text(json.dumps({"best_step": 1}), encoding="utf-8")
            selected = run / "best_skill.md"
            selected.write_bytes(SEED_SKILL.read_bytes())
            seal_selection(run, frozen)
            evaluate(selected, root / "mock-eval", frozen, mock=True)
            report = json.loads((root / "mock-eval" / "comparison.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_kind"], "draft_experiment")
            self.assertEqual(report["dataset_kind"], "draft_experiment")
            self.assertFalse(report["publishable"])
            with self.assertRaisesRegex(SystemExit, "publication gate"):
                package(selected, root / "mock-eval" / "comparison.json", root / "release")
            # Even a mistakenly marked successful comparison must not package
            # when its dataset provenance still says draft_experiment.
            report.update(publishable=True, evaluation_kind="frozen_holdout", mock=False,
                          coverage_ok=True, repeats=2, unstable_direction_ids=[],
                          selection_provenance={"verified": True})
            (root / "mock-eval" / "comparison.json").write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "publication gate"):
                package(selected, root / "mock-eval" / "comparison.json", root / "release")
            manifest_path = frozen / "manifest.json"
            manifest["publishable"] = True
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "non-publishable"):
                _reviewed_manifest(frozen)

    def test_draft_gate_rejects_false_approval_and_cross_split_template(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wireless-draft-reject-") as temp:
            root = Path(temp).resolve()
            source = root / "draft.jsonl"
            rows = draft_rows()
            rows[0]["review_status"] = "approved"
            write_rows(source, rows)
            with self.assertRaisesRegex(ValueError, "must be draft"):
                freeze_draft(source, root / "invalid-approved")
            rows = draft_rows()
            rows[1]["question"] = "标准高斯右尾函数在一点取什么数值？"
            write_rows(source, rows)
            with self.assertRaisesRegex(ValueError, "near-duplicate"):
                freeze_draft(source, root / "invalid-leak")
            write_rows(source, draft_rows())
            with self.assertRaisesRegex(ValueError, "must be approved"):
                freeze(source, root / "invalid-reviewed")


if __name__ == "__main__":
    unittest.main()
