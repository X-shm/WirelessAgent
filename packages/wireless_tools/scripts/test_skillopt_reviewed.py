"""Offline checks for reviewed-case isolation, MCP verification and release gate."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skillopt_wireless.__main__ import SEED_SKILL, _selection_provenance, evaluate, package, seal_selection
from skillopt_wireless.adapter import WirelessMCPDataLoader
from skillopt_wireless.reviewed_cases import _validate_rows, freeze
from skillopt_wireless.rollout import run_batch
from skillopt_wireless.scoring import grade_case


def sample_rows() -> list[dict]:
    common = {"source_ref": "unit_test_only", "reviewer": "test", "review_status": "approved", "origin_type": "expert_authored", "tool": "q_function"}
    return [
        {**common, "id": "test_train", "split": "train", "scenario_id": "scenario_train",
         "question": "测试题：计算 Q(1)", "kind": "tool_call",
         "arguments": {"mode": "qfunc", "values": "[1]"},
         "expected": {"output": [0.15865525393145707]}, "answer_paths": ["/output"]},
        {**common, "id": "test_selection", "split": "selection", "scenario_id": "scenario_selection",
         "question": "测试题：计算 Q(0)", "kind": "tool_call",
         "arguments": {"mode": "qfunc", "values": "[0]"},
         "expected": {"output": [0.5]}, "answer_paths": ["/output"]},
        {**common, "id": "test_holdout", "split": "holdout", "scenario_id": "scenario_holdout",
         "question": "测试题：请计算 Q 函数", "kind": "ask_clarification",
         "answer_terms": ["输入值"]},
    ]


class ReviewedCasesTest(unittest.TestCase):
    def test_answer_paths_require_requested_field_and_allow_file_artifact(self) -> None:
        item = {"source": "reviewed_business", "kind": "tool_call", "tool": "example",
                "arguments": {}, "expected": {"requested": 1, "other": 2},
                "answer_paths": ["/requested"]}
        calls = [{"name": "example", "arguments": {}, "result": item["expected"], "is_error": False}]
        self.assertEqual(grade_case(item, calls, '<answer>{"other":2}</answer>')["answer_ok"], False)
        self.assertEqual(grade_case(item, calls, '<answer>{"requested":1}</answer>')["hard"], 1)
        item["expected"] = {"artifacts": {"file": "<DATA_ROOT>/output.npz"}}
        item["answer_paths"] = ["/artifacts/file"]
        calls[0]["result"] = item["expected"]
        self.assertEqual(grade_case(item, calls, '<answer>{"artifacts":{"file":"<DATA_ROOT>/output.npz"}}</answer>')["hard"], 1)

    def test_draft_and_cross_split_scenario_rejected(self) -> None:
        rows = sample_rows()
        rows[0]["review_status"] = "draft"
        with self.assertRaisesRegex(ValueError, "approved"):
            _validate_rows(rows)
        rows = sample_rows()
        rows[2]["scenario_id"] = rows[0]["scenario_id"]
        with self.assertRaisesRegex(ValueError, "scenario_id"):
            _validate_rows(rows)
        rows = sample_rows()
        del rows[0]["origin_type"]
        with self.assertRaisesRegex(ValueError, "origin_type"):
            _validate_rows(rows)

    def test_freeze_real_mcp_and_mock_cannot_publish(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wireless-reviewed-test-") as temp:
            root = Path(temp).resolve()
            self.assertTrue(root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
            source = root / "input.jsonl"
            source.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in sample_rows()), encoding="utf-8")
            frozen = root / "frozen"
            manifest = freeze(source, frozen)
            self.assertEqual(manifest["cases_by_split"], {"train": 1, "selection": 1, "holdout": 1})
            self.assertEqual(manifest["coverage"]["holdout"]["by_kind"], {"ask_clarification": 1})
            self.assertEqual(manifest["coverage"]["holdout"]["by_origin"], {"expert_authored": 1})
            loader = WirelessMCPDataLoader(split_dir=str(frozen), split_mode="split_dir", seed=42)
            loader.setup({"train_size": 1})
            self.assertEqual(len(loader.train_items), 1)
            tool_result = run_batch(loader.train_items, SEED_SKILL.read_text(encoding="utf-8"), root / "mock-tool", mock=True)
            self.assertEqual(tool_result[0]["hard"], 1)
            run = root / "training"
            run.mkdir()
            (run / "config.json").write_text(json.dumps({"split_dir": str(frozen), "eval_test": False}), encoding="utf-8")
            (run / "summary.json").write_text(json.dumps({"best_step": 1}), encoding="utf-8")
            selected = run / "best_skill.md"
            selected.write_bytes(SEED_SKILL.read_bytes())
            seal_selection(run, frozen)
            self.assertTrue(_selection_provenance(selected, frozen)["verified"])
            selected.write_bytes(selected.read_bytes() + b" ")
            self.assertFalse(_selection_provenance(selected, frozen)["verified"])
            evaluate(SEED_SKILL, root / "mock-eval", frozen, mock=True, repeats=2)
            report = json.loads((root / "mock-eval" / "comparison.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evaluation_kind"], "frozen_holdout")
            self.assertEqual(report["candidate"]["overall"]["hard"], 1.0)
            self.assertFalse(report["publishable"])
            self.assertFalse(report["coverage_ok"])
            self.assertEqual(report["repeats"], 2)
            self.assertEqual(report["unstable_direction_ids"], [])
            with self.assertRaises(SystemExit):
                package(SEED_SKILL, root / "mock-eval" / "comparison.json", root / "release")
            holdout_file = frozen / "test" / "items.json"
            holdout_file.write_bytes(holdout_file.read_bytes() + b" ")
            with self.assertRaisesRegex(SystemExit, "content changed"):
                evaluate(SEED_SKILL, root / "tampered", frozen, mock=True)
            rows = sample_rows()
            rows[0]["expected"] = {"output": [9]}
            source.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expected result differs"):
                freeze(source, root / "invalid")


if __name__ == "__main__":
    unittest.main()
