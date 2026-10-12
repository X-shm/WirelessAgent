"""NR Polar Encoder — 5G NR Polar encoding (3GPP TS 38.212 §5.3.1).

Replicates MATLAB nrPolarEncode exactly. Uses the 3GPP reliability sequence
for channel polarization. Downlink (nMax=9, iIL=true) and uplink
(nMax=10, iIL=false).

Verified against MATLAB golden samples.
"""
from __future__ import annotations

import json
import os
import sys
import numpy as np

_SEQUENCE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'matlab_oracle', 'samples', 'polar_sequence.json'
)

_SEQUENCE_CACHE: dict = {}


def _load_sequence() -> np.ndarray:
    if 'seq' not in _SEQUENCE_CACHE:
        with open(_SEQUENCE_PATH, 'r', encoding='utf-8') as f:
            _SEQUENCE_CACHE['seq'] = np.array(json.load(f), dtype=np.int32)
    return _SEQUENCE_CACHE['seq']


_KILMAX = 164
_INTERLEAVE_PATTERN = [
    0, 2, 4, 7, 9, 14, 19, 20, 24, 25, 26, 28, 31, 34, 42, 45, 49,
    50, 51, 53, 54, 56, 58, 59, 61, 62, 65, 66, 67, 69, 70, 71, 72,
    76, 77, 81, 82, 83, 87, 88, 89, 91, 93, 95, 98, 101, 104, 106,
    108, 110, 111, 113, 115, 118, 119, 120, 122, 123, 126, 127, 129,
    132, 134, 138, 139, 140, 1, 3, 5, 8, 10, 15, 21, 27, 29, 32, 35,
    43, 46, 52, 55, 57, 60, 63, 68, 73, 78, 84, 90, 92, 94, 96, 99,
    102, 105, 107, 109, 112, 114, 116, 121, 124, 128, 130, 133, 135,
    141, 6, 11, 16, 22, 30, 33, 36, 44, 47, 64, 74, 79, 85, 97, 100,
    103, 117, 125, 131, 136, 142, 12, 17, 23, 37, 48, 75, 80, 86,
    137, 143, 13, 18, 38, 144, 39, 145, 40, 146, 41, 147, 148, 149,
    150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162,
    163,
]

_SUBBLOCK_PATTERN = [0, 1, 2, 4, 3, 5, 6, 7, 8, 16, 9, 17, 10, 18, 11, 19,
                     12, 20, 13, 21, 14, 22, 15, 23, 24, 25, 26, 28, 27, 29, 30, 31]


def _interleave_map(K: int) -> np.ndarray:
    """Input interleaving map for DL polar coding (TS 38.212 §5.3.1.1)."""
    pi = []
    for m in range(_KILMAX):
        if _INTERLEAVE_PATTERN[m] >= _KILMAX - K:
            pi.append(_INTERLEAVE_PATTERN[m] - (_KILMAX - K))
    return np.array(pi, dtype=np.int32)


def _get_n(K: int, E: int, nmax: int) -> int:
    """Determine mother code size N per TS 38.212 §5.3.1 (MATLAB getN)."""
    cl2e = int(np.ceil(np.log2(E)))
    if E <= (9 / 8) * (2 ** (cl2e - 1)) and K / E < 9 / 16:
        n1 = cl2e - 1
    else:
        n1 = cl2e
    rmin = 1 / 8
    n2 = int(np.ceil(np.log2(K / rmin)))
    n_min = 5
    n = max(min(n1, n2, nmax), n_min)
    return n


