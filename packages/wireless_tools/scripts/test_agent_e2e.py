"""End-to-end agent call test for wireless-toolbox tools."""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
SCHEMA_PATTERN = "*.schema.json"
TIMEOUT = 30


def load_schema(schema_path: Path) -> dict:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def extract_example_cmd(schema: dict) -> list[str] | None:
    example = schema.get("example")
    if not example:
        return None
    cmd_str = example.get("cmd")
    if not cmd_str:
        return None
    # shlex keeps quoted JSON payloads as a single argv token
    parts = shlex.split(cmd_str, posix=True)
    if parts and parts[0] == "python":
        parts = parts[1:]
    return parts


def run_tool(cmd_args: list[str], timeout: int = None):
    if timeout is None:
        timeout = TIMEOUT
    # Fix relative paths: if the script doesn't exist at given path,
    # try prepending tools/ directory
    if cmd_args and not cmd_args[0].endswith(".py"):
        pass
    else:
        script_path = Path(cmd_args[0])
        if not script_path.is_file():
            alt_path = TOOLS_DIR / cmd_args[0]
            if alt_path.is_file():
                cmd_args[0] = str(alt_path)
    full_cmd = [sys.executable] + cmd_args
    try:
        result = subprocess.run(
            full_cmd, capture_output=True, text=True,
            timeout=timeout, cwd=str(ROOT),
            encoding="utf-8", errors="replace",
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", f"TIMEOUT after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def validate_json_output(stdout: str):
    stdout = (stdout or "").strip()
    if not stdout:
        return False, None, "Empty output"
    try:
        parsed = json.loads(stdout)
        if not isinstance(parsed, dict):
            return False, None, f"Output is {type(parsed).__name__}"
        return True, parsed, ""
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {e}"


def check_output_fields(schema: dict, output: dict):
    declared = schema.get("outputs", {})
    if not declared:
        return [], []

    # Bluetooth/adapter tools wrap payload as {"ok":..., "result": {...}}
    if isinstance(output.get("result"), dict):
        nested = output["result"]
        merged = dict(nested)
        merged.update({k: v for k, v in output.items() if k != "result"})
        output = merged

    def _is_optional(field_def):
        if isinstance(field_def, dict):
            return field_def.get("optional", False)
        return False

    required = [k for k, v in declared.items() if not _is_optional(v)]
    present = [k for k in required if k in output]
    missing = [k for k in required if k not in output]
    return present, missing


def test_tool(schema_path: Path, verbose: bool = False) -> dict:
    schema = load_schema(schema_path)
    tool_name = schema.get("name", schema_path.stem.replace(".schema", ""))
    result = {
        "name": tool_name, "status": "UNKNOWN", "cmd": None,
        "returncode": None, "output_valid": False,
        "output_fields_present": [], "output_fields_missing": [],
        "error": None, "duration_ms": 0,
    }
    cmd_args = extract_example_cmd(schema)
    if cmd_args is None:
        result["status"] = "NO_EXAMPLE"
        result["error"] = "No example command in schema"
        return result
    result["cmd"] = " ".join(cmd_args)
    start = time.time()
    returncode, stdout, stderr = run_tool(cmd_args)
    duration = round((time.time() - start) * 1000, 1)
    result["duration_ms"] = duration
    result["returncode"] = returncode
    if returncode != 0:
        result["status"] = "EXEC_FAILED"
        result["error"] = (stderr or "").strip() or f"Exit code {returncode}"
        return result
    is_valid, parsed, json_error = validate_json_output(stdout)
    result["output_valid"] = is_valid
    if not is_valid:
        result["status"] = "INVALID_OUTPUT"
        result["error"] = json_error
        return result
    present, missing = check_output_fields(schema, parsed)
    result["output_fields_present"] = present
    result["output_fields_missing"] = missing
    if missing:
        result["status"] = "MISSING_FIELDS"
        result["error"] = f"Missing output fields: {missing}"
    else:
        result["status"] = "PASS"
    return result


def print_result(result: dict, verbose: bool = False) -> None:
    status = result["status"]
    name = result["name"]
    icons = {
        "PASS": "PASS", "NO_EXAMPLE": "SKIP",
        "EXEC_FAILED": "FAIL", "INVALID_OUTPUT": "FAIL",
        "MISSING_FIELDS": "WARN",
    }
    icon = icons.get(status, "????")
    line = f"  [{icon}] {name}: {status}"
    dur = result["duration_ms"]
    if dur:
        line += f" ({dur}ms)"
    print(line)
    if result["cmd"] and (status != "PASS" or verbose):
        cmd = result["cmd"]
        print(f"     cmd: {cmd}")
    if result["error"]:
        err = result["error"]
        print(f"     err: {err}")
    if result["output_fields_missing"]:
        missing = result["output_fields_missing"]
        print(f"     missing: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent e2e test")
    parser.add_argument("--tool", type=str, default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--timeout", type=int, default=None)
    args = parser.parse_args()
    global TIMEOUT
    if args.timeout is not None:
        TIMEOUT = args.timeout
    if args.tool:
        schema_path = TOOLS_DIR / f"{args.tool}.schema.json"
        if not schema_path.is_file():
            print(f"Schema not found: {schema_path}")
            return 1
        schemas = [schema_path]
    else:
        schemas = sorted(TOOLS_DIR.glob(SCHEMA_PATTERN))
    print(f"Testing {len(schemas)} tools...")
    print()
    results = []
    for sp in schemas:
        r = test_tool(sp, verbose=args.verbose)
        results.append(r)
        print_result(r, verbose=args.verbose)
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    no_ex = sum(1 for r in results if r["status"] == "NO_EXAMPLE")
    exec_f = sum(1 for r in results if r["status"] == "EXEC_FAILED")
    inv_out = sum(1 for r in results if r["status"] == "INVALID_OUTPUT")
    miss_f = sum(1 for r in results if r["status"] == "MISSING_FIELDS")
    print()
    print("=" * 50)
    print(f"SUMMARY: {passed}/{total} tools ready")
    print(f"  PASS: {passed}  SKIP: {no_ex}  FAIL(exec): {exec_f}")
    print(f"  FAIL(output): {inv_out}  WARN(fields): {miss_f}")
    if exec_f or inv_out:
        failed = [r["name"] for r in results if r["status"] in ("EXEC_FAILED", "INVALID_OUTPUT")]
        ftools = ", ".join(failed)
        print(f"\nFailed: {ftools}")
    return 0 if (exec_f + inv_out) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
