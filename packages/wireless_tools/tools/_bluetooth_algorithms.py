"""Bluetooth LE primitives shared by the initial PHY and stateful tools."""
from __future__ import annotations

import math
import numpy as np

from _bluetooth_common import InputError


BLE_SYMBOL_RATES = {"LE1M": 1_000_000, "LE2M": 2_000_000, "LE500K": 1_000_000, "LE125K": 1_000_000}


def whiten(bits: np.ndarray, channel_index: int, state: list[int] | None = None) -> tuple[np.ndarray, list[int]]:
    """BLE data whitening, x^7+x^4+1, with the Core-spec channel seed."""
    if not 0 <= channel_index <= 39:
        raise InputError("channel_index must be in 0..39")
    register = list(state) if state is not None else [1] + [(channel_index >> bit) & 1 for bit in range(5, -1, -1)]
    if len(register) != 7 or any(bit not in (0, 1) for bit in register):
        raise InputError("whitening state must contain seven bits")
    out = np.empty(len(bits), dtype=np.uint8)
    for index, bit in enumerate(bits):
        # MATLAB bluetoothWhiten exposes the last register element, shifts
        # with circshift(...,1), then writes old(4) xor old(7) into slot 5.
        # Keeping that ordering is important because BLE channel seeds are
        # expressed MSB first.
        old = register
        out[index] = int(bit) ^ old[6]
        register = [old[6], old[0], old[1], old[2], old[3] ^ old[6], old[4], old[5]]
    return out, register


def gaussian_filter(samples_per_symbol: int, modulation_index: float, pulse_length: int) -> np.ndarray:
    if samples_per_symbol < 1 or int(samples_per_symbol) != samples_per_symbol:
        raise InputError("samples_per_symbol must be a positive integer")
    if not 0.45 <= modulation_index <= 0.55:
        raise InputError("modulation_index must be in 0.45..0.55")
    if pulse_length not in (1, 2, 3, 4):
        raise InputError("pulse_length must be in 1..4")
    # Bluetooth specifies BT=0.5.  A normalized truncated Gaussian impulse
    # response is sufficient for the continuous-phase GFSK reference model.
    count = pulse_length * samples_per_symbol
    points = (np.arange(count, dtype=float) - (count - 1) / 2) / samples_per_symbol
    alpha = math.sqrt(math.pi / math.log(2.0)) * 0.5
    impulse = np.exp(-2.0 * math.pi * math.pi * alpha * alpha * points * points)
    return impulse / impulse.sum()


