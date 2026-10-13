"""Decode Bluetooth LE uncoded/coded GFSK waveforms to PHY bits."""
from __future__ import annotations

from pathlib import Path
from zipfile import BadZipFile
import numpy as np

from _bluetooth_algorithms import ble_coded_phy_decode, ble_gmsk_modulate, whiten
from _bluetooth_common import InputError, complex_from_json, complex_to_json, run_cli


def _cte_iq_samples(waveform: np.ndarray, bits: np.ndarray, *, mode: str,
                    samples_per_symbol: int, df_packet_type: str,
                    slot_duration: int, cte_time: int) -> np.ndarray:
    sps = samples_per_symbol
    factor = 2 if mode == "LE2M" else 1
    time = np.linspace(-1, 1, 2 * sps + 1)
    alpha = np.sqrt(np.log(2) / 2) / 0.5
    pulse = (np.sqrt(np.pi) / alpha) * np.exp(-(time * np.pi / alpha) ** 2)
    filtered = np.convolve(waveform, pulse / pulse.sum(), mode="same")
    pdu_length = sum(int(bits[8 + index]) << index for index in range(8))
    cte_start = 16 if df_packet_type == "ConnectionCTE" else 32
    cte_type = sum(int(bits[cte_start + 6 + index]) << index for index in range(2))
    if cte_type in (1, 2):
        slot_duration = cte_type
    header_length = 24 if df_packet_type == "ConnectionCTE" else 16
    start = ((16 if mode == "LE2M" else 8) + 32 + header_length
             + pdu_length * 8 + 24) * sps
    count = cte_time * 8 * factor * sps
    cte = np.zeros(count, dtype=complex)
    if start < filtered.size:
        available = filtered[start:start + count]
        cte[:available.size] = available
    sample_point = 0.5 if mode == "LE2M" or sps % 2 == 0 else np.ceil(0.5 * sps) / sps
    reference = np.arange(8, dtype=float) + 4 + sample_point
    ref_indices = np.floor(reference * sps * factor + 0.5).astype(int) - 1
    samples = [cte[ref_indices]]
    slot_point = sample_point
    if slot_duration == 2:
        slot_point = 1.5 if mode == "LE2M" or sps % 2 == 0 else np.ceil(1.5 * sps) / sps
    first = int(np.floor((4 + 8 + slot_duration + slot_point) * sps * factor + 0.5)) - 1
    step = 2 * slot_duration * sps * factor
    if first < count:
        samples.append(cte[first:count:step])
    return np.concatenate(samples)


def _recover_delayed_symbols(samples: np.ndarray, hard: np.ndarray, *,
                             delay: int, samples_per_symbol: int,
                             modulation_index: float, pulse_length: int) -> np.ndarray:
    """Resolve the short CPM tail using a noiseless waveform comparison."""
    known = hard[delay:]
    best = None
    best_error = float("inf")
    for candidate in range(1 << delay):
        tail = np.asarray([(candidate >> bit) & 1 for bit in range(delay)], dtype=np.uint8)
        frame = np.concatenate((known, tail))
        predicted = ble_gmsk_modulate(frame, samples_per_symbol, modulation_index, pulse_length)
        phase = np.vdot(predicted, samples)
        if phase:
            predicted *= phase / abs(phase)
        residual = samples - predicted
        error = float(np.vdot(residual, residual).real)
        if error < best_error:
            best, best_error = frame, error
    return best


