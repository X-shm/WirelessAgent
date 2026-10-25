"""Check optimizer schemas against their filenames and CLI input contract."""
from __future__ import annotations
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def main():
    paths = sorted((BASE / "tools").glob("*.schema.json"))
    failures = []
    for path in paths:
        schema = json.loads(path.read_text(encoding="utf-8"))
        name = path.name.removesuffix(".schema.json")
        if schema.get("name") != name or schema.get("script") != f"{name}.py":
            failures.append(f"{path.name}: name/script mismatch")
        if not {"name", "script", "description", "inputs", "outputs", "example"}.issubset(schema):
            failures.append(f"{path.name}: missing contract field")
        for key, value in schema.get("inputs", {}).items():
            if value.get("required") not in (True, False):
                failures.append(f"{path.name}: {key} lacks required boolean")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"{len(paths)}/{len(paths)} schemas passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
