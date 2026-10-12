"""WLAN LDPC Tool — IEEE 802.11 LDPC 编解码工具.

Replicates MATLAB wlan.internal.ldpcEncodeCore / wlanLDPCDecode
from the WLAN Toolbox. H matrices exported from MATLAB wlan.internal.ldpcMatrix.

Supports code rates: 1/2, 2/3, 3/4, 5/6
Block lengths: 648, 1296, 1944
"""
from __future__ import annotations

import json
import os
import sys
import numpy as np

_MATRICES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'matlab_oracle', 'samples', 'wlan_ldpc_matrices.json'
)

# Valid rate -> block_length combinations
_RATE_MAP = {
    '1/2': {'num': 1, 'den': 2, 'key': 'rate1_2'},
    '2/3': {'num': 2, 'den': 3, 'key': 'rate2_3'},
    '3/4': {'num': 3, 'den': 4, 'key': 'rate3_4'},
    '5/6': {'num': 5, 'den': 6, 'key': 'rate5_6'},
}

_VALID_BLOCKS = [648, 1296, 1944]

# Cache loaded matrices
_H_CACHE = {}


def _load_H(rate_str: str, block_length: int) -> np.ndarray:
    """Load parity-check matrix H from exported JSON data."""
    cache_key = (rate_str, block_length)
    if cache_key in _H_CACHE:
        return _H_CACHE[cache_key]

    with open(_MATRICES_PATH, 'r', encoding='utf-8') as f:
        all_mats = json.load(f)

    rate_info = _RATE_MAP[rate_str]
    mat_key = f"{rate_info['key']}_blk{block_length}"
    if mat_key not in all_mats:
        raise ValueError(f"matrix {mat_key} not found")

    data = all_mats[mat_key]
    n_rows = data['n_rows']
    n_cols = data['n_cols']
    rows = np.array(data['rows'], dtype=int)
    cols = np.array(data['cols'], dtype=int)

    H = np.zeros((n_rows, n_cols), dtype=np.uint8)
    H[rows, cols] = 1
    _H_CACHE[cache_key] = H
    return H


