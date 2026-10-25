"""MATLAB-free signal conditioning, antenna and OFDM configuration slices."""
from __future__ import annotations

from fractions import Fraction

import numpy as np

from _nr_remaining_common import complex_array, run_cli


def _positive_int(value, name):
    if isinstance(value, bool) or int(value) != value or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def arrayConfig(size=(1, 1), element_spacing=0.5):
    dims = np.asarray(size, int).reshape(-1)
    if len(dims) != 2 or np.any(dims < 1):
        raise ValueError("size must contain two positive dimensions")
    spacing = np.asarray(element_spacing, float).reshape(-1)
    if len(spacing) == 1:
        spacing = np.repeat(spacing, 2)
    if len(spacing) != 2 or np.any(spacing <= 0) or np.any(~np.isfinite(spacing)):
        raise ValueError("element_spacing must contain one or two positive finite values")
    positions = [[0.0, float(row * spacing[0]), float(col * spacing[1])]
                 for col in range(dims[1]) for row in range(dims[0])]
    return {"size": dims.tolist(), "element_spacing": spacing.tolist(),
            "element_positions": positions}


def ofdmPilotConfig(indices, values=1):
    positions = np.asarray(indices, int)
    if positions.ndim != 2 or positions.shape[1] != 2 or len(positions) == 0 or np.any(positions < 0):
        raise ValueError("indices must be nonempty zero-based [subcarrier,symbol] pairs")
    if len(np.unique(positions, axis=0)) != len(positions):
        raise ValueError("pilot indices must be unique")
    vals = complex_array(values).reshape(-1)
    if len(vals) == 1:
        vals = np.repeat(vals, len(positions))
    if len(vals) != len(positions) or np.any(~np.isfinite(vals)):
        raise ValueError("values must be one finite pilot or one per index")
    return {"indices": positions.tolist(), "values": vals}


def ofdmPilotGrid(num_subcarriers: int, num_symbols: int, indices, values=1):
    nsc, nsym = _positive_int(num_subcarriers, "num_subcarriers"), _positive_int(num_symbols, "num_symbols")
    config = ofdmPilotConfig(indices, values)
    positions = np.asarray(config["indices"], int)
    if np.any(positions[:, 0] >= nsc) or np.any(positions[:, 1] >= nsym):
        raise ValueError("pilot index outside grid")
    grid = np.zeros((nsc, nsym), complex)
    grid[positions[:, 0], positions[:, 1]] = config["values"]
    return {"grid": grid, "indices": config["indices"]}


def ofdmPrecode(x, p):
    data, precoder = complex_array(x), complex_array(p)
    if data.ndim != 3 or precoder.ndim not in (2, 3) or not data.size or not precoder.size:
        raise ValueError("x must be [subcarrier,symbol,stream], p [stream,antenna] or [stream,antenna,subcarrier]")
    if precoder.shape[0] != data.shape[2] or (precoder.ndim == 3 and precoder.shape[2] not in (1, data.shape[0])):
        raise ValueError("precoder dimensions do not match data")
    if np.any(~np.isfinite(data)) or np.any(~np.isfinite(precoder)):
        raise ValueError("data and precoder must be finite")
    if precoder.ndim == 2:
        result = np.einsum("cst,ta->csa", data, precoder)
    else:
        if precoder.shape[2] == 1:
            precoder = np.repeat(precoder, data.shape[0], axis=2)
        result = np.einsum("cst,tac->csa", data, precoder)
    return {"symbols": result}


def iqimbal(x, amplitude_db: float, phase_deg: float = 0):
    samples = complex_array(x)
    amp, phase = np.asarray(amplitude_db, float), np.asarray(phase_deg, float)
    if not samples.size or np.any(~np.isfinite(samples)) or np.any(~np.isfinite(amp)) or np.any(~np.isfinite(phase)):
        raise ValueError("finite nonempty samples, amplitude and phase required")
    a = np.deg2rad(phase) / 2
    i_gain = 10 ** (amp / 40) * np.exp(-1j * a)
    q_gain = 10 ** (-amp / 40) * 1j * np.exp(1j * a)
    return {"samples": samples.real * i_gain + samples.imag * q_gain}


