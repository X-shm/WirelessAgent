"""SISO/MIMO Shannon capacity baseline for link optimization comparisons."""
from __future__ import annotations
import argparse
import json
import math
import sys

import numpy as np
from _complex_io import parse_complex


def link_capacity(snr_db, bandwidth_hz, channel=None):
    snr, bandwidth = 10**(float(snr_db)/10.0), float(bandwidth_hz)
    if bandwidth <= 0:
        raise ValueError("bandwidth_hz must be positive")
    if channel is None:
        efficiency = math.log2(1+snr)
        streams = 1
    else:
        matrices = np.asarray(channel, dtype=complex)
        if matrices.ndim == 2:
            matrices = matrices[None, :, :]
        if matrices.ndim != 3:
            raise ValueError("channel must be [NRx,NTx] or [Nsc,NRx,NTx]")
        efficiencies = []
        for matrix in matrices:
            nrx, ntx = matrix.shape
            gram = np.eye(nrx)+(snr/ntx)*(matrix@matrix.conj().T)
            _, logdet = np.linalg.slogdet(gram)
            efficiencies.append(float(logdet/math.log(2)))
        efficiency = float(np.mean(efficiencies))
        streams = min(matrices.shape[1], matrices.shape[2])
    return {"spectral_efficiency_bps_hz": efficiency, "capacity_bps": bandwidth*efficiency, "spatial_stream_limit": streams}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snr_db", type=float, required=True)
    parser.add_argument("--bandwidth_hz", type=float, required=True)
    parser.add_argument("--channel")
    args = parser.parse_args()
    try:
        channel = None if args.channel is None else parse_complex(args.channel)
        print(json.dumps(link_capacity(args.snr_db, args.bandwidth_hz, channel)))
    except (ValueError, json.JSONDecodeError, np.linalg.LinAlgError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
