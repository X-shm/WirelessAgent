"""Technically verify draft cases without approving them for business use."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skillopt_wireless.reviewed_cases import freeze


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs" / "skillopt_review" / "SkillOpt_候选业务题标注.jsonl.example"


class BusinessDraftTest(unittest.TestCase):
    def test_all_product_splits_and_mcp_references(self) -> None:
        rows = [json.loads(line) for line in DRAFT.read_text(encoding="utf-8").splitlines()]
        products = {entry["product"] for entry in json.loads(
            (ROOT / "tool_registry.json").read_text(encoding="utf-8")
        )["tools"]}
        names_to_product = {entry["name"]: entry["product"] for entry in json.loads(
            (ROOT / "tool_registry.json").read_text(encoding="utf-8")
        )["tools"]}
        self.assertEqual(len(rows), 26)
        self.assertTrue(all(row["review_status"] == "draft" for row in rows))
        self.assertTrue(all(row["origin_type"] == "expert_authored" for row in rows))
        for split in ("train", "selection", "holdout"):
            self.assertEqual({names_to_product[row["tool"]] for row in rows if row["split"] == split}, products)
        self.assertEqual({row["kind"] for row in rows if row["split"] == "holdout"},
                         {"tool_call", "ask_clarification"})

        # Change status only inside the temporary technical fixture. The draft
        # on disk remains unapproved and cannot be used for production training.
        with tempfile.TemporaryDirectory(prefix="wireless-business-draft-test-") as temp:
            root = Path(temp).resolve()
            self.assertTrue(root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
            source = root / "technical-only.jsonl"
            source.write_text("\n".join(json.dumps({**row, "review_status": "approved",
                                                      "reviewer": "TECHNICAL_TEST_ONLY"}, ensure_ascii=False)
                                         for row in rows), encoding="utf-8")
            manifest = freeze(source, root / "frozen")
            self.assertEqual(sum(manifest["cases_by_split"].values()), 26)
            self.assertEqual(manifest["coverage"]["holdout"]["by_kind"]["ask_clarification"], 1)


if __name__ == "__main__":
    unittest.main()
