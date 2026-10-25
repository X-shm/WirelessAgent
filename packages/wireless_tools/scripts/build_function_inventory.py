"""Build a conversion-tracking inventory from an installed MATLAB tree."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


PRODUCTS = {
    "5G Toolbox": ("5g/5g",),
    # Bluetooth exposes public names from separate Classic and BLE folders.
    "Bluetooth Toolbox": ("bluetooth/bluetooth", "bluetooth/ble"),
    "Communications Toolbox": ("comm/comm",),
    "LTE Toolbox": ("lte/lte",),
    "WLAN Toolbox": ("wlan/wlan", "wlan/wlan/+wlan/+type"),
    "Wireless Network Toolbox": ("wnet/wnet", "wnet/wnet/traffic", "wnet/wnet/+wnet"),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--matlab_root",
        required=True,
        help="Installed MATLAB root directory (the directory containing toolbox/)",
    )
    parser.add_argument("--matlab-release", help="MATLAB release/version recorded in the inventory")
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    registry = json.loads((root / "tool_registry.json").read_text(encoding="utf-8"))
    converted = {}
    for tool in registry["tools"]:
        for function in tool["source_functions"]:
            converted[function.lower()] = {
                "tool": tool["name"],
                "status": tool.get("source_status", {}).get(function, tool["status"]),
            }

    matlab_root = Path(args.matlab_root).resolve()
    toolbox_root = matlab_root / "toolbox"
    result = {
        "matlab_root": str(matlab_root),
        "matlab_release": args.matlab_release,
        "products": {},
    }
    for product, relative_paths in PRODUCTS.items():
        folders = [toolbox_root.joinpath(*relative_path.split("/")) for relative_path in relative_paths]
        available = all(folder.is_dir() for folder in folders)
        names = (
            sorted(
                {
                    (f"wnet.{path.stem}" if product == "Wireless Network Toolbox"
                     and folder.name == "+wnet" else
                     f"wlan.type.{path.stem}" if product == "WLAN Toolbox"
                     and folder.name == "+type" else path.stem)
                    for folder in folders
                    for path in folder.iterdir()
                    if path.is_file() and path.suffix.lower() in (".m", ".p", ".mlx") and path.stem != "Contents"
                },
                key=str.lower,
            )
            if available
            else []
        )
        functions = []
        for name in names:
            state = converted.get(name.lower(), {"tool": None, "status": "pending"})
            functions.append({"matlab_name": name, **state})
        product_inventory = {
            "available": available,
            "toolbox_path": str(folders[0]),
            "total_top_level_entries": len(functions),
            "converted_entries": sum(item["status"] != "pending" for item in functions),
            "functions": functions,
        }
        if len(folders) > 1:
            product_inventory["additional_toolbox_paths"] = [str(folder) for folder in folders[1:]]
        if product == "Wireless Network Toolbox":
            product_inventory["entry_scope"] = (
                "public root, traffic, and +wnet namespace files; excludes +internal implementation files"
            )
            product_inventory["total_public_entries"] = len(functions)
        if product == "WLAN Toolbox":
            product_inventory["entry_scope"] = (
                "public root and +wlan/+type enum classes; excludes +wlan/+internal implementation files"
            )
            product_inventory["total_public_entries"] = len(functions)
        result["products"][product] = product_inventory

    output = Path(args.output) if args.output else root / "references" / "function_inventory.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
