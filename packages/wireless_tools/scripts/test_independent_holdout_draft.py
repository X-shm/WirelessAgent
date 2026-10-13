"""Offline review checks for isolated, expert-authored holdout candidates."""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from skillopt_wireless.reviewed_cases import freeze
from skillopt_wireless.rollout import run_batch


ROOT = Path(__file__).resolve().parents[1]
HOLDOUT = ROOT / "docs" / "skillopt_review" / "SkillOpt_独立验收候选题.jsonl.example"
WORKFLOWS = ROOT / "docs" / "skillopt_review" / "SkillOpt_多工具候选题.jsonl.example"
PREVIOUS = ROOT / "docs" / "skillopt_review" / "SkillOpt_候选业务题标注.jsonl.example"
SEED = ROOT / "skills" / "wireless_mcp" / "seed_skill.md"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class IndependentHoldoutDraftTest(unittest.TestCase):
    def test_holdout_is_draft_and_distinct_from_prior_questions(self) -> None:
        holdout = rows(HOLDOUT)
        self.assertEqual(len(holdout), 18)
        self.assertEqual(len({row["id"] for row in holdout}), 18)
        self.assertTrue(all(row["split"] == "holdout" and row["review_status"] == "draft"
                            and row["origin_type"] == "expert_authored" for row in holdout))
        self.assertEqual(sum(row["kind"] == "tool_workflow" for row in holdout), 3)
        self.assertEqual(sum(row["kind"] == "ask_clarification" for row in holdout), 2)
        old_questions = {" ".join(row["question"].split()).casefold()
                         for path in (WORKFLOWS, PREVIOUS) for row in rows(path)}
        self.assertFalse(old_questions & {" ".join(row["question"].split()).casefold()
                                          for row in holdout})

    def test_selected_reference_values_have_independent_sanity_checks(self) -> None:
        cases = {row["id"]: row for row in rows(HOLDOUT)}
        self.assertEqual(cases["H05"]["expected"]["result"],
                         {"duration_us": 176.0, "num_bits": 176})
        self.assertEqual(cases["H07"]["expected"]["output"][0], 0.5)
        self.assertTrue(math.isclose(cases["H16"]["expected"]["capacity_bps"],
                                     5_000_000 * math.log2(11), rel_tol=1e-10))
        self.assertEqual(cases["H12"]["expected"]["positions"],
                         [[0.0, 25.0, 1.5], [0.0, 15.0, 1.5],
                          [20.0, 25.0, 1.5], [20.0, 15.0, 1.5]])
        self.assertTrue(cases["H14"]["steps"][1]["expected"]["accepted"])

    def test_freeze_and_mock_all_holdout_without_changing_review_status(self) -> None:
        holdout = rows(HOLDOUT)
        development = [row for row in rows(WORKFLOWS) if row["split"] != "holdout"]
        with tempfile.TemporaryDirectory(prefix="wireless-holdout-check-") as temp:
            root = Path(temp).resolve()
            input_path = root / "technical-fixture.jsonl"
            fixture = [{**row, "review_status": "approved", "reviewer": "TECHNICAL_TEST_ONLY"}
                       for row in development + holdout]
            input_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in fixture) + "\n",
                                  encoding="utf-8")
            frozen = root / "frozen"
            manifest = freeze(input_path, frozen)
            self.assertEqual(manifest["cases_by_split"], {"train": 2, "selection": 1, "holdout": 18})
            self.assertEqual(manifest["coverage"]["holdout"]["workflow_count"], 3)
            self.assertEqual(len(manifest["coverage"]["holdout"]["by_product"]), 8)
            items = json.loads((frozen / "test" / "items.json").read_text(encoding="utf-8"))
            results = run_batch(items, SEED.read_text(encoding="utf-8"), root / "mock",
                                mock=True, max_turns=manifest["max_workflow_steps"] + 1)
            self.assertEqual(len(results), 18)
            self.assertTrue(all(row["hard"] == 1 for row in results))
        self.assertTrue(all(row["review_status"] == "draft" for row in rows(HOLDOUT)))


if __name__ == "__main__":
    unittest.main()
