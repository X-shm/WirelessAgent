"""
NR Modulation Tool — 5G NR 调制/解调工具 (3GPP TS 38.211 §5.1).

Replicates MATLAB nrSymbolModulate / nrSymbolDemodulate from the 5G Toolbox.
Uses the extracted full mapping tables (mod_tables.json) as ground truth.

Supported modulations: 'BPSK', 'pi/2-BPSK', 'QPSK', '16QAM', '64QAM', '256QAM', '1024QAM'.
"""
from __future__ import annotations

import json
import os
import re
import sys
import numpy as np

_BITS_PER_SYMBOL = {
    'BPSK': 1, 'pi/2-BPSK': 1, 'QPSK': 2,
    '16QAM': 4, '64QAM': 6, '256QAM': 8, '1024QAM': 10,
}
_MODULATIONS = tuple(_BITS_PER_SYMBOL.keys())

_TABLES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'matlab_oracle', 'samples', 'mod_tables.json'
)

# Cache of loaded tables: {modulation: (bit_patterns_2d, symbols)}
_TABLES_CACHE: dict = {}


def _load_tables() -> dict:
    if _TABLES_CACHE:
        return _TABLES_CACHE
    with open(_TABLES_PATH, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    for entry in raw:
        mod = entry['modulation']
        if mod == 'pi/2-BPSK':
            # Handled by the analytic rotation path; skip table load.
            continue
        bps = _BITS_PER_SYMBOL[mod]
        n = entry['n_symbols']
        bits = np.array(entry['bits'], dtype=int).reshape(n, bps)
        syms = np.array(entry['symbols_real']) + 1j * np.array(entry['symbols_imag'])
        _TABLES_CACHE[mod] = (bits, syms)
    return _TABLES_CACHE


def _check_modulation(mod: str) -> None:
    if mod not in _BITS_PER_SYMBOL:
        raise ValueError(
            f"Unsupported modulation '{mod}'. Supported: {list(_MODULATIONS)}"
        )


def bits_per_symbol(mod: str) -> int:
    _check_modulation(mod)
    return _BITS_PER_SYMBOL[mod]


def _pi2_bpsk_stream(bits: np.ndarray) -> np.ndarray:
    """pi/2-BPSK per MATLAB nrSymbolModulate.

    Base symbols (unit amplitude): bit 0 -> +0.7071+0.7071j, bit 1 -> -0.7071-0.7071j,
    i.e. (1-2b) * (1+j)/sqrt(2). Odd-indexed symbols (i % 2 == 1) are rotated
    by +90deg (multiply by j).
    """
    k = 0.7071067811865476  # 1/sqrt(2)
    base = k * (1 - 2 * bits.astype(np.complex128)) * (1 + 1j)
    phase = np.exp(1j * (np.pi / 2) * (np.arange(len(bits)) % 2))
    return base * phase


def modulate(bits: np.ndarray, mod: str) -> np.ndarray:
    """Map bit vector to complex modulation symbols."""
    _check_modulation(mod)
    bits = np.asarray(bits).reshape(-1)
    bps = _BITS_PER_SYMBOL[mod]
    if bits.size % bps != 0:
        raise ValueError(f"bit vector length {bits.size} not divisible by {bps}")

    if mod == 'pi/2-BPSK':
        return _pi2_bpsk_stream(bits)

    tables = _load_tables()
    pats, syms = tables[mod]
    bits2d = bits.reshape(-1, bps)
    # Map each symbol's bit pattern to its table row
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

    if mod == 'pi/2-BPSK':
        # Undo the odd-index +90deg rotation; sign of Re((1-2b)*(1+j)) = real part gives the bit.
        phase = np.exp(-1j * (np.pi / 2) * (np.arange(len(symbols)) % 2))
        sym_rot = symbols * phase
        return np.where(sym_rot.real >= 0, 0, 1)

    pats, syms = tables[mod]
    bps = _BITS_PER_SYMBOL[mod]
    out = np.zeros(len(symbols) * bps, dtype=int)
    for i, sym in enumerate(symbols):
        d = np.abs(syms - sym)
        nearest = int(np.argmin(d))
        out[i * bps:(i + 1) * bps] = pats[nearest]
    return out


def soft_demodulate(symbols: np.ndarray, mod: str, noise_var: float = 1.0) -> np.ndarray:
    """Soft-decision demodulation: LLR values for each bit.

    Uses max-log-MAP approximation:
      LLR(b_k) = min_{s where b_k=1} |r-s|^2 - min_{s where b_k=0} |r-s|^2
    Scaled by -1/noise_var to get proper LLR.

    Args:
        symbols: received complex symbols
        mod: modulation scheme
        noise_var: noise variance (sigma^2)

    Returns:
        LLR values (positive means bit=0 is more likely, negative means bit=1).
        Convention: LLR = log(P(b=0|r) / P(b=1|r)), so LLR > 0 means bit=0.
    """
    _check_modulation(mod)
    symbols = np.asarray(symbols).reshape(-1)
    tables = _load_tables()

    if noise_var <= 0:
        noise_var = 1e-10

    if mod == 'pi/2-BPSK':
        phase = np.exp(-1j * (np.pi / 2) * (np.arange(len(symbols)) % 2))
        sym_rot = symbols * phase
        # LLR = 4 * real(sym_rot) / noise_var
        # (positive real -> bit 0, negative real -> bit 1)
        # Matches MATLAB convention: total complex noise power noise_var
        return 4.0 * sym_rot.real / noise_var

    pats, syms = tables[mod]
    bps = _BITS_PER_SYMBOL[mod]
    n_syms = len(syms)
    out = np.zeros(len(symbols) * bps, dtype=np.float64)

    for i, sym in enumerate(symbols):
        # Compute squared distances to all constellation points
        dist2 = np.abs(syms - sym) ** 2

        # For each bit position, find min distance for bit=0 and bit=1
        for b in range(bps):
            # Get the bit value at position b for each constellation point
            bit_vals = pats[:, b]
            d0 = np.min(dist2[bit_vals == 0])
            d1 = np.min(dist2[bit_vals == 1])
            # LLR = (d1 - d0) / noise_var  (max-log-MAP)
            # P(r|b) ~ exp(-|r-s|^2 / noise_var) for complex AWGN
            # where noise_var is total complex noise power
            # L > 0 means bit=0 is more likely.
            llr = (d1 - d0) / noise_var
            out[i * bps + b] = llr

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
    parser = argparse.ArgumentParser(description="NR modulation tool")
    parser.add_argument('--mod', required=True, help="modulation")
    parser.add_argument('--bits', help="comma-separated bits, e.g. 0,1,1,0")
    parser.add_argument('--bits-hex', help="hex string of bits (msb first)")
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
