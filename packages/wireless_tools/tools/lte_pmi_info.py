"""LTE PMI reporting metadata derived from the public ltePMIInfo M-file logic."""
from __future__ import annotations
import argparse
import json
import math
import sys


_REPORTING = {"cdd", "spatialmux", "multiuser", "port5", "port7-8", "port8", "port7-14"}


def _subset_size(scheme, layers, cell_ref_p, csi_ref_p, alt):
    size = 0
    if scheme == "cdd":
        size = {2: 2, 4: 4}.get(cell_ref_p, 0)
    elif scheme == "spatialmux" and layers > 1:
        size = {2: 6, 4: 64}.get(cell_ref_p, 0)
    elif (scheme == "spatialmux" and layers == 1) or scheme == "multiuser":
        size = {2: 4, 4: 16}.get(cell_ref_p, 0)
    elif scheme in ("port7-8", "port8"):
        size = 6 if cell_ref_p == 2 else (64 if alt else 32) if cell_ref_p == 4 else 0
    elif scheme == "port7-14":
        size = {2: 6, 4: 96 if alt else 64, 8: 109}.get(csi_ref_p, 0)
    return size


def pmi_info(ndlrb, cell_ref_p=1, csi_ref_p=1, pmi_mode="Wideband", n_layers=1, tx_scheme="SpatialMux", alt_codebook4tx=False):
    ndlrb, cell_ref_p, csi_ref_p, n_layers = map(int, (ndlrb, cell_ref_p, csi_ref_p, n_layers))
    scheme, mode, alt = tx_scheme.lower(), pmi_mode.lower(), bool(alt_codebook4tx)
    if not 6 <= ndlrb <= 110 or cell_ref_p not in (1, 2, 4) or csi_ref_p not in (1, 2, 4, 8):
        raise ValueError("invalid bandwidth, CellRefP or CSIRefP")
    if not 1 <= n_layers <= 8 or mode not in ("wideband", "subband"):
        raise ValueError("n_layers must be 1..8 and pmi_mode Wideband/Subband")
    if scheme == "port7-8" and n_layers > 2:
        raise ValueError("Port7-8 supports at most two layers")
    if scheme not in _REPORTING:
        return {"k": ndlrb, "NSubbands": 1, "MaxPMI": 0, "CodebookSubsetSize": 0}
    if mode == "wideband":
        k, nsubbands = ndlrb, 1
    else:
        k = 8 if ndlrb > 63 else 6 if ndlrb > 26 else 4 if ndlrb > 7 else ndlrb
        nsubbands = math.ceil(ndlrb/k)
    if scheme == "cdd":
        max_pmi = 0
    else:
        ports = csi_ref_p if scheme == "port7-14" else cell_ref_p
        uses_alt4 = ((scheme == "port7-14" and ports == 4) or (scheme in ("port7-8", "port8") and cell_ref_p == 4)) and alt
        if n_layers == 2 and ports == 2:
            max_pmi = 1
        elif uses_alt4:
            layer = 1 if scheme == "port8" else n_layers
            max_pmi = [[15, 15, 0, 0][layer-1], 15]
        elif scheme == "port7-14" and ports == 8:
            max_pmi = [[15, 15, 3, 3, 3, 3, 3, 0][n_layers-1], [15, 15, 15, 7, 0, 0, 0, 0][n_layers-1]]
        else:
            max_pmi = 0 if ports == 1 else (2**ports)-1
    return {"k": k, "NSubbands": nsubbands, "MaxPMI": max_pmi, "CodebookSubsetSize": _subset_size(scheme, n_layers, cell_ref_p, csi_ref_p, alt)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ndlrb", type=int, required=True)
    parser.add_argument("--cell_ref_p", type=int, choices=[1, 2, 4], default=1)
    parser.add_argument("--csi_ref_p", type=int, choices=[1, 2, 4, 8], default=1)
    parser.add_argument("--pmi_mode", choices=["Wideband", "Subband"], default="Wideband")
    parser.add_argument("--n_layers", type=int, default=1)
    parser.add_argument("--tx_scheme", default="SpatialMux")
    parser.add_argument("--alt_codebook4tx", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(pmi_info(args.ndlrb, args.cell_ref_p, args.csi_ref_p, args.pmi_mode, args.n_layers, args.tx_scheme, args.alt_codebook4tx)))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
