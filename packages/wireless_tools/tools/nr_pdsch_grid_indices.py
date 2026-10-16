"""Standalone single-port PDSCH and PDSCH DM-RS resource indices."""
from __future__ import annotations

import argparse
import json
import sys

from nr_dmrs import dmrs_subcarrier_locations


_MOD_BITS = {"QPSK": 2, "16QAM": 4, "64QAM": 6, "256QAM": 8, "1024QAM": 10}


def pdsch_grid_indices(
    operation: str, nrb: int, prb_set: list[int], symbol_allocation: list[int],
    dmrs_symbols: list[int], config_type: int = 1,
    num_cdm_groups_without_data: int = 2, modulation: str = "QPSK",
    index_base: str = "1based",
) -> dict:
    """Return linear carrier-grid indices for one PDSCH layer and DM-RS port 0."""
    if operation not in ("dmrs", "data"):
        raise ValueError("operation must be dmrs or data")
    if not 1 <= nrb <= 275 or config_type not in (1, 2):
        raise ValueError("nrb must be 1..275 and config_type must be 1 or 2")
    if index_base not in ("0based", "1based") or modulation not in _MOD_BITS:
        raise ValueError("invalid index_base or modulation")
    if not isinstance(prb_set, list) or not prb_set or any(
        not isinstance(rb, int) or not 0 <= rb < nrb for rb in prb_set
    ) or len(set(prb_set)) != len(prb_set):
        raise ValueError("prb_set must contain distinct RBs in 0..nrb-1")
    if not isinstance(symbol_allocation, list) or len(symbol_allocation) != 2:
        raise ValueError("symbol_allocation must be [start,length]")
    start, length = symbol_allocation
    if not isinstance(start, int) or not isinstance(length, int) or start < 0 or length < 1 or start + length > 14:
        raise ValueError("symbol_allocation must be inside a 14-symbol slot")
    if not isinstance(dmrs_symbols, list) or not dmrs_symbols or any(
        not isinstance(s, int) or s < start or s >= start + length for s in dmrs_symbols
    ) or len(set(dmrs_symbols)) != len(dmrs_symbols):
        raise ValueError("dmrs_symbols must be distinct symbols inside the allocation")
    groups = (set(range(0, 12, 2)), set(range(1, 12, 2))) if config_type == 1 else (
        {0, 1, 6, 7}, {2, 3, 8, 9}, {4, 5, 10, 11}
    )
    if not 1 <= num_cdm_groups_without_data <= len(groups):
        raise ValueError("invalid number of CDM groups without data")
    dmrs_re = set(dmrs_subcarrier_locations(config_type, 0).tolist())
    reserved_re = set().union(*groups[:num_cdm_groups_without_data])
    index_offset = int(index_base == "1based")
    nsc = 12 * nrb
    indices: list[int] = []
    for symbol in range(start, start + length):
        for rb in sorted(prb_set):
            for subcarrier in range(12):
                if operation == "dmrs":
                    include = symbol in dmrs_symbols and subcarrier in dmrs_re
                else:
                    include = symbol not in dmrs_symbols or subcarrier not in reserved_re
                if include:
                    indices.append(symbol * nsc + rb * 12 + subcarrier + index_offset)
    payload: dict = {"indices": indices, "n_indices": len(indices)}
    if operation == "data":
        payload["info"] = {"G": len(indices) * _MOD_BITS[modulation],
                           "Gd": len(indices), "DMRSSymbolSet": sorted(dmrs_symbols)}
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent single-port NR PDSCH grid indices")
    parser.add_argument("--operation", choices=("dmrs", "data"), required=True)
    parser.add_argument("--nrb", type=int, required=True)
    parser.add_argument("--prb_set", required=True, help="JSON 0-based carrier RB list")
    parser.add_argument("--symbol_allocation", required=True, help="JSON [start,length]")
    parser.add_argument("--dmrs_symbols", required=True, help="JSON explicit slot symbol list")
    parser.add_argument("--config_type", type=int, choices=(1, 2), default=1)
    parser.add_argument("--num_cdm_groups_without_data", type=int, default=2)
    parser.add_argument("--modulation", choices=tuple(_MOD_BITS), default="QPSK")
    parser.add_argument("--index_base", choices=("0based", "1based"), default="1based")
    args = parser.parse_args()
    try:
        payload = pdsch_grid_indices(
            args.operation, args.nrb, json.loads(args.prb_set),
            json.loads(args.symbol_allocation), json.loads(args.dmrs_symbols),
            args.config_type, args.num_cdm_groups_without_data,
            args.modulation, args.index_base,
        )
        print(json.dumps(payload))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
