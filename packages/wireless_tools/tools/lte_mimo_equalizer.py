"""LTE-style joint precoder-aware MMSE MIMO equalization with CSI output."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex
from lte_csi_codebook import csi_codebook


def mimo_equalize(received, channel_estimate, noise_variance, n_layers=1, codebook_index=0, precoder=None):
    signal = np.asarray(received, dtype=complex)
    channel = np.asarray(channel_estimate, dtype=complex)
    if signal.ndim == 1:
        signal = signal[:, None]
    if channel.ndim != 3 or signal.ndim != 2 or channel.shape[:2] != signal.shape:
        raise ValueError("received must be [M,NRx] and channel_estimate [M,NRx,NTx]")
    noise, n_layers = float(noise_variance), int(n_layers)
    if noise < 0 or not np.isfinite(noise) or not 1 <= n_layers <= channel.shape[2]:
        raise ValueError("noise_variance must be finite/nonnegative and n_layers <= NTx")
    if precoder is None:
        matrix = csi_codebook(n_layers, channel.shape[2], codebook_index)
    else:
        matrix = np.asarray(precoder, dtype=complex)
        if matrix.shape != (channel.shape[2], n_layers):
            raise ValueError("precoder must have shape [NTx,n_layers]")
    output = np.zeros((len(signal), n_layers), complex)
    csi = np.zeros((len(signal), n_layers), float)
    identity = np.eye(n_layers)
    for index in range(len(signal)):
        effective = channel[index]@matrix
        gram = effective.conj().T@effective
        inverse = np.linalg.pinv(gram+noise*identity)
        output[index] = inverse@effective.conj().T@signal[index]
        csi[index] = n_layers/np.maximum(np.real(np.diag(inverse)), np.finfo(float).tiny)
    return output, csi, matrix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--link", choices=["downlink", "uplink"], required=True)
    parser.add_argument("--received", required=True)
    parser.add_argument("--channel_estimate", required=True)
    parser.add_argument("--noise_variance", type=float, required=True)
    parser.add_argument("--n_layers", type=int, default=1)
    parser.add_argument("--codebook_index", type=int, default=0)
    parser.add_argument("--precoder")
    args = parser.parse_args()
    try:
        precoder = None if args.precoder is None else parse_complex(args.precoder)
        output, csi, matrix = mimo_equalize(parse_complex(args.received), parse_complex(args.channel_estimate), args.noise_variance, args.n_layers, args.codebook_index, precoder)
        print(json.dumps({"link": args.link, "output": complex_json(output), "csi": csi.tolist(), "precoder": complex_json(matrix)}))
    except (ValueError, json.JSONDecodeError, np.linalg.LinAlgError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
