"""Standalone Communications Toolbox numeric and source utility slices."""
from __future__ import annotations

import numpy as np
from scipy.signal import lfilter
from scipy.stats import beta

from _nr_remaining_common import complex_array, run_cli


def _order(bit_order: str) -> bool:
    if bit_order.lower() not in ("right-msb", "left-msb"):
        raise ValueError("bit_order must be right-msb or left-msb")
    return bit_order.lower() == "right-msb"


def bi2de(bits, bit_order: str = "right-msb"):
    values = np.asarray(bits)
    if values.ndim == 1:
        values = values[None, :]
    if values.ndim != 2 or not values.size or np.any((values != 0) & (values != 1)):
        raise ValueError("bits must be a nonempty binary row or matrix")
    width = values.shape[1]
    if width > 63:
        raise ValueError("this numeric slice supports at most 63 bits per row")
    shifts = np.arange(width) if _order(bit_order) else np.arange(width - 1, -1, -1)
    return {"values": np.sum(values.astype(np.int64) * (1 << shifts), axis=1)}


def de2bi(values, width: int | None = None, bit_order: str = "right-msb"):
    numbers = np.asarray(values)
    if numbers.ndim > 2 or not numbers.size or np.any(numbers < 0) or np.any(numbers != np.floor(numbers)):
        raise ValueError("values must be nonnegative integers")
    numbers = numbers.astype(np.int64).reshape(-1)
    if width is None:
        width = max(1, int(max(numbers)).bit_length())
    if not isinstance(width, int) or not 1 <= width <= 63 or np.any(numbers >= 1 << width):
        raise ValueError("width must fit all values and be 1..63")
    shifts = np.arange(width) if _order(bit_order) else np.arange(width - 1, -1, -1)
    return {"bits": ((numbers[:, None] >> shifts) & 1).astype(int)}


def _poly_digits(value, base: int, order: str):
    if order not in ("ascending", "descending"):
        raise ValueError("order must be ascending or descending")
    s = str(value).strip().lower()
    if base == 16 and s.startswith("0x"):
        s = s[2:]
    if base == 8 and s.startswith("0o"):
        s = s[2:]
    if not s:
        raise ValueError("polynomial digits must be nonempty")
    number = int(s, base)
    bits = [int(c) for c in bin(number)[2:]]
    return {"coefficients": bits[::-1] if order == "ascending" else bits}


def hex2poly(value, order: str = "descending"):
    return _poly_digits(value, 16, order)


def oct2poly(value, order: str = "descending"):
    return _poly_digits(value, 8, order)


def noisebw(num, den, num_samp: int = 1024, fs: float = 1.0):
    b, a = np.asarray(num, float).reshape(-1), np.asarray(den, float).reshape(-1)
    if not len(b) or not len(a) or a[0] == 0 or num_samp < 1 or fs <= 0:
        raise ValueError("valid filter coefficients, num_samp and fs required")
    impulse = np.zeros(num_samp)
    impulse[0] = 1
    h = lfilter(b, a, impulse)
    gain = float(np.sum(h))
    if abs(gain) < 1e-15:
        raise ValueError("filter DC gain must be nonzero")
    return {"bandwidth_hz": float(fs * np.sum(h * h) / gain**2)}


def modnorm(constellation, pow_type: str = "avpow", power: float = 1.0):
    c = complex_array(constellation).reshape(-1)
    if not len(c) or power <= 0 or not np.isfinite(power):
        raise ValueError("nonempty constellation and positive power required")
    powers = abs(c)**2
    if pow_type.lower() == "avpow":
        reference = float(np.mean(powers))
    elif pow_type.lower() == "peakpow":
        reference = float(np.max(powers))
    else:
        raise ValueError("pow_type must be avpow or peakpow")
    if reference <= 0:
        raise ValueError("constellation power must be positive")
    return {"scale": float(np.sqrt(power / reference))}


def vec2mat(vector, columns: int, padding=0):
    v = np.asarray(vector).reshape(-1)
    if columns < 1:
        raise ValueError("columns must be positive")
    missing = (-len(v)) % columns
    out = np.concatenate((v, np.repeat(padding, missing))).reshape(-1, columns)
    return {"matrix": out, "padded": missing}


