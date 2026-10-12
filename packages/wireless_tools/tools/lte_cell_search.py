"""Grid-domain LTE physical cell identity detection from PSS and SSS."""
from __future__ import annotations
import argparse
import json
import sys

import numpy as np
from _complex_io import parse_complex
from lte_pss import lte_pss
from lte_sss import lte_sss


def _score(observed, reference):
    observed = np.asarray(observed, dtype=complex).reshape(-1)
    reference = np.asarray(reference, dtype=complex).reshape(-1)
    if len(observed) != len(reference) or not np.linalg.norm(observed):
        return 0.0
    return float(abs(np.vdot(reference, observed)) ** 2 / (np.vdot(reference, reference).real * np.vdot(observed, observed).real))


def cell_search(observed_pss, observed_sss=None, sss_subframe: int | None = None):
    pss = np.asarray(observed_pss, dtype=complex).reshape(-1)
    if len(pss) != 62:
        raise ValueError("observed_pss must contain 62 symbols")
    pss_scores = [_score(pss, lte_pss(nid2, 0, "FDD")) for nid2 in range(3)]
    nid2 = int(np.argmax(pss_scores))
    result = {"nid2": nid2, "pss_score": pss_scores[nid2], "pss_scores": pss_scores}
    if observed_sss is not None:
        sss = np.asarray(observed_sss, dtype=complex).reshape(-1)
        if len(sss) != 62:
            raise ValueError("observed_sss must contain 62 symbols")
        candidates = [sss_subframe] if sss_subframe is not None else [0, 5]
        if any(value not in (0, 5) for value in candidates):
            raise ValueError("sss_subframe must be 0 or 5")
        best = (-1.0, None, None)
        for subframe in candidates:
            for nid1 in range(168):
                ncellid = 3*nid1 + nid2
                score = _score(sss, lte_sss(ncellid, subframe))
                if score > best[0]:
                    best = (score, ncellid, subframe)
        result.update({"ncellid": best[1], "nid1": best[1]//3, "sss_subframe": best[2], "sss_score": best[0]})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed_pss", required=True)
    parser.add_argument("--observed_sss")
    parser.add_argument("--sss_subframe", type=int)
    args = parser.parse_args()
    try:
        pss = parse_complex(args.observed_pss)
        sss = parse_complex(args.observed_sss) if args.observed_sss is not None else None
        print(json.dumps(cell_search(pss, sss, args.sss_subframe)))
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
