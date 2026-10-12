"""Generate deterministic Bluetooth BR/EDR/LE RF-PHY test waveforms."""
from __future__ import annotations

import numpy as np

from _bluetooth_algorithms import crc24_ble
from _bluetooth_common import InputError, array_result, run_cli
from bluetooth_classic_config import create
from bluetooth_classic_waveform import generate as generate_classic
from bluetooth_packet_duration import packet_duration
from ble_waveform import generate as generate_ble, _DEFAULT_ACCESS_ADDRESS


PATTERNS = {1: [1, 1, 1, 1, 0, 0, 0, 0], 2: [1, 0] * 4,
            4: [1] * 8, 5: [0] * 8, 6: [0] * 4 + [1] * 4,
            7: [0, 1] * 4}


def _pn(length: int, degree: int, tap: int) -> np.ndarray:
    bits = [1] * degree
    for index in range(degree, length):
        bits.append(bits[index - degree] ^ bits[index - (degree - tap)])
    return np.asarray(bits[:length], dtype=np.uint8)


def payload_bits(payload_type: int, length_octets: int) -> np.ndarray:
    if not isinstance(payload_type, int) or isinstance(payload_type, bool) or not 0 <= payload_type <= 7:
        raise InputError("payload_type must be an integer in 0..7")
    count = length_octets * 8
    if payload_type == 0:
        return _pn(count, 9, 5)
    if payload_type == 3:
        return _pn(count, 15, 14)
    return np.resize(np.asarray(PATTERNS[payload_type], dtype=np.uint8), count)


def generate(properties: dict) -> tuple[np.ndarray, dict]:
    cfg = create("test_waveform", properties)
    if cfg["mode"] in {"BR", "EDR2M", "EDR3M"}:
        kind = cfg["packet_type"]
        length = cfg["fixed_payload_length"]
        payload = payload_bits(cfg["payload_type"], length)
        waveform, _ = generate_classic(payload, {
            "mode": cfg["mode"], "packet_type": kind, "payload_length": length,
            "samples_per_symbol": cfg["samples_per_symbol"],
            "modulation_index": cfg["modulation_index"],
            "whiten_status": cfg["whiten_status"],
            "whiten_initialization": cfg["whiten_initialization"],
        })
        duration, _ = packet_duration(cfg["mode"], kind, length)
        trim = duration + (20 if cfg["mode"] != "BR" else 0)
        waveform = waveform[:int(trim) * cfg["samples_per_symbol"]]
        return waveform, {"message_bits": payload.tolist(), "packet_type": kind,
                          "samples": int(waveform.size)}
    if cfg["mode"] not in {"LE1M", "LE2M", "LE500K", "LE125K"}:
        raise InputError("unsupported Bluetooth test waveform mode")
    if cfg["packet_type"] not in {"Disabled", "ConnectionCTE"}:
        raise InputError("unsupported LE test packet_type")
    if cfg["packet_type"] == "ConnectionCTE" and cfg["mode"] not in {"LE1M", "LE2M"}:
        raise InputError("ConnectionCTE test packets require LE1M or LE2M")
    length = cfg["payload_length"]
    payload = payload_bits(cfg["payload_type"], length)
    cte_enabled = cfg["packet_type"] == "ConnectionCTE"
    header = np.asarray([(cfg["payload_type"] >> i) & 1 for i in range(4)]
                        + [0, int(cte_enabled), 0, 0]
                        + [(length >> i) & 1 for i in range(8)], dtype=np.uint8)
    if cte_enabled:
        cte_length = cfg["cte_length"]
        cte_type = cfg["cte_type"]
        if not isinstance(cte_length, int) or isinstance(cte_length, bool) or not 2 <= cte_length <= 20:
            raise InputError("cte_length must be an integer in 2..20")
        if not isinstance(cte_type, list) or len(cte_type) != 2 or any(bit not in (0, 1) for bit in cte_type) or cte_type == [1, 1]:
            raise InputError("cte_type must be a two-bit CTE type 0..2")
        cte_info = np.asarray([(cte_length >> i) & 1 for i in range(5)]
                              + [0] + cte_type, dtype=np.uint8)
    else:
        cte_info = np.empty(0, dtype=np.uint8)
    pdu = np.concatenate((header, cte_info, payload))
    message = np.concatenate((pdu, crc24_ble(pdu)))
    address = list(reversed(_DEFAULT_ACCESS_ADDRESS))
    waveform, _ = generate_ble(message, mode=cfg["mode"],
                               samples_per_symbol=cfg["samples_per_symbol"],
                               access_address=address, whiten_status="Off",
                               modulation_index=cfg["modulation_index"],
                               pulse_length=cfg["pulse_length"],
                               df_packet_type=cfg["packet_type"])
    return waveform, {"message_bits": message.tolist(), "access_address": address,
                      "samples": int(waveform.size)}


def _handler(args, request):
    properties = request.get("properties", {})
    if not isinstance(properties, dict):
        raise InputError("properties must be a JSON object")
    waveform, detail = generate(properties)
    result, artifacts = array_result("waveform", waveform, args)
    result.update(detail)
    return {"result": result, "artifacts": artifacts}


if __name__ == "__main__":
    run_cli("bluetooth_test_waveform", _handler, artifacts=True, description=__doc__)
