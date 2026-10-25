"""Standalone lookup for all valid R2026a NR PUSCH precoding matrices."""
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np


CODEBOOK_PATH = Path(__file__).resolve().parents[1] / "references" / "5g_pusch_codebook.json"
CODEBOOK_TYPES = ("codebook1_ng1n4n1", "codebook1_ng1n2n2", "codebook2", "codebook3", "codebook4")


@lru_cache(maxsize=1)
def _codebook() -> dict[tuple[int, int, int, bool, str], np.ndarray]:
    payload = json.loads(CODEBOOK_PATH.read_text(encoding="utf-8"))
    entries = {}
    for record in payload["entries"]:
        key = (record["n_layers"], record["n_ports"], record["tpmi"],
               record["transform_precode"], record["codebook_type"])
        real = np.asarray(record["real"], dtype=float).reshape(key[0], key[1])
        imag = np.asarray(record["imag"], dtype=float).reshape(key[0], key[1])
        entries[key] = real + 1j * imag
    return entries


def pusch_codebook(n_layers: int, n_ports: int, tpmi: int,
                   transform_precode: bool = False,
                   codebook_type: str = "codebook1_ng1n4n1") -> np.ndarray:
    if type(n_layers) is not int or type(n_ports) is not int or type(tpmi) is not int:
        raise ValueError("n_layers, n_ports and tpmi must be integers")
    if n_ports not in (1, 2, 4, 8) or not 1 <= n_layers <= n_ports or not 0 <= tpmi <= 304:
        raise ValueError("R2026a supports n_ports=1/2/4/8, n_layers=1..n_ports, tpmi=0..304")
    if type(transform_precode) is not bool or codebook_type not in CODEBOOK_TYPES:
        raise ValueError("invalid transform_precode or codebook_type")
    if n_ports != 8 and codebook_type != CODEBOOK_TYPES[0]:
        raise ValueError("codebook_type applies only to eight-port codebooks")
    key = (n_layers, n_ports, tpmi, transform_precode,
           codebook_type if n_ports == 8 else "default")
    try:
        return _codebook()[key].copy()
    except KeyError as exc:
        raise ValueError("invalid layer/port/TPMI/codebook combination for R2026a") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent NR PUSCH codebook lookup")
    parser.add_argument("--n_layers", type=int, required=True)
    parser.add_argument("--n_ports", type=int, required=True)
    parser.add_argument("--tpmi", type=int, required=True)
    parser.add_argument("--transform_precode", action="store_true")
    parser.add_argument("--codebook_type", choices=CODEBOOK_TYPES, default=CODEBOOK_TYPES[0])
    args = parser.parse_args()
    try:
        matrix = pusch_codebook(args.n_layers, args.n_ports, args.tpmi,
                                args.transform_precode, args.codebook_type)
        print(json.dumps({"real": matrix.real.tolist(), "imag": matrix.imag.tolist(),
                          "shape": list(matrix.shape)}))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
