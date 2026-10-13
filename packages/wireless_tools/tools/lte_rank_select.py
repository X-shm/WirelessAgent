"""Two-port LTE rank indication selection using PMI LMMSE SINR metrics."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import parse_complex
from lte_pmi_select import pmi_select


def rank_select(channel_estimate, noise_variance, ndlrb, pmi_mode="Wideband", hysteresis=0.1):
    channel = np.asarray(channel_estimate, dtype=complex)
    if channel.ndim == 3:
        channel = channel[:, :, None, :]
    if channel.ndim != 4 or channel.shape[-1] != 2:
        raise ValueError("channel_estimate must be [K,L,NRx,2] or [K,L,2]")
    best_rank, best_metric, best_pmi = 1, -float("inf"), []
    metrics = {}
    for rank in (1, 2):
        pmi, info = pmi_select(channel, noise_variance, ndlrb, rank, pmi_mode)
        total = 0.0
        for subband, candidate_metrics in enumerate(info["SubbandSINR"]):
            chosen = info["Candidates"].index(pmi[subband])
            sinr = float(candidate_metrics[chosen])
            if sinr >= 1.0:
                total += rank*sinr
        metrics[str(rank)] = {"metric": total, "pmi_set": pmi}
        if total > best_metric+float(hysteresis):
            best_rank, best_metric, best_pmi = rank, total, pmi
    return {"ri": best_rank, "pmi_set": best_pmi, "rank_metrics": metrics, "hysteresis": float(hysteresis), "method": "two_port_lmmse_sinr"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel_estimate", required=True)
    parser.add_argument("--noise_variance", type=float, required=True)
    parser.add_argument("--ndlrb", type=int, required=True)
    parser.add_argument("--pmi_mode", choices=["Wideband", "Subband"], default="Wideband")
    parser.add_argument("--hysteresis", type=float, default=0.1)
    args = parser.parse_args()
    try:
        print(json.dumps(rank_select(parse_complex(args.channel_estimate), args.noise_variance, args.ndlrb, args.pmi_mode, args.hysteresis)))
    except (ValueError, json.JSONDecodeError, np.linalg.LinAlgError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
