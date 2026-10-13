"""LTE one/two-port CSI codebooks and closed-loop spatial precoding."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def csi_codebook(n_layers, ports, index):
    n_layers, ports, index = int(n_layers), int(ports), int(index)
    if ports == 1:
        if n_layers != 1 or index != 0:
            raise ValueError("one port requires one layer and codebook index 0")
        return np.ones((1, 1), complex)
    if ports != 2 or n_layers not in (1, 2):
        raise ValueError("independent codebook coverage supports one or two ports and layers <= ports")
    if n_layers == 1:
        phases = [1, -1, 1j, -1j]
        if not 0 <= index < len(phases):
            raise ValueError("two-port rank-1 codebook index must be 0..3")
        return np.asarray([[1], [phases[index]]], complex)/math.sqrt(2.0)
    if index not in (0, 1):
        raise ValueError("two-port rank-2 codebook index must be 0 or 1")
    phase = 1 if index == 0 else 1j
    return np.asarray([[1, 1], [phase, -phase]], complex)/2.0


def dl_precode(layers, ports, codebook_index):
    data = np.asarray(layers, dtype=complex)
    if data.ndim == 1:
        data = data[:, None]
    matrix = csi_codebook(data.shape[1], ports, codebook_index)
    return data@matrix.T, matrix


def dl_deprecode(antennas, n_layers, codebook_index):
    data = np.asarray(antennas, dtype=complex)
    if data.ndim == 1:
        data = data[:, None]
    matrix = csi_codebook(n_layers, data.shape[1], codebook_index)
    return data@np.linalg.pinv(matrix.T), matrix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["codebook", "precode", "deprecode"], required=True)
    parser.add_argument("--n_layers", type=int, required=True)
    parser.add_argument("--ports", type=int, choices=[1, 2], required=True)
    parser.add_argument("--codebook_index", type=int, required=True)
    parser.add_argument("--values")
    args = parser.parse_args()
    try:
        matrix = csi_codebook(args.n_layers, args.ports, args.codebook_index)
        if args.mode == "codebook":
            result = {"codebook": complex_json(matrix)}
        else:
            if args.values is None:
                raise ValueError("precode/deprecode mode requires values")
            values = parse_complex(args.values)
            if args.mode == "precode":
                output, _ = dl_precode(values, args.ports, args.codebook_index)
            else:
                output, _ = dl_deprecode(values, args.n_layers, args.codebook_index)
            result = {"output": complex_json(output), "codebook": complex_json(matrix)}
        print(json.dumps(result))
    except (ValueError, json.JSONDecodeError, np.linalg.LinAlgError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
