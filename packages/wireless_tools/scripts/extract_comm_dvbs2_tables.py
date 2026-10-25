"""Development-only extraction of DVB-S2 check-node tables from installed MATLAB."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = Path(args.source).read_text(encoding="utf-8", errors="ignore")
    source = source[source.index("function [ct1, ct2] = getchecknodetable") :]
    cases = list(re.finditer(r"(?m)^\s*case\s+(\d+/\d+)\s*$", source))
    tables = {}
    for index, match in enumerate(cases):
        body = source[match.end():cases[index+1].start() if index+1 < len(cases) else len(source)]
        components = {}
        for name in ("ct1", "ct2"):
            matrix = re.search(rf"\b{name}\s*=\s*\[(.*?)\]\s*;", body, re.S)
            if not matrix:
                raise ValueError(f"missing {name} for rate {match.group(1)}")
            rows = [[int(value) for value in re.findall(r"\d+", row)]
                    for line in matrix.group(1).splitlines()
                    for row in line.split(";") if re.findall(r"\d+", row)]
            if len({len(row) for row in rows}) != 1:
                raise ValueError(f"ragged {name} for rate {match.group(1)}")
            components[name] = rows
        tables[match.group(1)] = components
    if len(tables) != 11:
        raise ValueError(f"expected 11 DVB-S2 rates, found {len(tables)}")
    Path(args.output).write_text(json.dumps(tables, separators=(",", ":")), encoding="utf-8")
    print(f"Extracted {len(tables)} DVB-S2 rates")


if __name__ == "__main__":
    main()
