"""Single-symbol noninterleaved CORESET resource mapping."""
from __future__ import annotations

from _nr_remaining_common import run_cli


def pdcch_resources(nrb: int, coreset_start_rb: int = 0, coreset_nrb: int = 6,
                    symbol: int = 0, aggregation_level: int = 1,
                    candidate: int = 0, index_base: int = 1):
    if not 1 <= nrb <= 275 or not 0 <= symbol < 14:
        raise ValueError("nrb must be 1..275 and symbol 0..13")
    if coreset_nrb < 6 or coreset_nrb % 6 or coreset_start_rb < 0 or coreset_start_rb + coreset_nrb > nrb:
        raise ValueError("CORESET must occupy a multiple of 6 RBs within carrier")
    if aggregation_level not in (1, 2, 4, 8, 16) or candidate < 0 or index_base not in (0, 1):
        raise ValueError("invalid aggregation_level, candidate or index_base")
    n_cce = coreset_nrb // 6
    first_cce = candidate * aggregation_level
    if first_cce + aggregation_level > n_cce:
        raise ValueError("PDCCH candidate exceeds CORESET CCE allocation")
    data, dmrs = [], []
    for cce in range(first_cce, first_cce + aggregation_level):
        for reg in range(6):
            rb = coreset_start_rb + 6 * cce + reg
            for sc in range(12):
                index = index_base + symbol * 12 * nrb + 12 * rb + sc
                (dmrs if sc in (1, 5, 9) else data).append(index)
    return {"indices": data, "dmrs_indices": dmrs,
            "n_cce": n_cce, "aggregation_level": aggregation_level,
            "candidate": candidate}


def pdcch_space(nrb: int, coreset_start_rb: int = 0, coreset_nrb: int = 6,
                symbol: int = 0, num_candidates=None, index_base: int = 1):
    if (not 1 <= nrb <= 275 or coreset_nrb < 6 or coreset_nrb % 6 or
            coreset_start_rb < 0 or coreset_start_rb + coreset_nrb > nrb or
            not 0 <= symbol < 14 or index_base not in (0, 1)):
        raise ValueError("invalid single-symbol CORESET allocation")
    if num_candidates is None:
        num_candidates = [8, 8, 4, 2, 1]
    if len(num_candidates) != 5 or any(type(v) is not int or v < 0 for v in num_candidates):
        raise ValueError("num_candidates must contain five nonnegative integers")
    n_cce = coreset_nrb // 6
    groups = {}
    for level, count in zip((1, 2, 4, 8, 16), num_candidates):
        groups[str(level)] = [pdcch_resources(nrb, coreset_start_rb, coreset_nrb,
                                              symbol, level, candidate, index_base)
                              for candidate in range(min(count, n_cce // level))]
    return {"candidates": groups, "n_cce": n_cce}


if __name__ == "__main__":
    run_cli("Single-symbol noninterleaved NR PDCCH resources", {
        "nrPDCCHResources": pdcch_resources,
        "nrPDCCHSpace": pdcch_space,
    })