def receive(waveform, *, mode="LE1M", channel_index=37, samples_per_symbol=8,
            whiten_status="On", pulse_length=1,
            df_packet_type="Disabled", slot_duration=2,
            modulation_index=0.5, return_iq=False):
    if mode not in {"LE1M", "LE2M", "LE500K", "LE125K"}:
        raise InputError("mode must be LE1M, LE2M, LE500K, or LE125K")
    if not isinstance(samples_per_symbol, int) or isinstance(samples_per_symbol, bool) or samples_per_symbol < 2:
        raise InputError("samples_per_symbol must be an integer of at least 2")
    if not isinstance(channel_index, int) or isinstance(channel_index, bool) or not 0 <= channel_index <= 39:
        raise InputError("channel_index must be in 0..39")
    if whiten_status not in {"On", "Off"}:
        raise InputError("whiten_status must be On or Off")
    if pulse_length not in (1, 2, 3, 4):
        raise InputError("pulse_length must be 1, 2, 3, or 4")
    if df_packet_type not in {"Disabled", "ConnectionCTE", "ConnectionlessCTE"}:
        raise InputError("unsupported df_packet_type")
    if df_packet_type != "Disabled" and mode in {"LE125K", "LE500K"}:
        raise InputError("coded PHY does not support CTE")
    if df_packet_type == "ConnectionlessCTE" and mode != "LE1M":
        raise InputError("ConnectionlessCTE requires LE1M")
    if slot_duration not in (1, 2):
        raise InputError("slot_duration must be 1 or 2")
    if isinstance(modulation_index, bool) or not isinstance(modulation_index, (int, float)) or not 0.45 <= modulation_index <= 0.55:
        raise InputError("modulation_index must be in 0.45..0.55")
    samples = np.asarray(waveform, dtype=complex).reshape(-1)
    preamble = 8 if mode == "LE1M" else 16 if mode == "LE2M" else 80
    if samples.size <= (preamble + 32) * samples_per_symbol or samples.size % samples_per_symbol:
        raise InputError("waveform length must contain preamble, access address, and payload symbols")
    symbols = samples.reshape(-1, samples_per_symbol)
    frequency = np.angle(symbols[:, 1:] * np.conj(symbols[:, :-1]))
    hard = (frequency.mean(axis=1) >= 0).astype(np.uint8)
    delay = pulse_length // 2
    if delay and mode in {"LE1M", "LE2M"}:
        hard = _recover_delayed_symbols(samples, hard, delay=delay,
                                        samples_per_symbol=samples_per_symbol,
                                        modulation_index=modulation_index,
                                        pulse_length=pulse_length)
    cte_time = 0
    if mode in {"LE125K", "LE500K"}:
        # A pulse spanning L symbols delays the frequency decisions by
        # floor(L/2) symbols.  The missing tail is FEC termination data.
        if delay:
            hard = np.concatenate((hard[delay:], np.zeros(delay, dtype=np.uint8)))
        payload, access_address = ble_coded_phy_decode(hard[preamble:], mode)
    else:
        access_address = hard[preamble:preamble + 32]
        payload = hard[preamble + 32:]
        if df_packet_type != "Disabled":
            start = 16 if df_packet_type == "ConnectionCTE" else 32
            if payload.size < start + 8:
                raise InputError("waveform does not contain CTEInfo")
            header = payload[:start + 8]
            if whiten_status == "On":
                header, _ = whiten(header, channel_index)
            cte_time = sum(int(header[start + bit]) << bit for bit in range(5))
            if not 2 <= cte_time <= 20:
                raise InputError("decoded CTE length must be 2..20")
            cte_symbols = cte_time * 8 * (2 if mode == "LE2M" else 1)
            if payload.size < cte_symbols + start + 8:
                raise InputError("waveform does not contain CTE and payload")
            payload = payload[:-cte_symbols]
    if whiten_status == "On":
        payload, _ = whiten(payload, channel_index)
    if return_iq:
        iq = (_cte_iq_samples(samples, payload, mode=mode,
                              samples_per_symbol=samples_per_symbol,
                              df_packet_type=df_packet_type,
                              slot_duration=slot_duration, cte_time=cte_time)
              if df_packet_type != "Disabled" else np.empty(0, dtype=complex))
        return payload, access_address, iq
    return payload, access_address


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
        if waveform.ndim != 1 or not np.iscomplexobj(waveform):
            raise InputError("waveform_file waveform must be a 1-D complex array")
    else:
        waveform = complex_from_json(request["waveform"], "waveform")
    bits, address, iq = receive(waveform, mode=request.get("mode", "LE1M"),
                                channel_index=request.get("channel_index", 37),
                                samples_per_symbol=request.get("samples_per_symbol", 8),
                                whiten_status=request.get("whiten_status", "On"),
                                pulse_length=request.get("pulse_length", 1),
                                df_packet_type=request.get("df_packet_type", "Disabled"),
                                slot_duration=request.get("slot_duration", 2),
                                modulation_index=request.get("modulation_index", 0.5),
                                return_iq=True)
    return {"result": {"bits": bits.tolist(), "access_address": address.tolist(),
                       "bit_count": int(bits.size), "iq_samples": complex_to_json(iq)}}


if __name__ == "__main__":
    run_cli("ble_ideal_receiver", _handler, description=__doc__)
