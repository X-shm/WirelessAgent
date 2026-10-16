"""Standalone NR CQI and PUSCH MCS lookup tables."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TABLES_PATH = Path(__file__).resolve().parents[1] / "references" / "5g_lookup_tables.json"


def lookup(family: str, table: str | None = None, index: int | None = None) -> dict:
    data = json.loads(TABLES_PATH.read_text(encoding="utf-8"))
    if family not in ("cqi", "pusch"):
        raise ValueError("family must be cqi or pusch")
    tables = data[family]
    if table is None:
        if index is not None:
            raise ValueError("index requires table")
        return {"family": family, "tables": tables}
    if table not in tables or not isinstance(tables[table], list):
        raise ValueError(f"unknown {family} table: {table}")
    rows = tables[table]
    if index is None:
        return {"family": family, "table": table, "rows": rows}
    if not isinstance(index, int) or not 0 <= index < len(rows):
        raise ValueError(f"index must be 0..{len(rows)-1}")
    return {"family": family, "table": table, "row": rows[index]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR CQI / PUSCH MCS lookup tables")
    parser.add_argument("--family", choices=("cqi", "pusch"), required=True)
    parser.add_argument("--table", help="Named CQI or PUSCH MCS table; omit to list family")
    parser.add_argument("--index", type=int, help="Optional 0-based CQI/MCS row index")
    args = parser.parse_args()
    try:
        print(json.dumps(lookup(args.family, args.table, args.index)))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
