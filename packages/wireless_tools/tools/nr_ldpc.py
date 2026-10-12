"""
NR LDPC Tool — 5G NR LDPC 编解码工具 (3GPP TS 38.212 §5.3.2).

Replicates MATLAB nrLDPCEncode / nrLDPCDecode from the 5G Toolbox.
Base graphs exported from MATLAB baseGraph.mat, verified against golden samples.

Supports BG1 (code rate 22/66) and BG2 (code rate 10/50).
"""
from __future__ import annotations

import json
import os
import sys
import numpy as np

_BASE_GRAPHS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'matlab_oracle', 'samples', 'base_graphs.json'
)

# Supported lifting sizes per 5G NR (TS 38.212)
_ZC_SET = {
    1: [2, 4, 8, 16, 32, 64, 128, 256],
    2: [3, 6, 12, 24, 48, 96, 192, 384],
    3: [5, 10, 20, 40, 80, 160, 320],
    4: [7, 14, 28, 56, 112, 224],
    5: [9, 18, 36, 72, 144, 288],
    6: [11, 22, 44, 88, 176, 352],
    7: [13, 26, 52, 104, 208],
    8: [15, 30, 60, 120, 240],
}

# Base graph dimensions
_BG_NSYS = {1: 22, 2: 10}
_BG_NCWNODES = {1: 66, 2: 50}


def _load_base_graph(bgn: int, zc: int) -> np.ndarray:
    """Load the V matrix (shift values) for a base graph + lifting size."""
    with open(_BASE_GRAPHS_PATH, 'r', encoding='utf-8') as f:
        all_bgs = json.load(f)
    set_idx = None
    for s, sizes in _ZC_SET.items():
        if zc in sizes:
            set_idx = s
            break
    if set_idx is None:
        raise ValueError(f"unsupported lifting size Zc={zc}")
    key = f"BG{bgn}S{set_idx}"
    if key not in all_bgs:
        raise ValueError(f"base graph {key} not in exported data")
    return np.array(all_bgs[key], dtype=int)


def _calc_shift_values(V: np.ndarray, zc: int) -> np.ndarray:
    """P(i,j) = mod(V(i,j), Zc), or -1 if V(i,j) == -1."""
    P = V.copy()
    mask = V != -1
    P[mask] = np.mod(V[mask], zc)
    return P


def _quasi_cyclic_matrix(zc: int, P: np.ndarray) -> np.ndarray:
    """Construct the parity-check matrix H from base graph shift values P.

    Each non-null entry (i,j) with shift p expands to a zc x zc circulant
    permutation matrix (identity shifted right by p). Null entries (-1) are
    all-zero zc x zc blocks.
    """
    rows, cols = P.shape
    H = np.zeros((rows * zc, cols * zc), dtype=np.uint8)
    for i in range(rows):
        for j in range(cols):
            p = P[i, j]
            if p == -1:
                continue
            for r in range(zc):
                c = (r + p) % zc
                H[i * zc + r, j * zc + c] = 1
    return H


def _mod2_mul(A: np.ndarray, x: np.ndarray) -> np.ndarray:
    """A @ x over GF(2)."""
    return (A @ x) % 2


