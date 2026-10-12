"""Two-port LTE PMI selection using the ltePMISelect LMMSE SINR metric."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import parse_complex
from lte_csi_codebook import csi_codebook
from lte_pmi_info import pmi_info


def pmi_select(channel_estimate, noise_variance, ndlrb, n_layers=1, pmi_mode="Wideband", codebook_subset=None):
    channel = np.asarray(channel_estimate, dtype=complex)
    if channel.ndim == 3:
        channel = channel[:, :, None, :]
    if channel.ndim != 4 or channel.shape[-1] != 2:
        raise ValueError("channel_estimate must have shape [K,L,NRx,2] or [K,L,2]")
    noise = float(noise_variance)
    if not np.isfinite(noise) or noise <= 0:
        raise ValueError("noise_variance must be positive and finite")
    info = pmi_info(ndlrb, 2, 1, pmi_mode, n_layers, "SpatialMux", False)
    candidates = list(range(4 if int(n_layers) == 1 else 2))
    if codebook_subset is not None:
        allowed = [int(value) for value in codebook_subset]
        candidates = [value for value in candidates if value in allowed]
    if not candidates:
        raise ValueError("codebook_subset excludes every valid PMI")
    sinr = np.zeros((channel.shape[0], channel.shape[1], len(candidates), int(n_layers)))
    for candidate_index, pmi in enumerate(candidates):
        precoder = csi_codebook(n_layers, 2, pmi)
        for carrier in range(channel.shape[0]):
            for symbol in range(channel.shape[1]):
                effective = channel[carrier, symbol]@precoder
                gram = effective.conj().T@effective
                den = noise*np.linalg.inv(gram+noise*np.eye(int(n_layers)))
                sinr[carrier, symbol, candidate_index] = np.maximum(np.real(1.0/np.diag(den)-1.0), 0.0)
    subband_width = 12*info["k"]
    selected, subband_sinr = [], []
    for subband in range(info["NSubbands"]):
        start, finish = subband*subband_width, min((subband+1)*subband_width, channel.shape[0])
        if start >= finish:
            break
        metric = np.mean(np.sum(sinr[start:finish], axis=3), axis=(0, 1))
        best = int(np.argmax(metric))
        selected.append(candidates[best])
        subband_sinr.append(metric.tolist())
    return selected, {**info, "Candidates": candidates, "SubbandSINR": subband_sinr}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel_estimate", required=True)
    parser.add_argument("--noise_variance", type=float, required=True)
    parser.add_argument("--ndlrb", type=int, required=True)
    parser.add_argument("--n_layers", type=int, choices=[1, 2], default=1)
    parser.add_argument("--pmi_mode", choices=["Wideband", "Subband"], default="Wideband")
    parser.add_argument("--codebook_subset")
    args = parser.parse_args()
    try:
        subset = None if args.codebook_subset is None else json.loads(args.codebook_subset)
        selected, info = pmi_select(parse_complex(args.channel_estimate), args.noise_variance, args.ndlrb, args.n_layers, args.pmi_mode, subset)
        print(json.dumps({"pmi_set": selected, "info": info}))
    except (ValueError, json.JSONDecodeError, np.linalg.LinAlgError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
