"""Python runtime capability check corresponding to the MATLAB support hook."""
from __future__ import annotations

import importlib.util
import sys

from _nr_remaining_common import run_cli


def wirelessnetwork_support_package_check():
    modules = {name: importlib.util.find_spec(name) is not None
               for name in ("numpy", "scipy", "mcp")}
    return {"runtime": "Python", "python_version": sys.version.split()[0],
            "matlab_required": False, "dependencies": modules,
            "core_ready": modules["numpy"] and modules["scipy"],
            "mcp_ready": modules["numpy"] and modules["scipy"] and modules["mcp"]}


if __name__ == "__main__":
    run_cli("Wireless Network Toolbox Python runtime support check", {
        "wirelessnetworkSupportPackageCheck": wirelessnetwork_support_package_check,
    })
