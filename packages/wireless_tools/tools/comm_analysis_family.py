"""Headless BER and waveform-analysis entry points for agents."""
from __future__ import annotations

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator
from scipy.special import erfc

from _nr_remaining_common import complex_array, run_cli


def berfit(ebno_db, ber, fit_ebno_db=None):
    x, y = np.asarray(ebno_db, float).reshape(-1), np.asarray(ber, float).reshape(-1)
    if len(x) < 2 or len(x) != len(y) or np.any(~np.isfinite(x)) or np.any(np.diff(x) <= 0):
        raise ValueError("at least two strictly increasing finite Eb/No points required")
    if np.any(~np.isfinite(y)) or np.any((y < 0) | (y > .5)):
        raise ValueError("BER must be between zero and 0.5")
    target = x if fit_ebno_db is None else np.asarray(fit_ebno_db, float).reshape(-1)
    if not len(target) or np.any(~np.isfinite(target)):
        raise ValueError("fit_ebno_db must be finite and nonempty")
    # A monotone log-BER curve avoids unphysical increases between noisy empirical samples.
    floor = min((v for v in y if v > 0), default=1e-12) / 10
    monotone = np.minimum.accumulate(np.maximum(y, floor))
    fitted = np.exp(PchipInterpolator(x, np.log(monotone), extrapolate=True)(target))
    return {"ebno_db": target, "ber": np.clip(fitted, 0, .5)}


def bersync(ebno_db, sigma: float, error_type="carrier"):
    ebno = np.asarray(ebno_db, float)
    if sigma < 0 or not np.isfinite(sigma) or np.any(~np.isfinite(ebno)):
        raise ValueError("finite Eb/No and nonnegative finite sigma required")
    mode = error_type.lower()
    if mode not in ("carrier", "timing") or (mode == "timing" and sigma > .5):
        raise ValueError("error_type must be carrier or timing; timing sigma <= 0.5")
    result = []
    for db in ebno.flat:
        g = 10 ** (db / 10)
        if sigma == 0:
            value = .5 * erfc(np.sqrt(g))
        elif mode == "carrier":
            value = quad(lambda p: .5 * erfc(np.sqrt(g) * np.cos(p)) *
                         np.exp(-p*p/(2*sigma*sigma)) / (np.sqrt(2*np.pi)*sigma),
                         -10*sigma, 10*sigma, epsabs=1e-9)[0]
        else:
            value = quad(lambda t: .5 * erfc(np.sqrt(g) * (1 - 2*abs(t))) *
                         np.exp(-t*t/(2*sigma*sigma)) / (np.sqrt(2*np.pi)*sigma),
                         -10*sigma, 10*sigma, epsabs=1e-9)[0]
        result.append(float(np.clip(value, 0, .5)))
    return {"ber": np.asarray(result).reshape(ebno.shape)}


def scatterplot(x, n: int = 1, offset: int = 0):
    samples = complex_array(x).reshape(-1)
    if int(n) != n or n < 1 or int(offset) != offset or offset < 0 or offset >= len(samples):
        raise ValueError("positive decimation and valid nonnegative offset required")
    sampled = samples[offset::n]
    return {"i": sampled.real, "q": sampled.imag, "sample_indices": np.arange(offset, len(samples), n)}


def eyediagram(x, n: int, period: float = 1, offset: int = 0):
    samples = complex_array(x).reshape(-1)
    if int(n) != n or n < 2 or period <= 0 or int(offset) != offset or not 0 <= offset < n:
        raise ValueError("n >= 2, positive period and offset in [0,n) required")
    traces = []
    for center in range(offset, len(samples), n):
        start = center - n // 2
        if start >= 0 and start + n <= len(samples):
            traces.append(samples[start:start+n])
    waveforms = np.asarray(traces, complex).reshape(-1, n)
    return {"time": (np.arange(n) - n/2) * period/n,
            "in_phase": waveforms.real, "quadrature": waveforms.imag,
            "trace_count": len(waveforms)}


def semianalytic(tx_sig, rx_sig, mod_type: str, m: int, nsamp: int,
                 ebno_db, trials: int = 20000, seed: int = 0):
    tx, rx = complex_array(tx_sig).reshape(-1), complex_array(rx_sig).reshape(-1)
    if len(tx) != len(rx) or not len(tx) or np.any(~np.isfinite(tx)) or np.any(~np.isfinite(rx)):
        raise ValueError("equal-length finite transmit and noiseless receive vectors required")
    if mod_type.lower() not in ("psk/nondiff", "qam") or m < 2 or m & (m-1) or nsamp != 1:
        raise ValueError("supported slice: power-of-two PSK/QAM and nsamp=1")
    if trials < 1:
        raise ValueError("trials must be positive")
    constellation = np.unique(tx)
    if len(constellation) != m:
        raise ValueError("tx_sig must contain all m constellation points")
    labels = np.argmin(abs(tx[:, None] - constellation[None, :]), axis=1)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(tx), size=trials)
    bits_per_symbol = int(np.log2(m))
    power = np.mean(abs(tx)**2)
    results = []
    for db in np.asarray(ebno_db, float).reshape(-1):
        n0 = power / (bits_per_symbol * 10**(db/10))
        noise = np.sqrt(n0/2) * (rng.normal(size=trials) + 1j*rng.normal(size=trials))
        received = rx[indices] + noise
        decisions = np.argmin(abs(received[:, None] - constellation[None, :]), axis=1)
        errors = sum(int(a ^ b).bit_count() for a, b in zip(labels[indices], decisions))
        results.append(errors / (trials * bits_per_symbol))
    return {"ebno_db": np.asarray(ebno_db, float), "ber": results,
            "trials": trials, "seed": seed}


if __name__ == "__main__":
    run_cli("Headless BER and waveform analysis", {
        "berfit": berfit, "bersync": bersync, "scatterplot": scatterplot,
        "eyediagram": eyediagram, "semianalytic": semianalytic,
    })
