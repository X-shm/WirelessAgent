"""Static checks for the wireless tool interface contract."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
FLAG_RE = re.compile(r"['\"](--[A-Za-z0-9_-]+)['\"]")
SUBCOMMAND_RE = re.compile(r"\.add_parser\(\s*['\"]([A-Za-z0-9_-]+)['\"]")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)
    print(f"FAIL {message}")


def check_inputs(
    errors: list[str],
    tool_name: str,
    scope: str,
    inputs: object,
    flags: set[str],
) -> None:
    """Validate flag-backed schema inputs for a tool or positional subcommand."""
    if not isinstance(inputs, dict):
        fail(errors, f"{tool_name}: {scope} inputs must be an object")
        return

    for key, spec in inputs.items():
        if key not in flags:
            fail(errors, f"{tool_name}: {scope} input {key!r} has no exact --{key} CLI flag")
        if not isinstance(spec, dict) or "required" not in spec:
            fail(errors, f"{tool_name}: {scope} input {key!r} has no required field")


def main() -> int:
    errors: list[str] = []
    schemas = sorted(TOOLS.glob("*.schema.json"))
    registry = json.loads((ROOT / "tool_registry.json").read_text(encoding="utf-8"))
    registered = {item["name"] for item in registry["tools"]}
    schema_names: set[str] = set()
    bluetooth_tools = [item for item in registry["tools"] if item["product"] == "Bluetooth Toolbox"]
    bluetooth_sources = [source for item in bluetooth_tools for source in item["source_functions"]]
    if len(bluetooth_sources) != 52 or len(set(bluetooth_sources)) != 52:
        fail(errors, "Bluetooth Toolbox must map 52 distinct top-level source functions exactly once")
    else:
        print(f"PASS Bluetooth Toolbox: {len(bluetooth_tools)} tools map 52 distinct source functions")
    for item in bluetooth_tools:
        if not item.get("coverage"):
            fail(errors, f"{item['name']}: Bluetooth coverage boundary must be explicit")
    matrix_path = ROOT / "bluetooth_capabilities.json"
    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        groups = matrix.get("groups")
        if not isinstance(groups, list):
            raise ValueError("groups must be a list")
        matrix_sources = [source for group in groups if isinstance(group, dict)
                          for source in group.get("source_functions", [])]
        allowed_states = {"verified_slice", "partial", "complete"}
        invalid_groups = [group.get("cli", "<unknown>") for group in groups if not isinstance(group, dict)
                          or group.get("state") not in allowed_states or not isinstance(group.get("remaining"), list)]
        if set(matrix_sources) != set(bluetooth_sources) or len(matrix_sources) != len(set(matrix_sources)):
            fail(errors, "Bluetooth capability matrix must enumerate the 52 registered source functions exactly once")
        elif invalid_groups:
            fail(errors, f"Bluetooth capability matrix has invalid groups: {invalid_groups}")
        else:
            print("PASS Bluetooth capability matrix: 52 source functions with explicit completion state")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        fail(errors, f"Bluetooth capability matrix is invalid: {exc}")

    for schema_path in schemas:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        expected_name = schema_path.name.removesuffix(".schema.json")
        name = schema.get("name")
        schema_names.add(name)
        script_name = schema.get("script")
        script_path = TOOLS / str(script_name)

        if name != expected_name:
            fail(errors, f"{schema_path.name}: name={name!r}, expected {expected_name!r}")
        if script_name != f"{expected_name}.py":
            fail(errors, f"{schema_path.name}: script must be {expected_name}.py")
        if not script_path.is_file():
            fail(errors, f"{schema_path.name}: missing {script_name}")
            continue

        source = script_path.read_text(encoding="utf-8")
        flags = {match[2:] for match in FLAG_RE.findall(source)}
        # Bluetooth tools share a deliberately uniform CLI adapter.  Its
        # common flags are real public flags even though argparse declares
        # them in the shared module rather than in every thin entrypoint.
        if "_bluetooth_common" in source:
            common_source = (TOOLS / "_bluetooth_common.py").read_text(encoding="utf-8")
            flags.update(match[2:] for match in FLAG_RE.findall(common_source))
        if "from _nr_remaining_common import" in source and "run_cli(" in source:
            common_source = (TOOLS / "_nr_remaining_common.py").read_text(encoding="utf-8")
            flags.update(match[2:] for match in FLAG_RE.findall(common_source))
        check_inputs(errors, name, "schema", schema.get("inputs", {}), flags)

        subcommands = schema.get("subcommands", {})
        if not isinstance(subcommands, dict):
            fail(errors, f"{name}: subcommands must be an object")
        else:
            cli_subcommands = set(SUBCOMMAND_RE.findall(source))
            for subcommand, subcommand_schema in subcommands.items():
                if subcommand not in cli_subcommands:
                    fail(errors, f"{name}: schema subcommand {subcommand!r} is not a CLI subcommand")
                    continue
                if not isinstance(subcommand_schema, dict):
                    fail(errors, f"{name}: subcommand {subcommand!r} must be an object")
                    continue
                check_inputs(
                    errors,
                    name,
                    f"subcommand {subcommand!r}",
                    subcommand_schema.get("inputs", {}),
                    flags,
                )

        help_run = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if help_run.returncode != 0:
            fail(errors, f"{name}: --help exited {help_run.returncode}")
        else:
            print(f"PASS {name}: names, flags, JSON schema, --help")

    if schema_names != registered:
        fail(errors, f"registry mismatch: schemas={sorted(schema_names)}, registry={sorted(registered)}")

    docs_run = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_registry_docs.py"), "--check"],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if docs_run.returncode != 0:
        fail(errors, "registry-derived documentation is stale")
    else:
        print("PASS registry-derived documentation")

    required_skill_fields = ("name:", "description:")
    skill_text = (TOOLS / "SKILL.md").read_text(encoding="utf-8")
    if not skill_text.startswith("---\n") or not all(field in skill_text for field in required_skill_fields):
        fail(errors, "tools/SKILL.md frontmatter is incomplete")
    else:
        print("PASS tools/SKILL.md frontmatter")

    print(f"\n{len(schemas)} schemas checked; {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
