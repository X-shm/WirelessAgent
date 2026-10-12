"""Measure Bluetooth LE RF-PHY test waveforms in pure Python.

The CLI mirrors the output families of ``bluetoothTestWaveformValidate``:
CRC verdicts, frequency/modulation measurements, and CTE IQ measurements.
It returns named JSON fields instead of MATLAB's positional ``varargout``.
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from zipfile import BadZipFile

from _bluetooth_algorithms import crc24_ble
from _bluetooth_common import InputError, complex_from_json, complex_to_json, run_cli
from ble_ideal_receiver import receive
from ble_waveform import _DEFAULT_ACCESS_ADDRESS
from bluetooth_classic_config import create as classic_configuration


CRC_TESTS = {"Blocking", "C/I", "Intermodulation", "PER report integrity"}
FREQUENCY_TESTS = {"Modulation characteristics", "Carrier frequency offset and drift"}
IQ_TESTS = {"IQ samples coherency", "IQ samples dynamic range"}


def _configuration(*, test: str, mode: str, samples_per_symbol: int,
                   payload_length: int | None, properties: dict | None) -> dict:
    """Normalize compatibility arguments or an explicit RF-PHY configuration."""
    if properties is not None:
        if not isinstance(properties, dict):
            raise InputError("configuration must be an RF-PHY properties JSON object")
        merged = dict(properties)
        # Explicit function arguments remain useful for callers that only
        # need to override an archived configuration.
        merged.setdefault("test", test)
        merged.setdefault("mode", mode)
        merged.setdefault("samples_per_symbol", samples_per_symbol)
        if payload_length is not None:
            merged.setdefault("payload_length", payload_length)
    else:
        merged = {"test": test, "mode": mode, "samples_per_symbol": samples_per_symbol}
        if payload_length is not None:
            merged["payload_length"] = payload_length
    return classic_configuration("rf_phy_test", merged)


def _waveform_array(waveform: object, *, columns: int | None = None) -> np.ndarray:
    values = np.asarray(waveform, dtype=complex)
    if values.ndim == 1:
        values = values[:, None]
    if values.ndim != 2 or values.shape[0] < 2 or not np.all(np.isfinite(values)):
        raise InputError("waveform must be a finite one- or two-dimensional complex array")
    if columns is not None and values.shape[1] != columns:
        raise InputError(f"waveform must have exactly {columns} column(s) for this RF-PHY test")
    return values


def _frequency_waveform(waveform: np.ndarray, config: dict) -> tuple[np.ndarray, float]:
    values = _waveform_array(waveform)
    mode, sps = config["mode"], config["samples_per_symbol"]
    if mode not in {"LE1M", "LE2M", "LE125K"}:
        raise InputError("frequency measurements support LE1M, LE2M, and LE125K")
    if values.shape[0] % sps:
        raise InputError("waveform row count must be a multiple of samples_per_symbol")
    sample_rate = (2e6 if mode == "LE2M" else 1e6) * sps
    return np.diff(np.unwrap(np.angle(values), axis=0), axis=0) * sample_rate / (2 * np.pi), sample_rate


def _discard_positions(config: dict) -> tuple[float, float, float, float, float, float]:
    """Port of Bluetooth Toolbox's RF-PHY timing-discard calculation."""
    mode, test, packet = config["mode"], config["test"], config["packet_type"]
    preamble = 8 if mode == "LE1M" else 16 if mode == "LE2M" else 80
    crc, access, header, cte_info = 24, 32, 16, 8
    cte_length = config["cte_length"] if packet == "ConnectionCTE" else 0
    test_id = _rf_test_id(config)
    start1 = end1 = start2 = end2 = start3 = end3 = 0.0
    term1 = term2 = coded = 0
    if test_id in {"RF-PHY/TRM/BV-06-C", "RF-PHY/TRM/BV-12-C"}:
        start1 = 1
    elif test_id in {"RF-PHY/TRM/BV-05-C", "RF-PHY/TRM/BV-09-C", "RF-PHY/TRM/BV-10-C", "RF-PHY/TRM/BV-11-C"}:
        start1 = end1 = 4
    elif test_id == "RF-PHY/TRM/BV-13-C":
        term1 = term2 = 3
        coded, start1, end1 = 2, 30.25, 34.75
    elif test_id == "RF-PHY/TRM/BV-14-C":
        term1 = term2 = 3
        coded, start1, end1 = 2, 26, -3
    elif test_id == "RF-PHY/TRM/BV-16-C":
        start1, end1 = 4, 4
        start2, end2 = config["payload_length"] * 8 - 20, 4
        start3, end3 = 4, 12 - 8 * (cte_length % 2)
    elif test_id == "RF-PHY/TRM/BV-17-C":
        start1, end1 = 4, 4
        start2, end2 = config["payload_length"] * 8 - 36, 4
        start3, end3 = 8, 24 - 16 * (cte_length % 2)
    factor = 8 if mode == "LE125K" else 1
    if test_id in {"RF-PHY/TRM/BV-16-C", "RF-PHY/TRM/BV-17-C"}:
        multiplier = 2 if mode == "LE2M" else 1
        return (preamble + access + header + cte_info + start1,
                end1 + crc + cte_length * 8 * multiplier,
                preamble + access + header + cte_info + start2,
                end2 + crc + cte_length * 8 * multiplier,
                preamble + access + header + cte_info + config["payload_length"] * 8 + crc + start3,
                end3)
    return (preamble + (access + header + term1 + coded + start1) * factor,
            (end1 + crc + term2) * factor, 0, 0, 0, 0)


