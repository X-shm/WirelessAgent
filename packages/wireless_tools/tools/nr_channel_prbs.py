"""Independent channel-specific NR scrambling sequences."""
from __future__ import annotations

import argparse
import json
import sys

from nr_prbs import prbs


def channel_prbs(
    channel: str, nid: int, n: int, rnti: int | None = None,
    q: int = 0, v: int = 0, mapping: str = "binary",
) -> tuple[int, list[int] | list[float]]:
    """Return initialization value and PRBS bits for standard base syntaxes."""
    if channel not in ("pbch", "pdsch", "pusch", "pucch"):
        raise ValueError("channel must be pbch, pdsch, pusch or pucch")
    if not 0 <= nid <= (1007 if channel == "pbch" else 1023):
        raise ValueError("nid is outside the channel's allowed range")
    if n < 0:
        raise ValueError("n must be nonnegative")
    if mapping not in ("binary", "signed"):
        raise ValueError("mapping must be binary or signed")
    if channel == "pbch":
        if not 0 <= v <= 7:
            raise ValueError("PBCH phase v must be 0..7")
        if rnti is not None or q:
            raise ValueError("rnti and q are not PBCH inputs")
        cinit = nid
        sequence = prbs(cinit, [v * n, n], mapping)
    else:
        if rnti is None or not 0 <= rnti <= 65535:
            raise ValueError("rnti must be 0..65535")
        if v:
            raise ValueError("v is only a PBCH input")
        if q not in (0, 1):
            raise ValueError("codeword q must be 0 or 1")
        if channel == "pucch" and q:
            raise ValueError("PUCCH does not accept q")
        cinit = (rnti << 15) + (q << 14) + nid
        sequence = prbs(cinit, n, mapping)
    return cinit, sequence.tolist()


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR PBCH/PDSCH/PUSCH/PUCCH PRBS")
    parser.add_argument("--channel", choices=("pbch", "pdsch", "pusch", "pucch"), required=True)
    parser.add_argument("--nid", type=int, required=True, help="Scrambling identity / cell ID")
    parser.add_argument("--n", type=int, required=True, help="Output sequence length")
    parser.add_argument("--rnti", type=int, help="Required except for PBCH")
    parser.add_argument("--q", type=int, default=0, help="Codeword index for PDSCH/PUSCH")
    parser.add_argument("--v", type=int, default=0, help="PBCH scrambling phase")
    parser.add_argument("--mapping", choices=("binary", "signed"), default="binary")
    args = parser.parse_args()
    try:
        cinit, seq = channel_prbs(args.channel, args.nid, args.n, args.rnti, args.q, args.v, args.mapping)
        print(json.dumps({"channel": args.channel, "cinit": cinit, "seq": seq}))
    except (ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
