"""SkillOpt EnvAdapter around the Wireless Toolbox MCP server."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

from skillopt.datasets.base import BatchSpec, SplitDataLoader
from skillopt.envs.base import EnvAdapter

from . import ROOT
from .cases import SPLITS, registry_names
from .rollout import run_batch, prompt_for_case
from .scoring import grade_case


def _cached_rollout(
    items: list[dict[str, Any]], skill_content: str, out_dir: str,
    max_turns: int,
) -> list[dict[str, Any]] | None:
    """Reuse a complete live batch after a crash, only when inputs still match."""
    root = Path(out_dir)
    try:
        rows = json.loads((root / "rollouts.json").read_text(encoding="utf-8"))
        if not isinstance(rows, list) or len(rows) != len(items):
            return None
        model = os.environ.get("DEEPSEEK_TARGET_MODEL", "deepseek-flash")
        for item, row in zip(items, rows):
            prompt = prompt_for_case(skill_content, item)
            if not isinstance(row, dict):
                return None
            if (
                row.get("id") != str(item["id"])
                or row.get("question") != item["question"]
                or row.get("task_type") != item["task_type"]
                or row.get("target_system_prompt") != prompt
                or row.get("target_user_prompt") != item["question"]
                or row.get("target_model", "deepseek-flash") != model
                or row.get("n_turns", max_turns + 1) > max_turns
            ):
                return None
            if row.get("fail_reason", "").startswith("model_error:"):
                return None
            if row.get("fail_reason") == "exceeded tool-turn budget" and row["n_turns"] != max_turns:
                return None
            usage = row.get("token_usage")
            if not isinstance(usage, list) or not any(
                isinstance(entry, dict) and entry.get("total_tokens", 0) > 0
                for entry in usage
            ):
                return None
            conversation_path = root / "predictions" / str(item["id"]) / "conversation.json"
            conversation = json.loads(conversation_path.read_text(encoding="utf-8"))
            if (
                not isinstance(conversation, list)
                or len(conversation) < 2
                or conversation[0] != {"role": "system", "content": prompt}
                or conversation[1] != {"role": "user", "content": item["question"]}
            ):
                return None
            scores = grade_case(item, row["tool_calls"], row["predicted_answer"])
            if any(row.get(key) != value for key, value in scores.items()):
                return None
        return rows
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError):
        return None


class WirelessMCPDataLoader(SplitDataLoader):
    def load_split_items(self, split_path: str) -> list[dict[str, Any]]:
        return json.loads((Path(split_path) / "items.json").read_text(encoding="utf-8"))

    def setup(self, cfg: dict) -> None:
        manifest = json.loads((Path(self.split_dir) / "manifest.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256((ROOT / "tool_registry.json").read_bytes()).hexdigest()
        if manifest["registry_sha256"] != digest:
            raise ValueError("tool_registry.json changed; rebuild SkillOpt fixtures")
        if not manifest["complete"]:
            raise ValueError("SkillOpt fixtures have gaps; inspect manifest.json")
        super().setup(cfg)
        if manifest.get("kind") in {"reviewed_business", "draft_experiment"}:
            for split in SPLITS:
                items = self._splits[split]
                if not items or len({row["id"] for row in items}) != len(items):
                    raise ValueError(f"{split} is empty or has duplicate task IDs")
            return
        names = registry_names()
        for split in SPLITS:
            items = self._splits[split]
            if {row["tool"] for row in items} != names:
                raise ValueError(f"{split} does not cover all registered tools")
            if len({row["id"] for row in items}) != len(items):
                raise ValueError(f"{split} has duplicate task IDs")
        by_name = {
            split: {row["tool"]: row for row in self._splits[split]}
            for split in SPLITS
        }
        for name in names:
            inputs = {
                json.dumps(by_name[split][name]["arguments"], sort_keys=True, ensure_ascii=False)
                for split in SPLITS
            }
            if len(inputs) != len(SPLITS):
                raise ValueError(f"{name} reuses input arguments across splits")


class WirelessMCPAdapter(EnvAdapter):
    def __init__(
        self, split_dir: str, *, max_turns: int = 3, mock_target: bool = False,
        output_root: str | None = None, reuse_root: str | None = None,
    ) -> None:
        self.dataloader = WirelessMCPDataLoader(
            split_dir=split_dir, split_mode="split_dir", seed=42,
        )
        self.max_turns = max_turns
        self.mock_target = mock_target
        self.output_root = Path(output_root).resolve() if output_root else None
        self.reuse_root = Path(reuse_root).resolve() if reuse_root else None
        # EnvAdapter.reflect() reads these attributes directly. Keep defaults
        # for standalone use, then bind the resolved training config in setup.
        self.analyst_workers = 2
        self.failure_only = False
        self.minibatch_size = 4
        self.edit_budget = 2

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.analyst_workers = int(cfg.get("analyst_workers", self.analyst_workers))
        self.failure_only = bool(cfg.get("failure_only", self.failure_only))
        self.minibatch_size = int(cfg.get("minibatch_size", self.minibatch_size))
        self.edit_budget = int(cfg.get("edit_budget", self.edit_budget))
        self.max_turns = int(cfg.get("max_turns", self.max_turns))
        self.dataloader.setup(cfg)

    def get_dataloader(self) -> WirelessMCPDataLoader:
        return self.dataloader

    def build_env_from_batch(self, batch: BatchSpec, **kwargs) -> list[dict[str, Any]]:
        del kwargs
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs) -> list[dict[str, Any]]:
        return self.build_env_from_batch(self.dataloader.build_train_batch(batch_size, seed, **kwargs))

    def build_eval_env(
        self, env_num: int, split: str, seed: int, **kwargs
    ) -> list[dict[str, Any]]:
        return self.build_env_from_batch(
            self.dataloader.build_eval_batch(env_num, split, seed, **kwargs)
        )

    def rollout(
        self, env_manager: list[dict[str, Any]], skill_content: str,
        out_dir: str, **kwargs,
    ) -> list[dict[str, Any]]:
        del kwargs
        if not self.mock_target:
            cached = _cached_rollout(env_manager, skill_content, out_dir, self.max_turns)
            if cached is not None:
                print(f"  [WirelessMCPAdapter] reused {len(cached)} verified rollouts from {out_dir}")
                return cached
            if self.output_root is not None and self.reuse_root is not None:
                try:
                    relative = Path(out_dir).resolve().relative_to(self.output_root)
                except ValueError:
                    relative = None
                if relative is not None:
                    source = self.reuse_root / relative
                    cached = _cached_rollout(
                        env_manager, skill_content, str(source), self.max_turns,
                    )
                    if cached is not None:
                        destination = Path(out_dir)
                        destination.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source / "rollouts.json", destination / "rollouts.json")
                        for item in env_manager:
                            task_id = str(item["id"])
                            target_dir = destination / "predictions" / task_id
                            target_dir.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(
                                source / "predictions" / task_id / "conversation.json",
                                target_dir / "conversation.json",
                            )
                        print(f"  [WirelessMCPAdapter] reused {len(cached)} verified rollouts from {source}")
                        return cached
        return run_batch(
            env_manager, skill_content, out_dir,
            mock=self.mock_target, max_turns=self.max_turns,
        )

    def get_task_types(self) -> list[str]:
        return sorted({
            row["task_type"]
            for split in (self.dataloader.train_items, self.dataloader.val_items, self.dataloader.test_items)
            for row in split
        })