def _rf_test_id(config: dict) -> str | None:
    """Small local mirror of the applicable transmitter measurement cases."""
    mode, test, packet = config["mode"], config["test"], config["packet_type"]
    standard = config["modulation_index"] != 0.5
    if test == "Modulation characteristics":
        return {"LE1M": "RF-PHY/TRM/BV-05-C" if standard else "RF-PHY/TRM/BV-09-C",
                "LE2M": "RF-PHY/TRM/BV-10-C" if standard else "RF-PHY/TRM/BV-11-C",
                "LE125K": "RF-PHY/TRM/BV-13-C"}.get(mode)
    if test == "Carrier frequency offset and drift":
        if mode == "LE1M":
            return "RF-PHY/TRM/BV-16-C" if packet == "ConnectionCTE" else "RF-PHY/TRM/BV-06-C"
        if mode == "LE2M":
            return "RF-PHY/TRM/BV-17-C" if packet == "ConnectionCTE" else "RF-PHY/TRM/BV-12-C"
        return "RF-PHY/TRM/BV-14-C" if mode == "LE125K" else None
    return None


def _modulation_frequency_calculate(values: np.ndarray, sps: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Port of ``modulationFrequencyCalculate`` with zero-based indexing."""
    values = _waveform_array(values).real
    spb = sps * 8
    num_bytes = values.shape[0] // spb
    if values.shape[0] % spb or num_bytes < 2:
        raise InputError("measurement region must contain at least two complete bytes")
    columns = values.shape[1]
    center = np.zeros((num_bytes - 1, columns))
    deviation = np.zeros((num_bytes - 1, columns))
    # Keep the Toolbox's historical output layout exactly.  With two input
    # columns, its second-sequence eight-value assignments overwrite the
    # first sequence's initial four-value assignments in this one vector.
    maxima = np.zeros((num_bytes - 1) * 4 * columns)
    offsets: list[int] = []
    for column in range(columns):
        changes = np.flatnonzero(np.diff(np.sign(values[:spb, column])))
        if changes.size == 0:
            raise InputError("measurement region has no frequency transition in its first byte")
        # MATLAB: find(diff(sign(...))) + 1, followed by an inclusive
        # one-based slice whose Python start is the resulting value.
        offsets.append(int(changes[0] + 2))
    for byte in range(num_bytes - 1):
        for column, offset in enumerate(offsets):
            section = values[spb * byte + offset:spb * (byte + 1) + offset, column]
            if section.size != spb:
                raise InputError("measurement region is too short after transition alignment")
            center[byte, column] = np.mean(section)
            bit_positions = (2, 3, 6, 7) if column == 0 else tuple(range(1, 9))
            bit_offsets = []
            for bit in bit_positions:
                samples = section[(bit - 1) * sps:bit * sps]
                value = np.mean(samples) if column == 0 else np.max(np.abs(samples - center[byte, column]))
                bit_offsets.append(abs(value - center[byte, column]) if column == 0 else value)
            deviation[byte, column] = np.mean(bit_offsets)
            if column == 0:
                maxima[4 * byte:4 * (byte + 1)] = bit_offsets
            else:
                maxima[8 * byte:8 * (byte + 1)] = bit_offsets
    return np.mean(deviation, axis=0), center, maxima


def _slice_measurement(values: np.ndarray, start_bits: float, end_bits: float, sps: int,
                       *, start_after_boundary: bool = False) -> np.ndarray:
    start = start_bits * sps
    end = end_bits * sps
    if abs(start - round(start)) > 1e-9 or abs(end - round(end)) > 1e-9:
        raise InputError("samples_per_symbol is incompatible with this coded PHY measurement")
    start_i, end_i = int(round(start)), int(round(end))
    # MATLAB uses one-based inclusive ranges.  Most RF-PHY branches start
    # at ``discard*sps``; the drift bins explicitly use ``+1``.
    start_i = start_i if start_after_boundary else start_i - 1
    result = values[start_i:values.shape[0] - end_i]
    if result.size == 0:
        raise InputError("waveform is too short for the RF-PHY measurement interval")
    return result


def _frequency_measurement(waveform: np.ndarray, config: dict) -> dict:
    instantaneous, sample_rate = _frequency_waveform(waveform, config)
    test_id = _rf_test_id(config)
    if test_id is None:
        raise InputError("configuration does not select a supported RF-PHY frequency measurement")
    expected_columns = 2 if test_id in {"RF-PHY/TRM/BV-05-C", "RF-PHY/TRM/BV-09-C", "RF-PHY/TRM/BV-10-C", "RF-PHY/TRM/BV-11-C"} else 1
    if instantaneous.shape[1] != expected_columns:
        raise InputError(f"waveform must have exactly {expected_columns} column(s) for {config['test']}")
    positions = _discard_positions(config)
    if config["test"] == "Modulation characteristics":
        measured = _slice_measurement(instantaneous, positions[0], positions[1], config["samples_per_symbol"])
        average, center, maximum = _modulation_frequency_calculate(measured, config["samples_per_symbol"])
        return {"measurement": "modulation_characteristics", "test_id": test_id,
                "frequency_demodulated_hz": measured.tolist(),
                "average_frequency_deviation_hz": average.tolist(),
                "average_center_frequency_hz": center.tolist(),
                "maximum_frequency_deviation_hz": maximum.tolist()}
    mode, sps = config["mode"], config["samples_per_symbol"]
    interval, preamble = ({"LE1M": (10, 8), "LE2M": (20, 16), "LE125K": (16, 80)}[mode])
    time = np.arange(instantaneous.shape[0], dtype=float) / sample_rate
    if mode == "LE125K":
        indices = np.arange(2 * sps, (preamble - 14) * sps)
        preamble_indices = indices[:interval * sps]
    else:
        start, stop = int(0.5 * sps) - 1, int((preamble + 0.5) * sps)
        preamble_indices = np.arange(start, stop)
        indices = preamble_indices
    preamble_frequency = instantaneous[preamble_indices, 0]
    preamble_time = time[preamble_indices]
    initial = float(np.trapezoid(preamble_frequency, preamble_time) / (preamble_frequency.size / sample_rate))
    if config["packet_type"] == "ConnectionCTE":
        offset_frequency = _slice_measurement(instantaneous[:, 0], positions[0], positions[1], sps)
        avg_deviation = _modulation_frequency_calculate(offset_frequency[:, None], sps)[0]
        center_region = _slice_measurement(instantaneous[:, 0], positions[2], positions[3], sps)
        average_center = float(np.mean(center_region))
        cte_frequency = _slice_measurement(instantaneous[:, 0], positions[4], positions[5], sps,
                                           start_after_boundary=True)
        cte_time = _slice_measurement(time, positions[4], positions[5], sps,
                                      start_after_boundary=True)
        count = cte_frequency.size // (interval * sps)
        drift = []
        for index in range(count):
            segment = slice(index * interval * sps, (index + 1) * interval * sps)
            drift.append(float(np.trapezoid(cte_frequency[segment], cte_time[segment]) /
                               (interval * sps / sample_rate) - avg_deviation[0]))
        return {"measurement": "carrier_frequency_offset_and_drift", "test_id": test_id,
                "frequency_demodulated_hz": instantaneous[:, 0].tolist(),
                "initial_frequency_offset_hz": initial, "average_center_frequency_hz": average_center,
                "carrier_frequency_drift_hz": drift}
    payload_frequency = _slice_measurement(instantaneous[:, 0], positions[0], positions[1], sps,
                                           start_after_boundary=True)
    payload_time = _slice_measurement(time, positions[0], positions[1], sps,
                                      start_after_boundary=True)
    if mode == "LE125K":
        extra = indices[interval * sps:]
        payload_frequency = np.concatenate((instantaneous[extra, 0], payload_frequency))
        payload_time = np.concatenate((time[extra], payload_time))
    count = payload_frequency.size // (interval * sps)
    drift = []
    for index in range(count):
        segment = slice(index * interval * sps, (index + 1) * interval * sps)
        drift.append(float(np.trapezoid(payload_frequency[segment], payload_time[segment]) /
                           (interval * sps / sample_rate)))
    return {"measurement": "carrier_frequency_offset_and_drift", "test_id": test_id,
            "frequency_demodulated_hz": instantaneous[:, 0].tolist(),
            "initial_frequency_offset_hz": initial, "carrier_frequency_drift_hz": drift}


def _principal_angle(values: np.ndarray) -> np.ndarray:
    # np.angle(exp(1j*x)) has range [-pi,pi], whereas the Toolbox uses
    # (-pi,pi]; replace the one endpoint to retain that documented range.
    output = np.angle(np.exp(1j * values))
    output[np.isclose(output, -np.pi)] = np.pi
    return output


def _iq_measurement(waveform: np.ndarray, config: dict) -> dict:
    if config["mode"] not in {"LE1M", "LE2M"}:
        raise InputError("IQ measurements support LE1M and LE2M")
    if config["packet_type"] != "ConnectionCTE":
        raise InputError("IQ measurements require packet_type=ConnectionCTE")
    slot_duration = 1 if config["cte_type"][0] else 2
    _bits, _address, iq = receive(_waveform_array(waveform, columns=1)[:, 0], mode=config["mode"],
                                  samples_per_symbol=config["samples_per_symbol"], whiten_status="Off",
                                  pulse_length=config["pulse_length"], modulation_index=config["modulation_index"],
                                  df_packet_type="ConnectionCTE", slot_duration=slot_duration, return_iq=True)
    required = iq[8:]
    elements = config["array_size"]
    if required.size == 0:
        raise InputError("waveform did not yield CTE IQ samples")
    if config["test"] == "IQ samples dynamic range":
        non_reference_indices = np.arange(0, required.size, 4)
        reference_indices = np.setdiff1d(np.arange(required.size), non_reference_indices, assume_unique=True)
        count = int(np.ceil(non_reference_indices.size / (elements - 1)))
        non_reference = np.zeros((count, elements - 1))
        for element in range(elements - 1):
            indices = non_reference_indices[element::elements - 1]
            non_reference[:indices.size, element] = np.abs(required[indices])
        return {"measurement": "iq_samples_dynamic_range",
                "mean_amplitude_reference_antennas": np.abs(required[reference_indices]).tolist(),
                "mean_amplitude_nonreference_antennas": non_reference.tolist()}
    phase = np.unwrap(np.angle(iq))[8:]
    indices = np.arange(4, max(4, phase.size - 1), 4)
    if indices.size == 0:
        raise InputError("waveform does not contain enough switched IQ samples")
    count = int(np.ceil(indices.size / (elements - 1)))
    relative = np.zeros((count, elements - 1))
    sums = np.zeros(elements - 1, dtype=complex)
    angles = np.zeros(elements - 1)
    for element in range(elements - 1):
        selected = indices[element::elements - 1]
        selected = selected[(selected - 2 >= 0) & (selected < phase.size)]
        values = _principal_angle(phase[selected] - 2 * phase[selected - 1] + phase[selected - 2])
        relative[:values.size, element] = values
        sums[element] = np.sum(np.exp(1j * values))
        angles[element] = np.angle(sums[element])
    reference_indices = indices[(indices + 1 < phase.size) & (indices - 2 >= 0)]
    reference = _principal_angle(phase[reference_indices + 1] - 3 * phase[reference_indices - 1] +
                                 2 * phase[reference_indices - 2])
    reference_sum = np.sum(np.exp(1j * reference))
    return {"measurement": "iq_samples_coherency", "relative_phase_rad": relative.tolist(),
            "sum_relative_phase": complex_to_json(sums), "angle_relative_phase_rad": angles.tolist(),
            "reference_phase_deviation_rad": reference.tolist(),
            "sum_reference_phase_deviation": complex_to_json(np.asarray([reference_sum])),
            "angle_reference_phase_deviation_rad": float(np.angle(reference_sum))}


def validate(waveform, *, test="PER report integrity", mode="LE1M", samples_per_symbol=8,
             payload_length=None, configuration: dict | None = None) -> dict:
    config = _configuration(test=test, mode=mode, samples_per_symbol=samples_per_symbol,
                            payload_length=payload_length, properties=configuration)
    if config["test"] in FREQUENCY_TESTS:
        return _frequency_measurement(waveform, config)
    if config["test"] in IQ_TESTS:
        return _iq_measurement(waveform, config)
    if config["test"] not in CRC_TESTS:
        raise InputError("this RF-PHY test has no waveform-validation measurement branch")
    if config["mode"] in {"LE125K", "LE500K"} and config["test"] not in {"C/I", "PER report integrity"}:
        raise InputError("coded PHY supports C/I and PER report integrity CRC validation only")
    bits, address = receive(_waveform_array(waveform, columns=1)[:, 0], mode=config["mode"],
                            samples_per_symbol=config["samples_per_symbol"], whiten_status="Off",
                            pulse_length=config["pulse_length"], modulation_index=config["modulation_index"])
    reference = np.asarray(list(reversed(_DEFAULT_ACCESS_ADDRESS)), dtype=np.uint8)
    if not np.array_equal(address, reference) or bits.size < 40:
        return {"crc_error": True, "access_address_valid": False, "decoded_payload_length": None}
    length = sum(int(bit) << shift for shift, bit in enumerate(bits[8:16]))
    if bits.size < 16 + 8 * length + 24:
        return {"crc_error": True, "access_address_valid": True, "decoded_payload_length": length}
    body = bits[:16 + 8 * length]
    received = bits[body.size:body.size + 24]
    expected = crc24_ble(body)
    valid = np.array_equal(received, expected)
    if test == "PER report integrity":
        valid = valid or np.array_equal(received[:-1], expected[:-1]) and received[-1] != expected[-1]
    return {"crc_error": not valid, "access_address_valid": True,
            "decoded_payload_length": length}


def _handler(_args, request):
    has_inline = "waveform" in request
    has_file = "waveform_file" in request
    if has_inline == has_file:
        raise InputError("provide exactly one of waveform or waveform_file")
    if has_file:
        raw = request["waveform_file"]
        if not isinstance(raw, str) or not raw:
            raise InputError("waveform_file must be a nonempty .npz path")
        path = Path(raw).expanduser().resolve()
        if path.suffix.lower() != ".npz" or not path.is_file():
            raise InputError("waveform_file must be an existing .npz file")
        try:
            with np.load(path, allow_pickle=False) as archive:
                if "waveform" not in archive.files:
                    raise InputError("waveform_file has no waveform array")
                waveform = np.asarray(archive["waveform"])
        except (OSError, ValueError, BadZipFile) as exc:
            raise InputError(f"cannot load waveform_file: {exc}") from exc
        if waveform.ndim not in {1, 2} or not np.iscomplexobj(waveform):
            raise InputError("waveform_file waveform must be a one- or two-dimensional complex array")
    else:
        waveform = complex_from_json(request["waveform"], "waveform")
    return {"result": validate(waveform, test=request.get("test", "PER report integrity"),
                               mode=request.get("mode", "LE1M"),
                               samples_per_symbol=request.get("samples_per_symbol", 8),
                               payload_length=request.get("payload_length"),
                               configuration=request.get("configuration"))}


if __name__ == "__main__":
    run_cli("bluetooth_test_waveform_validate", _handler, description=__doc__)
