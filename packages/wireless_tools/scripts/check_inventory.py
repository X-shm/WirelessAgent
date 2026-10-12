"""Summarize the checked-in function inventory and optional local MATLAB tree."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matlab-root",
        type=Path,
        help="MATLAB installation directory containing toolbox/ (optional)",
    )
    args = parser.parse_args()

    inv = json.loads((ROOT / "references" / "function_inventory.json").read_text(encoding="utf-8"))
    for product, entry in inv["products"].items():
        total = entry.get("total_top_level_entries", "?")
        converted = entry.get("converted_entries", "?")
        print(f"{product}: {converted}/{total}")

    tools_dir = ROOT / "tools"
    nr = list(tools_dir.glob("nr_*.py"))
    lte = list(tools_dir.glob("lte_*.py"))
    wlan = list(tools_dir.glob("wlan_*.py"))
    print(f"\nLocal tools: NR={len(nr)}, LTE={len(lte)}, WLAN={len(wlan)}")

    if args.matlab_root is None:
        print("MATLAB function counts: unavailable (pass --matlab-root to inspect a local installation)")
        return

    toolbox_root = args.matlab_root.expanduser().resolve() / "toolbox"
    if not toolbox_root.is_dir():
        parser.error(f"MATLAB toolbox directory not found: {toolbox_root}")

    # Count MATLAB functions in local toolbox folders.
    counts = {}
    for sub in ("5g", "comm", "wlan", "signal", "lte"):
        folder = toolbox_root / sub / sub
        if folder.is_dir():
            counts[sub] = len(list(folder.glob("*.m")))
    print(f"MATLAB function counts: {counts}")


if __name__ == "__main__":
    main()