def randerr(rows: int, columns: int | None = None, errors: int = 1, seed: int = 0):
    if columns is None:
        columns = rows
    if rows < 1 or columns < 1 or errors < 0 or errors > columns:
        raise ValueError("rows/columns must be positive and errors within each row")
    rng = np.random.default_rng(seed)
    out = np.zeros((rows, columns), dtype=int)
    for row in out:
        row[rng.choice(columns, errors, replace=False)] = 1
    return {"pattern": out}


def randsrc(rows: int = 1, columns: int = 1, alphabet=(-1, 1),
            probabilities=None, seed: int = 0):
    if rows < 1 or columns < 1 or not len(alphabet):
        raise ValueError("positive shape and nonempty alphabet required")
    p = None if probabilities is None else np.asarray(probabilities, float)
    if p is not None and (len(p) != len(alphabet) or np.any(p < 0) or
                          not np.isclose(np.sum(p), 1)):
        raise ValueError("probabilities must be nonnegative and sum to 1")
    return {"values": np.random.default_rng(seed).choice(alphabet, (rows, columns), p=p)}


def compand(samples, param: float = 255, peak: float = 1.0, method: str = "mu/compressor"):
    x = np.asarray(samples, float)
    method = method.lower()
    if peak <= 0 or param <= 1 or np.any(~np.isfinite(x)):
        raise ValueError("finite samples, peak > 0 and param > 1 required")
    normalized = abs(x) / peak
    if method == "mu/compressor":
        y = np.log1p(param * normalized) / np.log1p(param)
    elif method == "mu/expander":
        y = np.expm1(np.log1p(param) * normalized) / param
    elif method == "a/compressor":
        y = np.where(normalized < 1 / param, param * normalized,
                     1 + np.log(np.maximum(param * normalized, 1e-300))) / (1 + np.log(param))
    elif method == "a/expander":
        pivot = 1 / (1 + np.log(param))
        y = np.where(normalized < pivot, normalized * (1 + np.log(param)) / param,
                     np.exp(normalized * (1 + np.log(param)) - 1) / param)
    else:
        raise ValueError("unsupported companding method")
    return {"samples": np.sign(x) * peak * y}


def quantiz(samples, partition, codebook=None):
    x, p = np.asarray(samples, float), np.asarray(partition, float).reshape(-1)
    if np.any(~np.isfinite(x)) or np.any(~np.isfinite(p)) or np.any(np.diff(p) <= 0):
        raise ValueError("finite samples and strictly increasing partition required")
    indices = np.searchsorted(p, x, side="left")
    result = {"indices": indices}
    if codebook is not None:
        c = np.asarray(codebook, float).reshape(-1)
        if len(c) != len(p) + 1:
            raise ValueError("codebook must have len(partition)+1 entries")
        quantized = c[indices]
        result.update(values=quantized, distortion=float(np.mean((x - quantized)**2)))
    return result


def berconfint(errors: int, trials: int, level: float = 0.95):
    if type(errors) is not int or type(trials) is not int or not 0 <= errors <= trials or trials < 1 or not 0 < level < 1:
        raise ValueError("0 <= errors <= trials and 0 < level < 1 required")
    alpha = (1 - level) / 2
    lo = 0.0 if errors == 0 else float(beta.ppf(alpha, errors, trials - errors + 1))
    hi = 1.0 if errors == trials else float(beta.ppf(1 - alpha, errors + 1, trials - errors))
    return {"ber": errors / trials, "interval": [lo, hi]}


if __name__ == "__main__":
    run_cli("Standalone legacy Communications numeric and source utility slices", {
        "bi2de": bi2de, "de2bi": de2bi, "hex2poly": hex2poly, "oct2poly": oct2poly,
        "noisebw": noisebw, "modnorm": modnorm, "vec2mat": vec2mat,
        "randerr": randerr, "randsrc": randsrc, "compand": compand,
        "quantiz": quantiz, "berconfint": berconfint,
    })
