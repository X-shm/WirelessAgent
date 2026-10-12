"""Generate Bluetooth LE Channel Sounding step-mode 0..3 waveforms."""
from __future__ import annotations

import secrets
import numpy as np

from _bluetooth_algorithms import ble_gmsk_modulate, ble_preamble
from _bluetooth_common import InputError, array_result, bit_vector, run_cli
from ble_network_config import configuration


def _random_address(role: str) -> np.ndarray:
    candidates = np.asarray([secrets.randbits(1) for _ in range(128)], dtype=np.uint8).reshape((4, 32))
    scores = []
    for item in candidates:
        counts = [int(np.count_nonzero(item[:-lag] != item[lag:])) for lag in (1, 2, 3)]
        scores.append(sum(abs(2 * count - (32 - lag)) for lag, count in zip((1, 2, 3), counts)))
    low = 0 if role == "Initiator" else 2
    selected = low + (1 if scores[low] >= scores[low + 1] else 0)
    return candidates[selected][::-1].copy()


def _optional_sequence(kind: str, length: int) -> np.ndarray:
    if kind == "Random Sequence":
        return np.asarray([secrets.randbits(1) for _ in range(length)], dtype=np.uint8)
    sequence = np.tile(np.asarray([1, 0], dtype=np.uint8), length // 2)
    if length == 32:
        positions = [secrets.randbelow(29)]
    else:
        positions = [secrets.randbelow(64)]
        second = secrets.randbelow(75) + 67
        if second <= 92:
            positions.append(second)
    for position in positions:
        sequence[position:position + 4] = [0, 0, 1, 1] if secrets.randbits(1) else [1, 1, 0, 0]
    return sequence[::-1].copy()


def _sync_bits(mode: str, address: np.ndarray) -> np.ndarray:
    preamble = ble_preamble("LE1M" if mode == "LE1M" else "LE2M", address)
    trailer = np.asarray([1, 0, 1, 0] if address[-1] == 0 else [0, 1, 0, 1], dtype=np.uint8)
    return np.concatenate((preamble, address, trailer))


def _tone(cfg: dict) -> tuple[np.ndarray, np.ndarray]:
    factor = 1 if cfg["mode"] == "LE1M" else 2
    sample_rate = cfg["samples_per_symbol"] * 1_000_000 * factor
    tone_samples = cfg["tone_duration"] * cfg["samples_per_symbol"] * factor
    if cfg["output_data_type"] == "single":
        t = np.arange(tone_samples, dtype=np.float32) / np.float32(sample_rate)
    else:
        t = np.arange(tone_samples, dtype=float) / sample_rate
    tone = np.cos(2 * np.pi * (1_000_000 * factor / 2) * t).astype(complex)
    guard = np.zeros(10 * cfg["samples_per_symbol"] * factor, dtype=complex)
    return tone, guard


def generate(properties: dict | None = None, *, access_address=None,
             optional_sequence=None, tone_extension_bit=None) -> tuple[np.ndarray, dict]:
    cfg = configuration("bleCSConfig", properties)
    step, role = cfg["step_mode"], cfg["device_role"]
    if step == 0 and role == "Reflector" and cfg["tone_duration"] != 80:
        raise InputError("step_mode 0 reflector requires tone_duration=80")
    if step in (2, 3) and cfg["tone_duration"] == 80:
        raise InputError("step_mode 2 or 3 requires tone_duration=10, 20, or 40")
    if access_address is not None and step == 2:
        raise InputError("step_mode 2 has no access_address")
    if optional_sequence is not None and step not in (1, 3):
        raise InputError("optional_sequence applies only to step_mode 1 or 3")
    if tone_extension_bit is not None and step not in (2, 3):
        raise InputError("tone_extension_bit applies only to step_mode 2 or 3")
    address = (bit_vector(access_address, "access_address") if access_address is not None
               else _random_address(role)) if step != 2 else np.empty(0, dtype=np.uint8)
    if address.size not in (0, 32):
        raise InputError("access_address must contain 32 bits")
    optional = (bit_vector(optional_sequence, "optional_sequence") if optional_sequence is not None
                else _optional_sequence(cfg["sequence_type"], cfg["sequence_length"])) if step in (1, 3) else np.empty(0, dtype=np.uint8)
    if step in (1, 3) and optional.size != cfg["sequence_length"]:
        raise InputError("optional_sequence length must equal sequence_length")
    if tone_extension_bit is None:
        tone_extension_bit = secrets.randbits(1)
    if tone_extension_bit not in (0, 1):
        raise InputError("tone_extension_bit must be 0 or 1")
    factor = 1 if cfg["mode"] == "LE1M" else 2
    bt = 2.0 if cfg["mode"] == "LE2M 2BT" else 0.5
    sync_bits = _sync_bits(cfg["mode"], address) if step != 2 else np.empty(0, dtype=np.uint8)
    sync_wave = (ble_gmsk_modulate(np.concatenate((sync_bits, optional)),
                                   cfg["samples_per_symbol"], cfg["modulation_index"],
                                   cfg["pulse_length"], bt)
                 if step != 2 else np.empty(0, dtype=complex))
    if step == 0 and role == "Initiator" or step == 1:
        waveform = sync_wave
    else:
        tone, guard = _tone(cfg)
        extension = tone if tone_extension_bit else np.zeros_like(tone)
        if step == 0:
            waveform = np.concatenate((sync_wave, guard, tone))
        elif step == 2:
            waveform = np.concatenate((tone, extension))
        elif role == "Initiator":
            waveform = np.concatenate((sync_wave, guard, tone, extension))
        elif tone_extension_bit:
            waveform = np.concatenate((tone, extension, guard, sync_wave))
        else:
            waveform = np.concatenate((tone, guard, sync_wave, extension))
    if cfg["output_data_type"] == "single":
        waveform = waveform.astype(np.complex64)
    return waveform, {"access_address": address.tolist(),
                      "optional_sequence": optional.tolist(),
                      "tone_extension_bit": tone_extension_bit if step in (2, 3) else None,
                      "samples": int(waveform.size)}


def _handler(args, request):
    waveform, detail = generate(request.get("properties"),
                                access_address=request.get("access_address"),
                                optional_sequence=request.get("optional_sequence"),
                                tone_extension_bit=request.get("tone_extension_bit"))
    result, artifacts = array_result("waveform", waveform, args)
    result.update(detail)
    return {"result": result, "artifacts": artifacts}


if __name__ == "__main__":
    run_cli("ble_cs_waveform", _handler, artifacts=True, description=__doc__)
