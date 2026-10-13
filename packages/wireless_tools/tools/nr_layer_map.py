"""NR Layer Map — 5G NR layer mapping (3GPP TS 38.211 §6.3.1.2).

Replicates MATLAB nrLayerMap from the 5G Toolbox: maps one codeword of
complex modulation symbols onto nLayers transmission layers.

The i-th symbol goes to layer (i mod nLayers), column (floor(i / nLayers)).
"""
from __future__ import annotations

import json
import sys
import numpy as np


def layer_map(symbols: np.ndarray, n_layers: int) -> np.ndarray:
    """Map a 1-D complex symbol vector onto n_layers transmission layers.

    Returns an (n_layers, n_symbols // n_layers) complex array, layer-major.
    MATLAB nrLayerMap returns (n_symbols/n_layers, n_layers) — i.e. layers are
    columns, not rows. To match MATLAB exactly, we return that orientation.
    """
    symbols = np.asarray(symbols).reshape(-1)
    if n_layers < 1 or n_layers > 8:
        raise ValueError(f"n_layers must be 1..8, got {n_layers}")
    if symbols.size % n_layers != 0:
        raise ValueError(
            f"symbol count {symbols.size} not divisible by n_layers {n_layers}"
        )
    cols = symbols.size // n_layers
    out = np.empty((cols, n_layers), dtype=np.complex128)
    for i in range(symbols.size):
        out[i // n_layers, i % n_layers] = symbols[i]
    return out


def layer_demap(layered: np.ndarray, n_layers: int) -> np.ndarray:
    """Inverse of layer_map: (N, n_layers) -> 1-D symbol vector."""
    layered = np.asarray(layered)
    if layered.ndim != 2 or layered.shape[1] != n_layers:
        raise ValueError(f"expected (N, {n_layers}) array, got {layered.shape}")
    cols = layered.shape[0]
    out = np.empty(cols * n_layers, dtype=np.complex128)
    for i in range(out.size):
        out[i] = layered[i // n_layers, i % n_layers]
    return out


def _parse_complex_list(text: str) -> np.ndarray:
    import re
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
            re_v = float(m.group(1)) if m.group(1) not in ('+', '') else 0.0
            im_s = 1 if m.group(2) == '+' else -1
            im_v = float(m.group(3)) * im_s
            syms.append(complex(re_v, im_v))
    return np.array(syms, dtype=np.complex128)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NR layer mapping tool")
    parser.add_argument('--nlayers', type=int, required=True)
    parser.add_argument('--symbols', help="JSON array of complex symbols")
    parser.add_argument('--inverse', action='store_true', help="layer demap")
    args = parser.parse_args()

    if args.inverse:
        # input is layered matrix (row-major JSON), demap
        syms = _parse_complex_list(args.symbols)
        layered = syms.reshape(args.nlayers, -1)
        out = layer_demap(layered, args.nlayers)
        print(json.dumps({"n_layers": args.nlayers, "symbols_real": out.real.tolist(),
                          "symbols_imag": out.imag.tolist()}))
    else:
        syms = _parse_complex_list(args.symbols)
        out = layer_map(syms, args.nlayers)
        print(json.dumps({"n_layers": args.nlayers,
                          "symbols_real": out.real.tolist(),
                          "symbols_imag": out.imag.tolist()}))


if __name__ == '__main__':
    main()