def iqimbal2coef(amplitude_db: float, phase_deg: float):
    amp, phase = np.broadcast_arrays(np.asarray(amplitude_db, float), np.asarray(phase_deg, float))
    result = []
    for a, p in zip(amp.flat, phase.flat):
        theta = np.deg2rad(p) / 2
        k = np.array([[10 ** (a / 40) * np.cos(theta), -10 ** (-a / 40) * np.sin(theta)],
                      [-10 ** (a / 40) * np.sin(theta), 10 ** (-a / 40) * np.cos(theta)]])
        if abs(np.linalg.det(k)) < 1e-12:
            raise ValueError("singular I/Q imbalance")
        r = np.linalg.inv(k)
        w1 = ((r[0, 0] + r[1, 1]) + 1j * (r[1, 0] - r[0, 1])) / 2
        w2 = ((r[0, 0] - r[1, 1]) + 1j * (r[1, 0] + r[0, 1])) / 2
        result.append(w2 / w1)
    return {"coefficient": np.asarray(result).reshape(amp.shape)}


def iqcoef2imbal(coefficient):
    coeff = complex_array(coefficient)
    if np.any(~np.isfinite(coeff)) or np.any(abs(coeff) >= 1):
        raise ValueError("finite compensator coefficient with magnitude less than one required")
    # Invert the forward mapping numerically, preserving the exact MATLAB coefficient convention.
    from scipy.optimize import least_squares
    amplitudes, phases = [], []
    for c in coeff.flat:
        def residual(v):
            z = iqimbal2coef(v[0], v[1])["coefficient"].item() - c
            return [z.real, z.imag]
        fit = least_squares(residual, [0.0, 0.0], bounds=([-100, -89.9], [100, 89.9]), xtol=1e-12,
                            ftol=1e-12, gtol=1e-12)
        if np.linalg.norm(fit.fun) > 1e-8:
            raise ValueError("coefficient has no supported amplitude/phase solution")
        amplitudes.append(fit.x[0])
        phases.append(fit.x[1])
    return {"amplitude_db": np.asarray(amplitudes).reshape(coeff.shape),
            "phase_deg": np.asarray(phases).reshape(coeff.shape)}


def srmdelay(input_rates, input_lengths, output_rate, output_length, mode="multitasking"):
    rates, lengths = np.asarray(input_rates, float), np.asarray(input_lengths, int)
    if rates.shape != (2,) or lengths.shape != (2,) or np.any(rates <= 0) or np.any(lengths < 1):
        raise ValueError("two positive input rates and lengths required")
    if output_rate < max(rates) or _positive_int(output_length, "output_length") < 1:
        raise ValueError("output rate must be at least both input rates")
    if mode not in ("singletasking", "multitasking"):
        raise ValueError("mode must be singletasking or multitasking")
    ratios = [Fraction(float(output_rate / rate)).limit_denominator(100000) for rate in rates]
    # Buffer latency is exact for integral frame ratios; filter group delay depends on designMultirateFIR.
    return {"rate_factors": [[r.numerator, r.denominator] for r in ratios],
            "buffer_delay_samples": [int(np.ceil(length / output_length) * output_length - length)
                                     for length in lengths], "mode": mode,
            "filter_delay_samples": None}


def dpdPreprocessor(x, memory_depth: int = 1, degree=1, state=None):
    samples = complex_array(x).reshape(-1)
    m = _positive_int(memory_depth, "memory_depth")
    powers = np.asarray(degree, int).reshape(-1)
    if not len(samples) or not len(powers) or np.any(powers < 1) or np.any(~np.isfinite(samples)):
        raise ValueError("nonempty finite samples and positive degree required")
    previous = np.zeros(m - 1, complex) if state is None else complex_array(state).reshape(-1)
    if len(previous) != m - 1:
        raise ValueError("state must contain memory_depth-1 prior samples")
    padded = np.concatenate([previous, samples])
    delayed = np.stack([padded[i:i + len(samples)] for i in range(m)], axis=1)
    features = np.concatenate([delayed.real, delayed.imag] +
                              [abs(delayed) ** int(power) for power in powers if power > 1], axis=1)
    return {"features": features, "state": padded[-(m - 1):] if m > 1 else np.array([], complex)}


if __name__ == "__main__":
    run_cli("MATLAB-free signal configuration and conditioning slices", {
        "arrayConfig": arrayConfig, "ofdmPilotConfig": ofdmPilotConfig,
        "ofdmPilotGrid": ofdmPilotGrid, "ofdmPrecode": ofdmPrecode,
        "iqimbal": iqimbal, "iqimbal2coef": iqimbal2coef,
        "iqcoef2imbal": iqcoef2imbal, "srmdelay": srmdelay,
        "dpdPreprocessor": dpdPreprocessor,
    })
