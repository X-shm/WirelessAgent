"""Extract published LTE NSSS binary masks from the installed MATLAB M-file."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matlab-root", type=Path, required=True)
    args = parser.parse_args()
    source = args.matlab_root / "toolbox" / "lte" / "lte" / "lteNSSS.m"
    body = source.read_text(encoding="utf-8").split("bseq = [", 1)[1].split("];", 1)[0]
    rows = [[int(x) for x in re.findall(r"-?\d+", row)]
            for row in re.findall(r"\[([^\[\]]+)\]", body)]
    if len(rows) != 4 or any(len(row) != 128 for row in rows):
        raise ValueError(f"unexpected NSSS binary matrix shape: {[len(row) for row in rows]}")
    root = Path(__file__).resolve().parents[1]
    output = root / "tools" / "_lte_nsss_binary.json"
    output.write_text(json.dumps(rows) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
