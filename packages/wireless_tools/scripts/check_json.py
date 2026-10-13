"""Validate every repository JSON file and the local schema document shape."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"


def main() -> int:
    errors: list[str] = []
    json_paths = sorted(ROOT.rglob("*.json"))
    schema_paths = sorted(TOOLS_DIR.glob("*.schema.json"))

    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: {exc}")

    for path in schema_paths:
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        required = {"name": str, "script": str, "inputs": dict, "outputs": dict}
        for field, expected_type in required.items():
            if not isinstance(schema.get(field), expected_type):
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}: {field!r} must be "
                    f"{expected_type.__name__}"
                )

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print(f"\n{len(json_paths)} JSON files; {len(schema_paths)} schemas; {len(errors)} errors")
        return 1

    print(f"PASS {len(json_paths)} JSON files parsed; {len(schema_paths)} schemas have required fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