def encode(info_bits: np.ndarray, bgn: int, zc: int | None = None) -> np.ndarray:
    """LDPC encode per nrLDPCEncode. info_bits length must be nsys*Zc.

    If zc is given, info_bits is zero-padded or truncated to nsys*zc.
    Otherwise zc is inferred from info_bits.size // nsys.
    """
    info_bits = np.asarray(info_bits, dtype=np.int8).reshape(-1)
    nsys = _BG_NSYS[bgn]
    if zc is None:
        zc = info_bits.size // nsys
        if info_bits.size != nsys * zc or zc == 0:
            raise ValueError(f"input length {info_bits.size} not nsys({nsys})*Zc")
    else:
        target = nsys * zc
        if info_bits.size < target:
            info_bits = np.pad(info_bits, (0, target - info_bits.size))
        elif info_bits.size > target:
            info_bits = info_bits[:target]

    V = _load_base_graph(bgn, zc)
    P = _calc_shift_values(V, zc)
    H = _quasi_cyclic_matrix(zc, P)
    nrows, ncols = H.shape
    # Full codeword = nsys systematic columns + (nrows) parity columns.
    # nsys*zc info bits sit in the first nsys*zc columns; the first 2*zc
    # systematic columns are punctured from the output (per nrLDPCEncode).
    n_info = nsys * zc
    H1 = H[:, :n_info]
    H2 = H[:, n_info:]

    # H1 @ info + H2 @ parity = 0  =>  H2 @ parity = H1 @ info (over GF2)
    rhs = _mod2_mul(H1, info_bits)
    n_parity = H2.shape[1]
    parity = _gf2_solve(H2, rhs, n_parity)

    codeword = np.concatenate([info_bits, parity]).astype(np.int8)
    # nrLDPCEncode punctures the first 2*Zc systematic bits
    return codeword[2 * zc:]


def _gf2_solve(A: np.ndarray, b: np.ndarray, n_unknowns: int) -> np.ndarray:
    """Solve A x = b over GF(2) via Gaussian elimination (A is 0/1)."""
    A = A.astype(np.uint8)
    b = b.astype(np.uint8) % 2
    m, n = A.shape
    aug = np.zeros((m, n + 1), dtype=np.uint8)
    aug[:, :n] = A
    aug[:, n] = b % 2

    piv_cols = []
    row = 0
    for col in range(n):
        # find pivot
        piv = -1
        for r in range(row, m):
            if aug[r, col]:
                piv = r
                break
        if piv == -1:
            continue
        aug[[row, piv]] = aug[[piv, row]]
        for r in range(m):
            if r != row and aug[r, col]:
                aug[r] ^= aug[row]
        piv_cols.append(col)
        row += 1

    # Back-substitution: free variables = 0
    x = np.zeros(n, dtype=np.uint8)
    for idx, col in enumerate(piv_cols):
        x[col] = aug[idx, n]
    return x.astype(np.int8)


def decode(llr: np.ndarray, bgn: int, max_iter: int = 8) -> np.ndarray:
    """LDPC decode, matching nrLDPCDecode.

    Input LLR is the punctured codeword (first 2*Zc systematic bits omitted).
    Returns the full nsys*Zc information bits.

    Strategy: recover the 2*Zc punctured systematic bits via hard-decision
    GF(2) solving on H, then run BP on the full unpunctured codeword.
    """
    llr = np.asarray(llr, dtype=np.float64).reshape(-1)
    nsys = _BG_NSYS[bgn]
    ncwnodes = _BG_NCWNODES[bgn]
    zc = llr.size // ncwnodes
    if llr.size == ncwnodes * zc:
        is_punctured = True
    elif llr.size == (ncwnodes + 2) * zc:
        is_punctured = False
    else:
        raise ValueError(f"LLR length {llr.size} invalid for BG{bgn}; Zc≈{zc}")

    V = _load_base_graph(bgn, zc)
    P = _calc_shift_values(V, zc)
    H = _quasi_cyclic_matrix(zc, P)

    if not is_punctured:
        # Straight BP on full codeword → already works
        return _bp_decode(H, llr, nsys, zc, max_iter)

    # ── Punctured path: recover erased bits via GF(2) ─────────────────
    # Known: cw_known = llr_p[16:] = [sys(16:176), parity(176:368)]
    # Unknown: punctured = cw_p[0:16]
    # H·[punctured; known] = 0 (mod 2). Solve for punctured.
    n_v = H.shape[1]
    punctured_cols = slice(0, 2 * zc)
    known_cols = slice(2 * zc, n_v)
    H_punct = H[:, punctured_cols]
    H_known = H[:, known_cols]

    # Hard decision on known bits from LLR
    known_bits = (llr < 0).astype(np.uint8)
    rhs = _mod2_mul(H_known, known_bits)
    punctured_bits = _gf2_solve(H_punct, rhs, 2 * zc)

    # Full codeword with HFBI-recovered punctured bits
    full_cw = np.concatenate([punctured_bits, known_bits])
    llr_full = np.zeros(n_v, dtype=np.float64)
    llr_full[punctured_cols] = (1 - 2 * punctured_bits.astype(float)) * 5.0  # mild LLR
    llr_full[known_cols] = llr

    return _bp_decode(H, llr_full, nsys, zc, max_iter)


