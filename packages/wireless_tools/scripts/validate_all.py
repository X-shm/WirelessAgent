"""Run every MATLAB-golden validator and return one process status."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
VALIDATORS = sorted(
    path.name for path in BASE.glob("validate_*.py")
    if path.name != "validate_all.py"
)
MISSING_GOLD_SAMPLE_EXIT = 77


def main() -> int:
    passed = 0
    skipped = 0
    failed = 0
    for filename in VALIDATORS:
        print(f"\n=== {filename} ===", flush=True)
        result = subprocess.run([sys.executable, str(BASE / filename)], check=False)
        if result.returncode == 0:
            passed += 1
        elif result.returncode == MISSING_GOLD_SAMPLE_EXIT:
            skipped += 1
            print(f"SKIP {filename}: MATLAB golden sample is not checked in")
        else:
            failed += 1
    print(
        f"\n{passed} passed, {skipped} skipped, {failed} failed "
        f"out of {len(VALIDATORS)} validators"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