def _subblock_interleave_map(N: int) -> np.ndarray:
    """Sub-block interleaver map per TS 38.212 §5.4.1.1 (for frozen bit construction)."""
    jn = np.zeros(N, dtype=np.int32)
    for n in range(N):
        i = (32 * n) // N
        jn[n] = _SUBBLOCK_PATTERN[i] * (N // 32) + (n % (N // 32))
    return jn


def _construct(K: int, E: int, nmax: int) -> tuple:
    """Construct polar code: frozen mask and info positions (MATLAB construct)."""
    n = _get_n(K, E, nmax)
    N = 2 ** n

    seq = _load_sequence()
    q_seq = seq[seq < N]

    jn = _subblock_interleave_map(N)

    qf_tmp = []
    if E < N:
        if K / E <= 7 / 16:
            for i in range(N - E):
                qf_tmp.append(int(jn[i]))
            if E >= 3 * N / 4:
                u_lim = int(np.ceil(3 * N / 4 - E / 2))
                qf_tmp.extend(range(u_lim))
            else:
                u_lim = int(np.ceil(9 * N / 16 - E / 4))
                qf_tmp.extend(range(u_lim))
            qf_tmp = sorted(set(qf_tmp))
        else:
            for i in range(E, N):
                qf_tmp.append(int(jn[i]))

    qf_tmp_set = set(qf_tmp)
    q_i = []
    for i in range(N):
        ind = int(q_seq[N - 1 - i])
        if ind in qf_tmp_set:
            continue
        q_i.append(ind)
        if len(q_i) == K:
            break

    q_i_set = set(q_i)
    q_f = [int(x) for x in q_seq if int(x) not in q_i_set]

    F = np.ones(N, dtype=np.int8)
    for p in q_i:
        F[p] = 0

    return F, q_i, q_f, N


def _polar_transform(u: np.ndarray) -> np.ndarray:
    """Polar transform: d = u * G_N where G_N = F^⊗n, F=[1,0;1,1]."""
    N = len(u)
    n = int(np.log2(N))
    x = u.copy()
    for stage in range(n):
        step = 2 ** (n - stage - 1)
        for i in range(0, N, 2 * step):
            for j in range(step):
                a = x[i + j]
                b = x[i + j + step]
                x[i + j] = a ^ b
                x[i + j + step] = b
    return x


def polar_encode(info: np.ndarray, E: int, nmax: int = 9, iil: bool = True) -> np.ndarray:
    """5G NR Polar encode per TS 38.212 §5.3.1 (replicates MATLAB nrPolarEncode).

    Args:
        info: input bits (K bits, including CRC)
        E: rate-matched output length
        nmax: 9 (DL) or 10 (UL)
        iil: true (DL input interleaving) or false (UL)

    Returns:
        N-length polar codeword (pre-rate-matching, matching MATLAB nrPolarEncode)
    """
    info = np.asarray(info, dtype=np.int8) % 2
    K = len(info)
    if K > E:
        raise ValueError(f"K={K} > E={E}")

    if iil:
        pi = _interleave_map(K)
        in_intr = info[pi]
    else:
        in_intr = info

    F, q_i, q_f, N = _construct(K, E, nmax)

    u = np.zeros(N, dtype=np.int8)
    u[F == 0] = in_intr

    d = _polar_transform(u)

    return d.astype(np.int8)


def polar_rate_match(encoded: np.ndarray, K: int, E: int) -> np.ndarray:
    """Rate-match a downlink Polar codeword per TS 38.212 §5.4.1.

    This is the non-interleaved coded-bit path used by DCI.  The input has the
    mother-code length ``N`` and the returned vector has exactly ``E`` bits.
    """
    encoded = np.asarray(encoded, dtype=np.int8).flatten() % 2
    N = len(encoded)
    if N < 32 or N & (N - 1):
        raise ValueError("encoded must have a power-of-two length of at least 32")
    if K <= 0 or E <= 0:
        raise ValueError("K and E must be positive")

    y = encoded[_subblock_interleave_map(N)]
    if E >= N:
        return y[np.arange(E) % N].astype(np.int8)
    if K / E <= 7 / 16:
        return y[N - E:].astype(np.int8)
    return y[:E].astype(np.int8)


def main():
    import argparse
    parser = argparse.ArgumentParser("NR Polar tool")
    parser.add_argument('--bits', required=True, help="comma-separated info bits")
    parser.add_argument('--E', type=int, required=True, help="output length")
    parser.add_argument('--mode', choices=['DL', 'UL'], default='DL')
    args = parser.parse_args()
    bits = np.array([int(b) for b in args.bits.split(',')], dtype=np.int8)
    nmax = 9 if args.mode == 'DL' else 10
    iil = args.mode == 'DL'
    enc = polar_encode(bits, args.E, nmax, iil)
    print(json.dumps({"mode": args.mode, "K": len(bits), "E": args.E,
                      "N": len(enc), "output_bits": enc.tolist()}))


if __name__ == '__main__':
    main()
