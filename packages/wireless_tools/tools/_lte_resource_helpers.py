"""Shared parsing and modulation helpers for LTE resource-index tools."""
from __future__ import annotations

import json


def slot_prbs(prb_set, nrb: int):
    value = json.loads(prb_set) if isinstance(prb_set, str) else prb_set
    if not isinstance(value, list) or not value:
        raise ValueError("prb_set must be a nonempty JSON array")
    slots = value if isinstance(value[0], list) else [value, value]
    if len(slots) != 2 or not all(isinstance(slot, list) and slot for slot in slots):
        raise ValueError("two-slot allocation must be [slot0_prbs,slot1_prbs]")
    parsed = [[int(prb) for prb in slot] for slot in slots]
    if any(len(set(slot)) != len(slot) or any(prb < 0 or prb >= int(nrb) for prb in slot) for slot in parsed):
        raise ValueError("PRB indices must be unique and within the configured bandwidth")
    return parsed


def modulation_order(name: str) -> int:
    orders = {"BPSK": 1, "QPSK": 2, "16QAM": 4, "64QAM": 6, "256QAM": 8, "1024QAM": 10}
    key = name.strip().upper()
    if key not in orders:
        raise ValueError(f"unsupported modulation {name!r}")
    return orders[key]
