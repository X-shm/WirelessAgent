"""Perform Bluetooth LE CTE reference/slot IQ sampling."""
from __future__ import annotations

import numpy as np

from _bluetooth_common import InputError, array_result, complex_from_json, run_cli


def iq_sample(samples, *, mode="LE1M", samples_per_symbol=8, slot_duration=2, sample_offset=4):
    data = np.asarray(samples, dtype=complex).reshape(-1)
    if mode not in {"LE1M", "LE2M"}:
        raise InputError("mode must be LE1M or LE2M")
    for value, name in ((samples_per_symbol, "samples_per_symbol"), (slot_duration, "slot_duration"), (sample_offset, "sample_offset")):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise InputError(f"{name} must be a positive integer")
    if slot_duration > 2:
        raise InputError("slot_duration must be 1 or 2")
    factor = 2 if mode == "LE2M" else 1
    minimum, maximum, multiple = 16 * samples_per_symbol * factor, 160 * samples_per_symbol * factor, 8 * samples_per_symbol * factor
    if not minimum <= data.size <= maximum or data.size % multiple:
        raise InputError("cte_samples length is invalid for mode and samples_per_symbol")
    if not round(samples_per_symbol * factor / 8) <= sample_offset <= round(7 * samples_per_symbol * factor / 8):
        raise InputError("sample_offset is outside the permitted CTE sampling window")
    bt = 0.5
    t = np.linspace(-1, 1, 2 * samples_per_symbol + 1)
    alpha = np.sqrt(np.log(2) / 2) / bt
    h = (np.sqrt(np.pi) / alpha) * np.exp(-(t * np.pi / alpha) ** 2)
    filtered = np.convolve(data, h / h.sum(), mode="same")
    ref_end = (4 + 8 - 1) * samples_per_symbol * factor + sample_offset
    reference_indices = np.rint(np.arange(4 * samples_per_symbol * factor + sample_offset, ref_end + 1, samples_per_symbol * factor)).astype(int) - 1
    remaining_indices = np.rint(np.arange(ref_end + 2 * slot_duration * samples_per_symbol * factor, data.size + 1, 2 * slot_duration * samples_per_symbol * factor)).astype(int) - 1
    reference = filtered[reference_indices]
    result = np.concatenate((reference, filtered[remaining_indices])) - reference.mean()
    times = np.arange(8)
    free = result[:8] * np.exp(1j * 2 * np.pi * (-(250e3 * factor * times / 1e6)))
    frequency_offset = np.mean(np.diff(np.unwrap(np.angle(free)))) * 1e6 / (2 * np.pi)
    time_steps = np.concatenate((reference_indices + 1, remaining_indices + 1))
    phase = frequency_offset * time_steps / (samples_per_symbol * 1e6 * factor)
    return result * np.exp(1j * 2 * np.pi * -phase[:result.size])


def _handler(args, request):
    data = complex_from_json(request.get("cte_samples"), "cte_samples")
    result = iq_sample(data, mode=request.get("mode", "LE1M"), samples_per_symbol=request.get("samples_per_symbol", 8), slot_duration=request.get("slot_duration", 2), sample_offset=request.get("sample_offset", 4))
    encoded, artifacts = array_result("iq_samples", result, args)
    return {"result": encoded, "artifacts": artifacts}


if __name__ == "__main__":
    run_cli("ble_cte_iq_sample", _handler, artifacts=True, description=__doc__)
