"""Per-resource-element SISO/MIMO ZF and MMSE equalization."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import complex_json, parse_complex


def equalize(received, channel, noise_variance: float = 0.0, algorithm: str = "mmse"):
    y = np.asarray(received, dtype=complex)
    h = np.asarray(channel, dtype=complex)
    if y.ndim == 1:
        y = y[:, None]
    if h.ndim == 1:
        h = h[:, None, None]
    elif h.ndim == 2:
        h = h[:, :, None]
    if y.ndim != 2 or h.ndim != 3 or y.shape[0] != h.shape[0] or y.shape[1] != h.shape[1]:
        raise ValueError("received must be NRE-by-NRx and channel NRE-by-NRx-by-NTx")
    if noise_variance < 0 or algorithm not in ("zf", "mmse"):
        raise ValueError("noise_variance must be nonnegative and algorithm zf/mmse")
    nre, _, ntx = h.shape
    output = np.zeros((nre, ntx), complex)
    csi = np.zeros((nre, ntx), float)
    identity = np.eye(ntx)
    for index in range(nre):
        matrix = h[index]
        gram = matrix.conj().T @ matrix
        if algorithm == "zf":
            inverse = np.linalg.pinv(gram)
            gain = np.linalg.pinv(matrix)
            diagonal = np.real(np.diag(inverse))
            csi[index] = np.divide(1.0, diagonal, out=np.zeros_like(diagonal), where=diagonal > 0)
        else:
            inverse = np.linalg.pinv(gram + noise_variance * identity)
            gain = inverse @ matrix.conj().T
            diagonal = np.real(np.diag(inverse))
            csi[index] = np.divide(1.0, diagonal, out=np.zeros_like(diagonal), where=diagonal > 0)
        output[index] = gain @ y[index]
    return output, csi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--received", required=True)
    parser.add_argument("--channel", required=True)
    parser.add_argument("--noise_variance", type=float, default=0.0)
    parser.add_argument("--algorithm", choices=["zf", "mmse"], default="mmse")
    args = parser.parse_args()
    try:
        output, csi = equalize(parse_complex(args.received), parse_complex(args.channel), args.noise_variance, args.algorithm)
        print(json.dumps({"equalized": complex_json(output), "csi": csi.tolist()}))
    except (ValueError, np.linalg.LinAlgError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
