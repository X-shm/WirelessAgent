"""Standalone PDSCH PRG precoding for one resource index per layer and RE."""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from _complex_io import complex_json, parse_complex
from nr_prg_info import prg_info


def pdsch_precode(port_sym: np.ndarray, port_ind: np.ndarray, weights: np.ndarray,
                  nrb: int, nstartgrid: int = 0, prg_size: int | None = None,
                  index_base: str = "1based", symbols_per_slot: int = 14) -> tuple[np.ndarray, np.ndarray]:
    """Apply the per-PRG layer-to-antenna matrix to PDSCH port symbols."""
    symbols = np.asarray(port_sym, dtype=complex)
    indices = np.asarray(port_ind)
    precoders = np.asarray(weights, dtype=complex)
    if symbols.ndim != 2 or symbols.shape[0] == 0:
        raise ValueError("port_sym must be a nonempty NRE x NLayers matrix")
    if indices.shape != symbols.shape or not np.issubdtype(indices.dtype, np.integer):
        raise ValueError("port_ind must be an integer matrix matching port_sym")
    if np.any(indices != indices[:, :1]):
        raise ValueError("this subset requires the same RE index for every layer")
    if symbols_per_slot not in (12, 14) or index_base not in ("0based", "1based"):
        raise ValueError("invalid symbols_per_slot or index_base")
    info = prg_info(nrb, nstartgrid, prg_size)
    if precoders.ndim == 2:
        precoders = precoders[:, :, np.newaxis]
    if precoders.ndim != 3 or precoders.shape[0] != symbols.shape[1] or precoders.shape[1] == 0:
        raise ValueError("weights must be NLayers x NAntennas x NPRG")
    if precoders.shape[2] != info["NPRG"]:
        raise ValueError(f"weights require {info['NPRG']} PRG matrices")
    offset = int(index_base == "1based")
    plane_length = nrb * 12 * symbols_per_slot
    linear = indices[:, 0].astype(np.int64) - offset
    if np.any(linear < 0) or np.any(linear >= plane_length):
        raise ValueError("port_ind contains an out-of-grid RE")
    rb = (linear % (nrb * 12)) // 12
    groups = np.asarray(info["PRGSet"], dtype=np.int64)[rb] - 1
    antenna_symbols = np.empty((symbols.shape[0], precoders.shape[1]), dtype=complex)
    for row, group in enumerate(groups):
        antenna_symbols[row] = symbols[row] @ precoders[:, :, group]
    antenna_indices = indices[:, :1].astype(np.int64) + np.arange(precoders.shape[1]) * plane_length
    return antenna_symbols, antenna_indices


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent PDSCH PRG precoding")
    parser.add_argument("--port_sym", required=True, help="Complex JSON NRE x NLayers matrix")
    parser.add_argument("--port_ind", required=True, help="JSON NRE x NLayers RE index matrix")
    parser.add_argument("--weights", required=True, help="Complex JSON NLayers x NAntennas x NPRG array")
    parser.add_argument("--nrb", type=int, required=True)
    parser.add_argument("--nstartgrid", type=int, default=0)
    parser.add_argument("--prg_size", type=int, choices=(2, 4), help="Omit for wideband")
    parser.add_argument("--index_base", choices=("0based", "1based"), default="1based")
    parser.add_argument("--symbols_per_slot", type=int, choices=(12, 14), default=14)
    args = parser.parse_args()
    try:
        symbols, indices = pdsch_precode(
            parse_complex(args.port_sym), np.asarray(json.loads(args.port_ind)),
            parse_complex(args.weights), args.nrb, args.nstartgrid,
            args.prg_size, args.index_base, args.symbols_per_slot,
        )
        print(json.dumps({"ant_sym": complex_json(symbols), "ant_ind": indices.tolist(),
                          "n_re": len(symbols), "n_antennas": symbols.shape[1]}))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
