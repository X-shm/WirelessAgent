"""Wireless Test Utilities — AWGN, BER, and signal analysis tools.

Pure math implementations, no external deps beyond numpy.
Matches MATLAB Communications Toolbox behavior.

Functions:
  - awgn: Add white Gaussian noise to a signal
  - biterr: Count bit errors between two sequences
  - berawgn: Theoretical BER for uncoded modulation in AWGN
  - bcc_interleave: WLAN BCC block interleaver
  - golay_sequence: WLAN Golay complementary sequences
"""
from __future__ import annotations
from scipy.special import erfc

import json
import sys
import numpy as np


# ============================================================
# AWGN
# ============================================================
def awgn(signal: np.ndarray, snr_db: float, signal_power: str = "measured") -> np.ndarray:
    """Add white Gaussian noise to a signal.

    Args:
        signal: input signal (real or complex)
        snr_db: signal-to-noise ratio in dB
        signal_power: "measured" => compute from signal, else treat as linear power

    Returns:
        noisy signal of same shape as input

    MATLAB compatibility: matches awgn(x, snr, 'measured') from Comm Toolbox.
    """
    signal = np.asarray(signal, dtype=np.complex128 if np.iscomplexobj(signal) else np.float64)
    if signal_power == "measured":
        p_sig = np.mean(np.abs(signal) ** 2)
    else:
        p_sig = float(signal_power)
    snr_linear = 10 ** (snr_db / 10.0)
    noise_power = p_sig / snr_linear
    if np.iscomplexobj(signal):
        noise = np.sqrt(noise_power / 2) * (
            np.random.randn(*signal.shape) + 1j * np.random.randn(*signal.shape)
        )
    else:
        noise = np.sqrt(noise_power) * np.random.randn(*signal.shape)
    return (signal + noise).astype(signal.dtype)


# ============================================================
# Bit Error Rate
# ============================================================
def biterr(x: np.ndarray, y: np.ndarray) -> tuple[int, float, int]:
    """Count bit errors between two binary sequences.

    Args:
        x: reference bits
        y: received bits

    Returns:
        (num_errors, ber, total_bits) tuple

    MATLAB compatibility: matches [num, ratio] = biterr(x, y) from Comm Toolbox.
    """
    x = np.asarray(x, dtype=np.uint8).reshape(-1) % 2
    y = np.asarray(y, dtype=np.uint8).reshape(-1) % 2
    n_total = len(x)
    n_errors = int(np.sum(x != y))
    ber = n_errors / n_total if n_total > 0 else 0.0
    return n_errors, ber, n_total


# ============================================================
# Theoretical BER for AWGN
# ============================================================
def berawgn(ebn0_db: float, mod: str, n_diversity: int = 1) -> float:
    """Theoretical uncoded BER in AWGN channel.

    Args:
        ebn0_db: Eb/N0 in dB
        mod: modulation type ("bpsk", "qpsk", "16qam", "64qam", "256qam", etc.)
        n_diversity: diversity order (default 1)

    Returns:
        theoretical BER (0..0.5)

    MATLAB compatibility: matches berawgn(EbNo, modtype, M) from Comm Toolbox.
    """
    ebn0 = 10 ** (ebn0_db / 10.0)
    mod = mod.lower().replace(" ", "").replace("-", "")

    if mod in ("bpsk", "pibpsk"):
        M = 2
    elif mod == "qpsk":
        M = 4
    elif "16" in mod:
        M = 16
    elif "64" in mod:
        M = 64
    elif "256" in mod:
        M = 256
    elif "1024" in mod:
        M = 1024
    else:
        raise ValueError(f"unknown modulation: {mod}")

    k = np.log2(M)
    # M-PSK/M-QAM BER approximation
    snr_per_bit = ebn0
    if M == 2:  # BPSK
        ber = 0.5 * erfc(np.sqrt(snr_per_bit * n_diversity))
    elif M == 4:  # QPSK
        ber = 0.5 * erfc(np.sqrt(snr_per_bit * n_diversity))
    else:  # M-QAM
        ber = (4 / k) * (1 - 1 / np.sqrt(M)) * 0.5 * erfc(
            np.sqrt(3 * k * snr_per_bit * n_diversity / (M - 1))
        )
    return float(max(ber, 1e-300))


