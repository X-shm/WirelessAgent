"""Data-only NR configuration constructors with MATLAB-free runtime."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path


DEFAULTS_PATH = Path(__file__).resolve().parents[1] / "references" / "5g_config_defaults.json"


def available_configs() -> dict[str, dict]:
    payload = json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))
    return payload["defaults"]


def _merge(base: dict, overrides: dict, path: str = "") -> None:
    for key, value in overrides.items():
        if key not in base:
            raise ValueError(f"unknown configuration property: {path}{key}")
        original = base[key]
        if isinstance(original, dict):
            if not isinstance(value, dict):
                raise ValueError(f"{path}{key} must be an object")
            _merge(original, value, path + key + ".")
        else:
            base[key] = value


def make_config(class_name: str, properties: dict | None = None) -> dict:
    defaults = available_configs()
    if class_name not in defaults:
        raise ValueError(f"unknown 5G configuration class: {class_name}")
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise ValueError("properties must be a JSON object")
    result = copy.deepcopy(defaults[class_name])
    _merge(result, properties)
    if class_name == "nrCarrierConfig":
        scs = result["SubcarrierSpacing"]
        cp = result["CyclicPrefix"]
        if scs not in (15, 30, 60, 120, 240, 480, 960):
            raise ValueError("SubcarrierSpacing must be 15, 30, 60, 120, 240, 480 or 960")
        if cp not in ("normal", "extended") or (cp == "extended" and scs != 60):
            raise ValueError("extended CyclicPrefix is valid only at 60 kHz")
        if not isinstance(result["NSizeGrid"], int) or not 1 <= result["NSizeGrid"] <= 275:
            raise ValueError("NSizeGrid must be an integer from 1 to 275")
        if not isinstance(result["NStartGrid"], int) or result["NStartGrid"] < 0:
            raise ValueError("NStartGrid must be a nonnegative integer")
        result["SymbolsPerSlot"] = 12 if cp == "extended" else 14
        result["SlotsPerSubframe"] = scs // 15
        result["SlotsPerFrame"] = 10 * result["SlotsPerSubframe"]
    return {"class_name": class_name, "properties": result}


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone 5G NR configuration snapshots")
    parser.add_argument("--class_name", choices=sorted(available_configs()), required=True)
    parser.add_argument("--properties", default="{}", help="JSON object of property overrides")
    args = parser.parse_args()
    try:
        print(json.dumps(make_config(args.class_name, json.loads(args.properties)), ensure_ascii=False))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
