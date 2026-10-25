"""Standalone LTE coding, configuration and headless GUI-helper operations."""
from __future__ import annotations
from functools import partial
from _nr_remaining_common import run_cli
from _lte_expansion_core import GROUPS, execute

DISPATCH = {name: partial(execute, name) for name in GROUPS["misc"]}

if __name__ == "__main__":
    run_cli("LTE coding, configuration and headless GUI-helper operations", DISPATCH)
