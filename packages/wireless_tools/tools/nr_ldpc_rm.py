"""NR Rate Match LDPC tool — 5G NR LDPC rate matching (3GPP TS 38.212 §5.4.2).

Replicates MATLAB nrRateMatchLDPC. Bit selection + bit interleaving.
Verified against MATLAB golden samples.
"""
from __future__ import annotations

import json
import sys
import numpy as np

# k0 starting positions per base graph and redundancy version
_K0 = {
    1: {0: 0, 1: 17, 2: 33, 3: 56},  # BG1
    2: {0: 0, 1: 13, 2: 25, 3: 43},  # BG2
}

_Qm = {'pi/2-BPSK': 1, 'BPSK': 1, 'QPSK': 2, '16QAM': 4,
       '64QAM': 6, '256QAM': 8, '1024QAM': 10}

_NCWNODES = {66: 1, 50: 2}  # N -> bgn


def rate_match(codeword: np.ndarray, outlen: int, rv: int,
               modulation: str, nlayers: int = 1, nref: int | None = None,
               bgn: int | None = None) -> np.ndarray:
    """Rate match an LDPC-encoded codeword per 3GPP 38.212 §5.4.2.

    Args:
        codeword: LDPC encoded codeword (N bits)
        outlen: desired output length
        rv: redundancy version 0-3
        modulation: 'QPSK' | '16QAM' | '64QAM' | '256QAM' | '1024QAM' | 'pi/2-BPSK'
        nlayers: number of transmission layers 1-4
        nref: limited buffer size (None = no limit)
        bgn: base graph number (1 or 2). If None, inferred from codeword length.

    Returns:
        rate-matched output bits (outlen)
    """
    codeword = np.asarray(codeword, dtype=np.int8).reshape(-1, 1)
    N, C = codeword.shape
    if N == 0 or outlen == 0:
        return np.zeros(0, dtype=codeword.dtype)

    # Infer Zc and bgn from codeword length N.
    # Supports both unpunctured (66*Zc / 50*Zc) and punctured (64*Zc / 48*Zc).
    Zc = 0
    inferred_bgn = None
    is_punctured = False
    for candidate_bgn, ncw in [(1, 66), (2, 50)]:
        if N % ncw == 0:
            Zc = N // ncw
            inferred_bgn = candidate_bgn
            is_punctured = False
            break
    if Zc == 0:
        for candidate_bgn, ncw in [(1, 64), (2, 48)]:
            if N % ncw == 0:
                Zc = N // ncw
                inferred_bgn = candidate_bgn
                is_punctured = True
                break
    if Zc == 0:
        raise ValueError(
            f"codeword length {N} is not a valid LDPC codeword size "
            f"(expected multiple of 66/64 for BG1 or 50/48 for BG2)"
        )
    if bgn is not None:
        inferred_bgn = bgn
    bgn = inferred_bgn
    # For rate matching, we need the "full" N (including punctured bits)
    # for k0 calculation. Convert if punctured.
    if is_punctured:
        N_full = N + 2 * Zc  # add back the 2*Zc punctured systematic bits
    else:
        N_full = N
    Qm = _Qm[modulation]
    zc = Zc

    # Limit buffer (based on full codeword length including punctured/filler bits)
    if nref is not None:
        Ncb = min(N_full, nref)
    else:
        Ncb = N_full

    # k0 start position
    k0 = _k0_start(bgn, rv, Ncb, N_full, zc)

    # Rate match each code block
    out_parts = []
    for r in range(C):
        if r <= C - (outlen % (nlayers * Qm * C) if (nlayers * Qm * C) else 0) - 1:
            E = nlayers * Qm * (outlen // (nlayers * Qm * C))
        else:
            E = nlayers * Qm * (outlen // (nlayers * Qm * C) + 1)
        cw = codeword[:, r]
        # If punctured input, prepend 2*Zc filler bits to form full circular buffer
        if is_punctured:
            cw = np.concatenate([-np.ones(2 * zc, dtype=np.int8), cw])
        out_parts.append(_cbs_rate_match(cw, int(E), int(k0), int(Ncb), int(Qm)))
    return np.concatenate(out_parts).reshape(-1)


def _k0_start(bgn, rv, Ncb, N, Zc):
    if bgn == 1:
        return [0, int(17 * Ncb / N) * Zc, int(33 * Ncb / N) * Zc, int(56 * Ncb / N) * Zc][rv]
    return [0, int(13 * Ncb / N) * Zc, int(25 * Ncb / N) * Zc, int(43 * Ncb / N) * Zc][rv]


def _cbs_rate_match(d, E, k0, Ncb, Qm):
    """Rate match a single code block segment (TS 38.212 §5.4.2)."""
    # Truncate to circular buffer
    d_buf = d[:Ncb].copy()
    n_filler = int(np.sum(d_buf == -1))

    # Repeat to cover E bits
    n_effective = len(d_buf) - n_filler
    reps = int(np.ceil(E / n_effective)) if n_effective > 0 else 1
    d_rep = np.tile(d_buf, reps)

    # Shift by k0
    d_rep = np.roll(d_rep, -k0)

    # Select E non-filler bits
    e = d_rep[d_rep != -1][:E]
    if len(e) < E:
        e = np.pad(e, (0, E - len(e)))

    # Bit interleaving Section 5.4.2.2
    # MATLAB: e2 = reshape(e, E/Qm, Qm); e2 = e2.'; e2 = e2(:);
    # This means: reshape column-major (Python order='F'), transpose, flatten column-major.
    e2 = e.reshape(E // Qm, Qm, order='F').T.flatten(order='F')
    return e2[:E]


def rate_recover(softbits: np.ndarray, cwlen: int, rv: int,
                 modulation: str, nlayers: int = 1, bgn: int = 1,
                 nref: int | None = None) -> np.ndarray:
    """Rate recovery (reverse of rate_match) for LDPC decoding.

    Takes rate-matched soft bits (LLRs) and writes them back into a full
    LDPC codeword buffer, undoing the bit interleaving, circular buffer
    selection, and repetition. Positions not received are set to 0 (LLR=0
    means equally likely 0/1). Positions received multiple times are summed.

    Args:
        softbits: rate-matched soft bits (LLR values), 1-D array
        cwlen: full LDPC codeword length (punctured, i.e. N = (ncwnodes-2)*Zc)
        rv: redundancy version 0-3
        modulation: 'QPSK' | '16QAM' | '64QAM' | '256QAM' | '1024QAM'
        nlayers: number of transmission layers 1-4
        bgn: base graph number (1 or 2)
        nref: limited buffer size (None = no limit)

    Returns:
        soft codeword LLRs of length cwlen
    """
    softbits = np.asarray(softbits, dtype=np.float64).reshape(-1)
    E = len(softbits)
    if E == 0 or cwlen == 0:
        return np.zeros(cwlen, dtype=np.float64)

    Qm = _Qm[modulation]
    zc = cwlen // 64 if bgn == 1 else cwlen // 48  # approximate
    N = cwlen  # punctured codeword length

    if nref is not None:
        Ncb = min(N, nref)
    else:
        Ncb = N

    k0 = int(_k0_start(bgn, rv, Ncb, N, zc))

    # Step 1: Undo bit interleaving (de-interleave)
    # Interleaving was: e2 = e.reshape(E//Qm, Qm, order='F').T.flatten(order='F')
    # So e2 has shape (E,) with Qm groups of (E//Qm)
    # To de-interleave: reshape e2 back to (Qm, E//Qm), transpose, flatten F-order
    e2 = softbits
    e_mat = e2.reshape(Qm, E // Qm, order='F')  # (Qm, E//Qm)
    e = e_mat.T.flatten(order='F')  # (E,) de-interleaved

    # Step 2: Write soft bits back into circular buffer
    # The rate matcher selected E non-filler bits starting from position k0
    # in the circular buffer (wrapping around as needed).
    # We need to map each received bit back to its position in the codeword.

    # Build a list of positions that were selected
    # The circular buffer is d[:Ncb] (first Ncb bits of codeword)
    # Selection starts at k0, wraps around, skips filler bits.
    # For PDSCH with BG1/BG2 and single code block, there are no filler bits
    # in normal cases (filler only when codeword is very short).

    # Compute positions of selected bits in the circular buffer
    # Strategy: iterate through received bits, track position in circular buffer
    # accounting for wrap-around and filler skipping.

    d_buf_len = Ncb
    out_llr = np.zeros(cwlen, dtype=np.float64)

    # For simple case (no filler bits), positions are just:
    # pos = (k0 + i) % Ncb  for i = 0..E-1
    # But with repetition (E > Ncb), we wrap multiple times.
    # Actually the rate matcher tiles the buffer and takes E bits sequentially
    # starting from k0, skipping filler. With no filler, it's just E bits
    # starting at k0, wrapping around.

    # Verify: with no filler, n_effective = Ncb, reps = ceil(E/Ncb)
    # d_rep = tile(d_buf, reps), roll by -k0, take first E
    # So received bit i came from position (k0 + i) % Ncb in d_buf
    # (and the corresponding position in the original codeword)

    # For each received bit, find its position in the codeword and add LLR
    for i in range(E):
        pos = (k0 + i) % Ncb
        out_llr[pos] += e[i]  # sum LLRs for repeated positions

    return out_llr


def main():
    import argparse
    parser = argparse.ArgumentParser("NR Rate Match LDPC")
    parser.add_argument('--bits', required=True, help="comma-separated codeword bits")
    parser.add_argument('--outlen', type=int, required=True)
    parser.add_argument('--rv', type=int, default=0)
    parser.add_argument('--mod', default='QPSK')
    parser.add_argument('--nlayers', type=int, default=1)
    args = parser.parse_args()
    bits = np.array([int(b) for b in args.bits.split(',')], dtype=np.int8)
    out = rate_match(bits, args.outlen, args.rv, args.mod, args.nlayers)
    print(json.dumps({"outlen": args.outlen, "output_bits": out.tolist()}))


if __name__ == '__main__':
    main()
