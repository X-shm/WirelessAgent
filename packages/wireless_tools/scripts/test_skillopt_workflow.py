"""Offline checks for multi-tool bindings, complete traces and frozen MCP references."""

from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from skillopt_wireless.__main__ import SEED_SKILL, evaluate
from skillopt_wireless.reviewed_cases import _validate_rows, freeze
from skillopt_wireless.rollout import run_batch
from skillopt_wireless.scoring import grade_case, json_pointer, workflow_arguments


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs" / "skillopt_review" / "SkillOpt_多工具候选题.jsonl.example"


def approved_fixture() -> list[dict]:
    rows = [json.loads(line) for line in DRAFT.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [{**row, "review_status": "approved", "reviewer": "TECHNICAL_TEST_ONLY"} for row in rows]


class WorkflowCasesTest(unittest.TestCase):
    def test_structured_binding_formats(self) -> None:
        prior = [{"seq": [0, 1, 1], "policy": [{"service_id": "voice", "gfbr_kbps": 120}]}]
        self.assertEqual(workflow_arguments({
            "arguments": {"bits": None, "qos_data": None},
            "bindings": [
                {"argument": "bits", "from_step": 0, "path": "/seq", "format": "csv"},
                {"argument": "qos_data", "from_step": 0, "path": "/policy", "format": "json"},
            ],
        }, prior), {"bits": "0,1,1", "qos_data": '[{"service_id":"voice","gfbr_kbps":120}]'})
        with self.assertRaisesRegex(ValueError, "scalar list"):
            workflow_arguments({"arguments": {"bits": None}, "bindings": [
                {"argument": "bits", "from_step": 0, "path": "/policy", "format": "csv"},
            ]}, prior)

    def test_full_trace_bindings_and_answer(self) -> None:
        item = _validate_rows(approved_fixture())[0]
        calls = [{"name": step["tool"], "arguments": step["arguments"],
                  "result": step["expected"], "is_error": False, "turn": index}
                 for index, step in enumerate(item["steps"])]
        answer = {field: json_pointer(item["steps"][spec["step"]]["expected"], spec["path"])
                  for field, spec in item["answer_fields"].items()}
        wrapped = "<answer>" + json.dumps(answer) + "</answer>"
        self.assertEqual(grade_case(item, calls, wrapped)["hard"], 1)

        bad = deepcopy(calls)
        bad[0], bad[1] = bad[1], bad[0]
        self.assertFalse(grade_case(item, bad, wrapped)["route_ok"])
        bad = deepcopy(calls)
        bad.append(deepcopy(calls[0]))
        self.assertFalse(grade_case(item, bad, wrapped)["route_ok"])
        bad = deepcopy(calls)
        bad[1]["arguments"]["itbs"] = "99"
        self.assertFalse(grade_case(item, bad, wrapped)["arguments_ok"])
        bad = deepcopy(calls)
        bad[1]["turn"] = 0
        self.assertFalse(grade_case(item, bad, wrapped)["arguments_ok"])
        bad = deepcopy(calls)
        bad[1]["result"]["tbs"] = -1
        self.assertFalse(grade_case(item, bad, wrapped)["result_ok"])
        self.assertFalse(grade_case(item, calls, '<answer>{"mod":"16QAM"}</answer>')["answer_ok"])
        embellished = {**answer, "invented_decision": "ready to deploy"}
        self.assertFalse(grade_case(item, calls, '<answer>' + json.dumps(embellished) + '</answer>')["answer_ok"])

    def test_validation_rejects_broken_binding_and_answer_field(self) -> None:
        rows = approved_fixture()
        rows[0]["steps"][1]["arguments"]["itbs"] = "99"
        with self.assertRaisesRegex(ValueError, "disagree"):
            _validate_rows(rows)
        rows = approved_fixture()
        rows[0]["steps"][1]["bindings"][0]["from_step"] = 1
        with self.assertRaisesRegex(ValueError, "invalid binding"):
            _validate_rows(rows)
        rows = approved_fixture()
        rows[0]["answer_fields"]["tbs"]["path"] = "/no_such_field"
        with self.assertRaisesRegex(ValueError, "answer field"):
            _validate_rows(rows)

    def test_freeze_and_mock_rollout_without_approving_draft(self) -> None:
        original = [json.loads(line) for line in DRAFT.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(original), 4)
        self.assertTrue(all(row["review_status"] == "draft" for row in original))
        with tempfile.TemporaryDirectory(prefix="wireless-workflow-test-") as temp:
            root = Path(temp).resolve()
            source = root / "technical-only.jsonl"
            source.write_text("\n".join(json.dumps(row, ensure_ascii=False)
                                         for row in approved_fixture()), encoding="utf-8")
            frozen = root / "frozen"
            manifest = freeze(source, frozen)
            self.assertEqual(manifest["max_workflow_steps"], 3)
            self.assertEqual(manifest["cases_by_split"], {"train": 2, "selection": 1, "holdout": 1})
            for split in ("train", "val", "test"):
                items = json.loads((frozen / split / "items.json").read_text(encoding="utf-8"))
                result = run_batch(items, SEED_SKILL.read_text(encoding="utf-8"),
                                   root / f"mock-{split}", mock=True,
                                   max_turns=manifest["max_workflow_steps"] + 1)
                self.assertTrue(all(row["hard"] == 1 for row in result))
                for item, row in zip(items, result):
                    self.assertEqual([call["turn"] for call in row["tool_calls"]],
                                     list(range(len(item["steps"]))))
            evaluate(SEED_SKILL, root / "mock-eval", frozen, mock=True, repeats=1)
            report = json.loads((root / "mock-eval" / "comparison.json").read_text(encoding="utf-8"))
            self.assertFalse(report["publishable"])
            self.assertEqual(report["baseline"]["by_kind"]["tool_workflow"]["hard"], 1)
            self.assertIn("tool_call", report["coverage_missing"]["kinds"])


if __name__ == "__main__":
    unittest.main()