def _gf2_solve(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Solve A x = b over GF(2) via Gaussian elimination."""
    A = A.astype(np.uint8)
    b = b.astype(np.uint8) % 2
    m, n = A.shape
    aug = np.zeros((m, n + 1), dtype=np.uint8)
    aug[:, :n] = A
    aug[:, n] = b % 2

    piv_cols = []
    row = 0
    for col in range(n):
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

    x = np.zeros(n, dtype=np.uint8)
    for idx, col in enumerate(piv_cols):
        x[col] = aug[idx, n]
    return x.astype(np.int8)


def encode(info_bits: np.ndarray, rate: str, block_length: int) -> np.ndarray:
    """LDPC encode — returns [info_bits; parity_bits].

    Args:
        info_bits: Information bit array (0/1), length = block_length * rate
        rate: Code rate — '1/2', '2/3', '3/4', or '5/6'
        block_length: LDPC codeword length — 648, 1296, or 1944

    Returns:
        Full codeword = [info_bits; parity_bits], length = block_length
    """
    info_bits = np.asarray(info_bits, dtype=np.int8).reshape(-1)
    n_info = len(info_bits)
    expected_info = int(block_length * _RATE_MAP[rate]['num'] / _RATE_MAP[rate]['den'])

    if n_info != expected_info:
        raise ValueError(
            f"input length {n_info} != expected {expected_info} "
            f"for rate {rate}, block_length {block_length}"
        )

    H = _load_H(rate, block_length)
    n_rows, n_cols = H.shape
    n_parity = n_rows  # parity bits = number of check rows

    # H = [H1 | H2] where H1 covers info bits, H2 covers parity bits
    H1 = H[:, :n_info]
    H2 = H[:, n_info:]

    # H1 @ info + H2 @ parity = 0  =>  H2 @ parity = H1 @ info (mod 2)
    rhs = (H1.astype(np.uint8) @ info_bits.astype(np.uint8)) % 2
    parity = _gf2_solve(H2, rhs)

    codeword = np.concatenate([info_bits, parity]).astype(np.int8)
    return codeword


def decode(llr: np.ndarray, rate: str, block_length: int,
           max_iter: int = 20, alpha: float = 0.75) -> np.ndarray:
    """LDPC decode — normalized min-sum BP.

    Args:
        llr: Log-likelihood ratio array, length = block_length
        rate: Code rate — '1/2', '2/3', '3/4', or '5/6'
        block_length: LDPC codeword length
        max_iter: Maximum BP iterations
        alpha: Normalization factor for min-sum

    Returns:
        Decoded information bits (hard decision)
    """
    llr = np.asarray(llr, dtype=np.float64).reshape(-1)
    n_info = int(block_length * _RATE_MAP[rate]['num'] / _RATE_MAP[rate]['den'])

    if len(llr) != block_length:
        raise ValueError(f"LLR length {len(llr)} != block_length {block_length}")

    H = _load_H(rate, block_length)
    n_v = H.shape[1]

    # Build adjacency lists
    nz_r, nz_c = np.nonzero(H)
    edges_c = [[] for _ in range(H.shape[0])]
    edges_v = [[] for _ in range(n_v)]
    for e, (r, c) in enumerate(zip(nz_r, nz_c)):
        edges_c[r].append(e)
        edges_v[c].append(e)
    col_of = nz_c

    L = llr.copy()
    n_edges = len(nz_r)
    msg_cv = np.zeros(n_edges)

    for _ in range(max_iter):
        # Check node update (min-sum)
        for r in range(H.shape[0]):
            if not edges_c[r]:
                continue
            edge_indices = edges_c[r]
            local = np.array([L[col_of[e]] - msg_cv[e] for e in edge_indices])
            signs = np.sign(local)
            signs[signs == 0] = 1
            sp = np.prod(signs)
            av = np.abs(local)
            idx = np.argmin(av)
            min_v = av[idx]
            if len(av) > 1:
                min2 = np.min(np.concatenate([av[:idx], av[idx + 1:]]))
            else:
                min2 = np.inf
            for i, e in enumerate(edge_indices):
                s = sp * np.sign(local[i])
                m_val = min2 if (i == idx and min2 != np.inf) else min_v
                msg_cv[e] = alpha * s * m_val

        # Variable node update
        for c in range(n_v):
            if not edges_v[c]:
                continue
            L[c] = llr[c] + sum(msg_cv[e] for e in edges_v[c])

        # Early termination: check parity
        hard = (L < 0).astype(np.int8)
        if np.all((H @ hard) % 2 == 0):
            break

    return hard[:n_info]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="WLAN LDPC tool")
    parser.add_argument('--mode', choices=['encode', 'decode'], required=True)
    parser.add_argument('--rate', choices=['1/2', '2/3', '3/4', '5/6'],
                        required=True, help="code rate")
    parser.add_argument('--block-length', type=int, choices=[648, 1296, 1944],
                        required=True, help="LDPC codeword length")
    parser.add_argument('--bits', help="comma-separated info bits (encode)")
    parser.add_argument('--llr', help="JSON array of LLR values (decode)")
    parser.add_argument('--max-iter', type=int, default=20)
    parser.add_argument('--alpha', type=float, default=0.75,
                        help="min-sum normalization factor")
    args = parser.parse_args()

    if args.mode == 'encode':
        bits = np.array([int(b) for b in args.bits.split(',')], dtype=np.int8)
        cw = encode(bits, args.rate, args.block_length)
        print(json.dumps({
            "rate": args.rate,
            "block_length": args.block_length,
            "n_info": len(bits),
            "info_bits": bits.tolist(),
            "codeword": cw.tolist()
        }))
    else:
        llr = np.array(json.loads(args.llr), dtype=np.float64)
        dec = decode(llr, args.rate, args.block_length, args.max_iter, args.alpha)
        print(json.dumps({
            "rate": args.rate,
            "block_length": args.block_length,
            "decoded_bits": dec.tolist()
        }))


if __name__ == '__main__':
    main()