def ble_preamble(mode: str, access_address: np.ndarray) -> np.ndarray:
    if mode == "LE1M":
        pattern = np.asarray([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
    elif mode == "LE2M":
        pattern = np.asarray([0, 1] * 8, dtype=np.uint8)
    elif mode in {"LE125K", "LE500K"}:
        return np.tile(np.asarray([0, 0, 1, 1, 1, 1, 0, 0], dtype=np.uint8), 10)
    else:
        raise InputError("mode must be LE1M, LE2M, LE500K, or LE125K")
    return pattern ^ int(access_address[0])


def ble_coded_phy_encode(payload: np.ndarray, access_address: np.ndarray, mode: str) -> np.ndarray:
    """LE Coded PHY FEC (K=4, octal 17/13) and S=8/S=2 pattern mapping."""
    if mode not in {"LE125K", "LE500K"}:
        raise InputError("coded PHY mode must be LE125K or LE500K")
    indicator = np.asarray([0, 0] if mode == "LE125K" else [1, 0], dtype=np.uint8)
    term = np.zeros(3, dtype=np.uint8)
    information = np.concatenate((access_address, indicator, term, payload, term))
    encoded = np.empty(information.size * 2, dtype=np.uint8)
    history = 0
    for index, bit in enumerate(information):
        register = (int(bit) << 3) | history
        encoded[2 * index] = (register & 0b1111).bit_count() & 1
        encoded[2 * index + 1] = (register & 0b1011).bit_count() & 1
        history = ((int(bit) << 2) | (history >> 1)) & 0b111
    mapped = np.stack((encoded, encoded, 1 - encoded, 1 - encoded), axis=1).reshape(-1)
    return mapped if mode == "LE125K" else np.concatenate((mapped[:37 * 2 * 4], encoded[37 * 2:]))


def ble_coded_phy_decode(coded_symbols: np.ndarray, mode: str) -> tuple[np.ndarray, np.ndarray]:
    """Hard-decision Viterbi decode of a complete LE Coded PHY payload."""
    if mode not in {"LE125K", "LE500K"}:
        raise InputError("coded PHY mode must be LE125K or LE500K")
    symbols = np.asarray(coded_symbols, dtype=np.uint8).reshape(-1)
    prefix = 37 * 2 * 4
    if mode == "LE125K":
        if symbols.size <= prefix or symbols.size % 8:
            raise InputError("LE125K payload must contain complete S=8 codewords")
        groups = symbols.reshape(-1, 4)
        coded = (groups[:, :2].sum(axis=1) >= 2).astype(np.uint8)
    else:
        if symbols.size <= prefix or (symbols.size - prefix) % 2:
            raise InputError("LE500K payload must contain complete S=2 codewords")
        groups = symbols[:prefix].reshape(-1, 4)
        first = (groups[:, :2].sum(axis=1) >= 2).astype(np.uint8)
        coded = np.concatenate((first, symbols[prefix:]))
    if coded.size % 2:
        raise InputError("coded PHY FEC stream must have an even length")
    pairs = coded.reshape(-1, 2)
    steps = pairs.shape[0]
    previous = np.full((steps, 8), -1, dtype=np.int8)
    decisions = np.zeros((steps, 8), dtype=np.uint8)
    metrics = np.full(8, 1_000_000, dtype=np.int32)
    metrics[0] = 0
    for index, pair in enumerate(pairs):
        next_metrics = np.full(8, 1_000_000, dtype=np.int32)
        for state in range(8):
            if metrics[state] >= 1_000_000:
                continue
            for bit in (0, 1):
                register = (bit << 3) | state
                expected0 = (register & 0b1111).bit_count() & 1
                expected1 = (register & 0b1011).bit_count() & 1
                next_state = ((bit << 2) | (state >> 1)) & 0b111
                cost = metrics[state] + (expected0 != int(pair[0])) + (expected1 != int(pair[1]))
                if cost < next_metrics[next_state]:
                    next_metrics[next_state] = cost
                    previous[index, next_state] = state
                    decisions[index, next_state] = bit
        metrics = next_metrics
    state = 0
    decoded = np.empty(steps, dtype=np.uint8)
    for index in range(steps - 1, -1, -1):
        decoded[index] = decisions[index, state]
        state = int(previous[index, state])
        if state < 0:
            raise InputError("coded PHY Viterbi path is invalid")
    if decoded.size < 41:
        raise InputError("coded PHY frame is too short")
    expected_ci = [0, 0] if mode == "LE125K" else [1, 0]
    if decoded[32:34].tolist() != expected_ci:
        raise InputError("coded PHY coding indicator does not match mode")
    return decoded[37:-3], decoded[:32]


def _gmsk_params(bt: float, pulse_length: int, samples_per_symbol: int) -> np.ndarray:
    """Translation of Bluetooth Toolbox's discrete Gaussian CPM pulse."""
    oversample = int(math.ceil(64 / samples_per_symbol))
    ts = 1.0 / (samples_per_symbol * oversample)
    offset = ts / 2
    time = offset + np.arange(pulse_length * samples_per_symbol * oversample) * ts
    k = 2 * math.pi * bt / math.sqrt(math.log(2))
    centered = time - pulse_length / 2
    qfunc = lambda values: 0.5 * (1 - np.vectorize(math.erf)(values / math.sqrt(2)))
    impulse = 0.5 * (qfunc(k * (centered - 0.5)) - qfunc(k * (centered + 0.5)))
    cumulative = ts * np.cumsum(impulse)
    impulse *= 0.5 / cumulative[-1]
    impulse = impulse.reshape(-1, oversample).mean(axis=1)
    impulse *= ts * oversample
    return np.concatenate(([0.0], np.cumsum(impulse[:-1])))


def ble_gmsk_modulate(bits: np.ndarray, samples_per_symbol: int, modulation_index: float, pulse_length: int,
                      bt_product: float = 0.5) -> np.ndarray:
    """Bluetooth Toolbox gmskmod-compatible sampled CPM waveform."""
    q = _gmsk_params(bt_product, pulse_length, samples_per_symbol)
    h = float(modulation_index)
    # For the one-symbol pulse used by the default BLE PHY, CPM reduces to
    # an exact per-symbol phase transition.  This form mirrors cpmMod's
    # phase-state update and avoids an off-by-one prehistory artifact.
    if pulse_length == 1:
        phase = []
        state = 0.0
        for bit in np.asarray(bits, dtype=float).reshape(-1):
            phase.extend(state + h * (2 * bit - 1) * q)
            state += 0.5 * h * (2 * bit - 1)
        return np.exp(2j * math.pi * np.asarray(phase))
    # The multi-symbol form is the same CPM sum with the Toolbox's +1
    # prehistory symbols.  Keeping the completed transitions in ``state``
    # makes the boundary convention explicit rather than relying on a
    # convolution alignment convention.
    symbols = 2 * np.asarray(bits, dtype=float).reshape(-1) - 1
    phase = np.empty(symbols.size * samples_per_symbol, dtype=float)
    # R2026a's initialized CPM prehistory shifts the reference phase for
    # even pulse spans by +/-h/4 cycles (verified at h=0.48, 0.5, 0.52).
    phase_reference = h / 4 if pulse_length == 2 else -h / 4 if pulse_length == 4 else 0.0
    for sample in range(phase.size):
        current = sample // samples_per_symbol
        value = 0.0
        for symbol in range(-(pulse_length - 1), current + 1):
            amplitude = 1.0 if symbol < 0 else symbols[symbol]
            offset = sample - symbol * samples_per_symbol
            if offset < q.size:
                value += amplitude * q[offset]
            else:
                value += amplitude * 0.5
        # cpmMod removes the phase contributed by the initialized
        # prehistory; for the BLE all-one prehistory this is h/2.
        phase[sample] = h * value - h / 2 + phase_reference
    return np.exp(2j * math.pi * phase)
    data = np.repeat(np.asarray(bits, dtype=float).reshape(-1), samples_per_symbol)
    history = np.full(samples_per_symbol * max(pulse_length - 1, 1), h)
    scaled = np.concatenate((history, h * (2 * data - 1)))
    phase = np.zeros(data.size, dtype=float)
    state = 0.0
    sample_indices = np.arange(samples_per_symbol)
    previous_phase = 0.0
    if pulse_length > 1:
        previous_phase = 2 * math.pi * np.sum((h * q[samples_per_symbol:]).reshape(samples_per_symbol, pulse_length - 1), axis=1)[0]
    for symbol in range(len(bits)):
        indices = (pulse_length * samples_per_symbol - 1 - np.arange(pulse_length * samples_per_symbol)) + symbol * samples_per_symbol
        filtered = scaled[indices] * q
        phase[symbol * samples_per_symbol + sample_indices] = state + filtered.reshape(samples_per_symbol, pulse_length).sum(axis=1)
        state += 0.5 * scaled[symbol * samples_per_symbol]
    return np.exp(1j * (2 * math.pi * phase - previous_phase))


def gfsk_modulate(bits: np.ndarray, samples_per_symbol: int = 8, modulation_index: float = 0.5,
                  pulse_length: int = 1) -> np.ndarray:
    bits = np.asarray(bits, dtype=np.uint8).reshape(-1)
    symbols = 2.0 * bits.astype(float) - 1.0
    shaped = np.convolve(np.repeat(symbols, samples_per_symbol),
                         gaussian_filter(samples_per_symbol, modulation_index, pulse_length), mode="full")
    phase = np.cumsum(shaped) * math.pi * modulation_index / samples_per_symbol
    return np.exp(1j * phase)


def gfsk_demodulate(waveform: np.ndarray, samples_per_symbol: int) -> np.ndarray:
    signal = np.asarray(waveform, dtype=complex).reshape(-1)
    if signal.size < samples_per_symbol + 1:
        raise InputError("waveform is too short for the selected samples_per_symbol")
    frequency = np.angle(signal[1:] * np.conj(signal[:-1]))
    count = frequency.size // samples_per_symbol
    return (frequency[:count * samples_per_symbol].reshape(count, samples_per_symbol).mean(axis=1) >= 0).astype(np.uint8)


def crc24_ble(bits: np.ndarray, init: int = 0x555555) -> np.ndarray:
    """Bluetooth LE CRC24 as transmitted bits (MATLAB crcGenerate direct method)."""
    crc = init & 0xFFFFFF
    for bit in np.asarray(bits, dtype=np.uint8):
        feedback = ((crc >> 23) & 1) ^ int(bit)
        crc = (crc << 1) & 0xFFFFFF
        if feedback:
            crc ^= 0x00065B
    return np.asarray([(crc >> shift) & 1 for shift in range(23, -1, -1)], dtype=np.uint8)
