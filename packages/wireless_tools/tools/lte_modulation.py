"""
LTE Modulation Tool — LTE 调制/解调工具 (3GPP TS 36.211 §7.1).

Replicates MATLAB lteSymbolModulate / lteSymbolDemodulate from the LTE Toolbox.
Uses the extracted full mapping tables (lte_mod_tables.json) as ground truth.

Supported modulations: 'BPSK', 'QPSK', '16QAM', '64QAM', '256QAM', '1024QAM'.
"""
from __future__ import annotations

import json
import os
import re
import sys
import numpy as np

_BITS_PER_SYMBOL = {
    'BPSK': 1, 'QPSK': 2, '16QAM': 4,
    '64QAM': 6, '256QAM': 8, '1024QAM': 10,
}
_MODULATIONS = tuple(_BITS_PER_SYMBOL.keys())

_TABLES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'lte_mod_tables.json'
)

_TABLES_CACHE: dict = {}


def _load_tables() -> dict:
    if _TABLES_CACHE:
        return _TABLES_CACHE
    from collections import defaultdict
    acc = defaultdict(list)
    with open(_TABLES_PATH, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    for entry in raw:
        mod = entry['modulation']
        bps = _BITS_PER_SYMBOL[mod]
        # MATLAB jsonencode collapses 1x1 arrays to scalars; atleast_1d normalizes.
        bits = np.atleast_1d(np.asarray(entry['bits'], dtype=int)).reshape(1, bps)
        sym = np.atleast_1d(np.asarray(entry['symbols_real'], dtype=float) +
                            1j * np.asarray(entry['symbols_imag'], dtype=float))[0]
        acc[mod].append((bits, sym))
    for mod, rows in acc.items():
        _TABLES_CACHE[mod] = (np.vstack([r[0] for r in rows]),
                              np.array([r[1] for r in rows]))
    return _TABLES_CACHE


def _check_modulation(mod: str) -> None:
    if mod not in _BITS_PER_SYMBOL:
        raise ValueError(
            f"Unsupported modulation '{mod}'. Supported: {list(_MODULATIONS)}"
        )


def bits_per_symbol(mod: str) -> int:
    _check_modulation(mod)
    return _BITS_PER_SYMBOL[mod]


def modulate(bits: np.ndarray, mod: str) -> np.ndarray:
    """Map bit vector to complex modulation symbols (TS 36.211 mapping)."""
    _check_modulation(mod)
    bits = np.asarray(bits).reshape(-1)
    bps = _BITS_PER_SYMBOL[mod]
    if bits.size % bps != 0:
        raise ValueError(f"bit vector length {bits.size} not divisible by {bps}")

    tables = _load_tables()
    pats, syms = tables[mod]
    bits2d = bits.reshape(-1, bps)
    idx = np.zeros(len(bits2d), dtype=int)
    for i, row in enumerate(bits2d):
        match = np.all(pats == row, axis=1)
        if not np.any(match):
            raise ValueError(f"unmapped bit pattern {row.tolist()} for {mod}")
        idx[i] = np.nonzero(match)[0][0]
    return syms[idx]


def demodulate(symbols: np.ndarray, mod: str) -> np.ndarray:
    """Hard-decision demodulation: nearest constellation point -> bits."""
    _check_modulation(mod)
    symbols = np.asarray(symbols).reshape(-1)
    tables = _load_tables()

    pats, syms = tables[mod]
    bps = _BITS_PER_SYMBOL[mod]
    out = np.zeros(len(symbols) * bps, dtype=int)
    for i, sym in enumerate(symbols):
        d = np.abs(syms - sym)
        nearest = int(np.argmin(d))
        out[i * bps:(i + 1) * bps] = pats[nearest]
    return out


def _parse_complex_list(text: str) -> np.ndarray:
    """Parse a JSON-ish complex number list. Accepts both strict JSON numbers
    ([0.7,-0.3]) and Python complex literals ([-0.7+0.7j, 0.7-0.7j])."""
    text = text.strip()
    try:
        return np.array(json.loads(text), dtype=np.complex128)
    except Exception:
        pass
    items = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?\s*[+-]\s*\d*\.?\d+(?:[eE][-+]?\d+)?j', text)
    syms = []
    for it in items:
        it = it.replace(' ', '')
        m = re.match(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)([+-])(\d*\.?\d+(?:[eE][-+]?\d+)?)j', it)
        if m:
            re_v = float(m.group(1) if m.group(1) not in ('+', '') else '0')
            im_s = 1 if m.group(2) == '+' else -1
            im_v = float(m.group(3)) * im_s
            syms.append(complex(re_v, im_v))
    if not syms:
        raise ValueError(f"cannot parse complex list: {text}")
    return np.array(syms, dtype=np.complex128)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="LTE modulation tool")
    parser.add_argument('--mod', required=True, help="modulation")
    parser.add_argument('--bits', help="comma-separated bits, e.g. 0,1,1,0")
    parser.add_argument('--bits_hex', '--bits-hex', dest='bits_hex', help="hex string of bits (msb first)")
    parser.add_argument('--inverse', action='store_true', help="demodulate symbols")
    parser.add_argument('--symbols', help="JSON array of complex symbols, e.g. [0.7+0.7j]")
    args = parser.parse_args()

    if args.inverse:
        if not args.symbols:
            print(json.dumps({"error": "need --symbols for inverse mode"}))
            sys.exit(1)
        syms = _parse_complex_list(args.symbols)
        bits = demodulate(syms, args.mod)
        print(json.dumps({"modulation": args.mod, "bits": bits.tolist()}))
    else:
        if args.bits_hex:
            raw = args.bits_hex
            bits = np.array([int(b) for b in bin(int(raw, 16))[2:].zfill(len(raw) * 4)], dtype=int)
        else:
            bits = np.array([int(b) for b in args.bits.split(',')], dtype=int)
        syms = modulate(bits, args.mod)
        print(json.dumps({
            "modulation": args.mod,
            "bits": bits.tolist(),
            "symbols_real": syms.real.tolist(),
            "symbols_imag": syms.imag.tolist(),
        }))


if __name__ == '__main__':
    main()