# ============================================================
# WLAN BCC Block Interleaver (IEEE 802.11)
# ============================================================
def bcc_interleave(bits: np.ndarray, ncbps: int, nbpsc: int = 1) -> np.ndarray:
    """WLAN BCC block interleaver (IEEE 802.11-2012 §20.3.11.7).

    First permutation: i_out = (NCBPS/16)(i mod 16) + floor(i/16)
    Second permutation: j_out = s*floor(i_out/s) + (i_out+NCBPS-floor(16*i_out/NCBPS)) mod s

    Args:
        bits: input bits (NCBPS bits)
        ncbps: coded bits per OFDM symbol
        nbpsc: coded bits per subcarrier (1 for BPSK, 2 for QPSK, 4 for 16QAM, 6 for 64QAM)

    Returns:
        interleaved bits
    """
    bits = np.asarray(bits, dtype=np.uint8).reshape(-1) % 2
    N = len(bits)
    s = max(1, int(nbpsc / 2))

    # First permutation
    first = np.zeros(N, dtype=int)
    for i in range(N):
        first[i] = (ncbps // 16) * (i % 16) + (i // 16)

    # Second permutation
    second = np.zeros(N, dtype=int)
    for i in range(N):
        j = first[i]
        second[i] = s * (j // s) + (j + ncbps - (16 * j // ncbps)) % s

    return bits[second]


# ============================================================
# WLAN Golay Complementary Sequences (IEEE 802.11ad/ay)
# ============================================================
def golay_sequence(length: int = 32) -> np.ndarray:
    """Generate Golay complementary sequences (Ga32, Gb32).

    IEEE 802.11ad/ay §21.3.6.2. Uses the recursive construction:
    a_0 = [1], b_0 = [1]
    a_k = [a_{k-1}, b_{k-1}]
    b_k = [a_{k-1}, -b_{k-1}]

    Args:
        length: sequence length (must be a power of 2, default 32)

    Returns:
        (Ga, Gb) tuple of arrays

    MATLAB compatibility: matches wlanGolaySequence(N) from WLAN Toolbox.
    """
    if length & (length - 1) != 0:
        raise ValueError(f"length must be a power of 2, got {length}")
    a = np.array([1], dtype=np.int8)
    b = np.array([1], dtype=np.int8)
    while len(a) < length:
        a_new = np.concatenate([a, b])
        b_new = np.concatenate([a, -b])
        a, b = a_new, b_new
    return a, b


def _parse_signal(text: str) -> np.ndarray:
    """Parse a signal string — JSON array first, fall back to comma-split."""
    text = text.strip()
    try:
        vals = json.loads(text)
        return np.array([complex(v) if isinstance(v, str) and 'j' in v else float(v)
                         for v in vals])
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    # Fallback: comma-separated, strip brackets if present
    if text.startswith('[') and text.endswith(']'):
        text = text[1:-1]
    return np.array([complex(v) if "j" in v else float(v)
                     for v in text.split(",") if v.strip()])


def _parse_bits(text: str) -> np.ndarray:
    """Parse a bits string — JSON array first, fall back to comma-split."""
    text = text.strip()
    try:
        vals = json.loads(text)
        return np.array([int(b) for b in vals], dtype=np.uint8)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    if text.startswith('[') and text.endswith(']'):
        text = text[1:-1]
    return np.array([int(b) for b in text.split(",") if b.strip()], dtype=np.uint8)


# ============================================================
# CLI
# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser("Wireless test utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_awgn = sub.add_parser("awgn")
    p_awgn.add_argument("--signal", required=True, help="comma-separated signal values")
    p_awgn.add_argument("--snr", type=float, required=True, help="SNR in dB")

    p_ber = sub.add_parser("biterr")
    p_ber.add_argument("--x", required=True, help="comma-separated reference bits")
    p_ber.add_argument("--y", required=True, help="comma-separated received bits")

    p_theory = sub.add_parser("berawgn")
    p_theory.add_argument("--ebn0", type=float, required=True, help="Eb/N0 in dB")
    p_theory.add_argument("--mod", required=True, help="modulation: bpsk/qpsk/16qam/64qam/256qam/1024qam")

    p_bcci = sub.add_parser("bcc-interleave")
    p_bcci.add_argument("--bits", required=True, help="comma-separated bits")
    p_bcci.add_argument("--ncbps", type=int, required=True, help="coded bits per symbol")
    p_bcci.add_argument("--nbpsc", type=int, default=1, help="coded bits per subcarrier")

    p_golay = sub.add_parser("golay")
    p_golay.add_argument("--length", type=int, default=32, help="sequence length (power of 2)")

    args = parser.parse_args()

    if args.cmd == "awgn":
        sig = _parse_signal(args.signal)
        noisy = awgn(sig, args.snr)
        result = {"noisy_signal_real": noisy.real.tolist(),
                   "noisy_signal_imag": noisy.imag.tolist() if np.iscomplexobj(noisy) else None}
    elif args.cmd == "biterr":
        x = _parse_bits(args.x)
        y = _parse_bits(args.y)
        n_err, ber, n_total = biterr(x, y)
        result = {"num_errors": n_err, "ber": ber, "total_bits": n_total}
    elif args.cmd == "berawgn":
        ber = berawgn(args.ebn0, args.mod)
        result = {"ebn0_db": args.ebn0, "mod": args.mod, "ber": ber}
    elif args.cmd == "bcc-interleave":
        bits = _parse_bits(args.bits)
        interleaved = bcc_interleave(bits, args.ncbps, args.nbpsc)
        result = {"interleaved_bits": interleaved.tolist()}
    elif args.cmd == "golay":
        Ga, Gb = golay_sequence(args.length)
        result = {"Ga": Ga.tolist(), "Gb": Gb.tolist()}
    else:
        result = {"error": f"unknown command {args.cmd}"}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