def _bp_decode(H, llr_in, nsys, zc, max_iter):
    """Normalized min-sum BP decoder (unpunctured input)."""
    n_v = H.shape[1]
    nz_r, nz_c = np.nonzero(H)
    edges_c = [[] for _ in range(H.shape[0])]
    edges_v = [[] for _ in range(n_v)]
    for e, (r, c) in enumerate(zip(nz_r, nz_c)):
        edges_c[r].append(e)
        edges_v[c].append(e)
    col_of = nz_c

    L = llr_in.copy()
    n_edges = len(nz_r)
    msg_cv = np.zeros(n_edges)
    for _ in range(max_iter):
        for r in range(H.shape[0]):
            if not edges_c[r]:
                continue
            local = np.array([L[col_of[e]] - msg_cv[e] for e in edges_c[r]])
            signs = np.sign(local)
            signs[signs == 0] = 1
            sp = np.prod(signs)
            av = np.abs(local)
            idx = np.argmin(av)
            min_v = av[idx]
            min2 = np.min(np.concatenate([av[:idx], av[idx + 1:]])) if len(av) > 1 else np.inf
            for i, e in enumerate(edges_c[r]):
                s = sp * np.sign(local[i])
                m_val = min2 if (i == idx and min2 != np.inf) else min_v
                msg_cv[e] = 0.8 * s * m_val
                L[col_of[e]] = llr_in[col_of[e]] + np.sum([msg_cv[ev] for ev in edges_v[col_of[e]]])
        hard = (L < 0).astype(np.int8)
        if np.all((H @ hard) % 2 == 0):
            break
    return hard[:nsys * zc]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NR LDPC tool")
    parser.add_argument('--mode', choices=['encode', 'decode'], required=True)
    parser.add_argument('--bgn', type=int, choices=[1, 2], required=True)
    parser.add_argument('--zc', type=int, required=True, help="lifting size")
    parser.add_argument('--bits', help="comma-separated info bits")
    parser.add_argument('--hex', help="hex string of info bits (msb first)")
    parser.add_argument('--llr', help="JSON array of LLR values for decode")
    parser.add_argument('--max-iter', type=int, default=8)
    args = parser.parse_args()

    if args.mode == 'encode':
        if args.hex:
            raw = args.hex
            bits = np.array([int(b) for b in bin(int(raw, 16))[2:].zfill(len(raw) * 4)], dtype=np.int8)
        else:
            bits = np.array([int(b) for b in args.bits.split(',')], dtype=np.int8)
        cw = encode(bits, args.bgn, args.zc)
        nsys = _BG_NSYS[args.bgn]
        info_out = np.zeros(nsys * args.zc, dtype=np.int8)
        info_out[:bits.size] = bits[:nsys * args.zc]
        print(json.dumps({"bgn": args.bgn, "zc": args.zc, "info_bits": info_out.tolist(),
                          "codeword": cw.tolist()}))
    else:
        llr = np.array(json.loads(args.llr), dtype=np.float64)
        dec = decode(llr, args.bgn, args.max_iter)
        print(json.dumps({"bgn": args.bgn, "decoded": dec.tolist()}))


if __name__ == '__main__':
    main()
