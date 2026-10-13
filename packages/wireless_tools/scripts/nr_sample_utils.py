"""Shared helpers for deterministic NR MATLAB-golden validators."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SAMPLES = ROOT / "matlab_oracle" / "samples"
MISSING_GOLD_SAMPLE_EXIT = 77


def add_tools_to_path() -> None:
    """Make repository tool modules importable from a validator."""
    tools_path = str(TOOLS)
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)


def load_golden_samples(filename: str) -> list[dict[str, Any]] | dict[str, Any] | None:
    """Load a checked-in MATLAB sample file, or report a truthful pending state.

    A missing sample is not a Python implementation regression.  It means the
    MATLAB generator has not yet run in an environment with 5G Toolbox.
    Callers must return ``MISSING_GOLD_SAMPLE_EXIT`` in that case so that the
    aggregate runner reports it as skipped rather than passed.
    """
    path = SAMPLES / filename
    if not path.is_file():
        print(
            f"SKIP  missing MATLAB golden sample: {path.relative_to(ROOT)}\n"
            "      Run matlab_oracle/gen_samples_nr_pending.m with 5G Toolbox "
            "to create it."
        )
        return None
    return json.loads(path.read_text(encoding="utf-8"))


class Checks:
    """Small, dependency-free result accumulator shared by validators."""

    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        if ok:
            self.passed += 1
            print(f"PASS  {name}")
        else:
            self.failed += 1
            suffix = f"  {detail}" if detail else ""
            print(f"FAIL  {name}{suffix}")

    def finish(self, label: str = "checks") -> int:
        total = self.passed + self.failed
        print(f"\n{self.passed}/{total} {label} passed")
        return 0 if self.failed == 0 else 1
