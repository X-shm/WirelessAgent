"""Generate an uncoded or coded Bluetooth LE PHY waveform from PDU bits."""
from __future__ import annotations

import numpy as np

from _bluetooth_algorithms import ble_coded_phy_encode, ble_gmsk_modulate, ble_preamble, whiten
from _bluetooth_common import InputError, array_result, bit_vector, run_cli


_DEFAULT_ACCESS_ADDRESS = [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
                           0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0]


def generate(message: np.ndarray, mode: str = "LE1M", channel_index: int = 37,
             samples_per_symbol: int = 8, access_address: list[int] | None = None,
             whiten_status: str = "On", modulation_index: float = 0.5,
             pulse_length: int = 1, df_packet_type: str = "Disabled") -> tuple[np.ndarray, dict]:
    if mode not in {"LE1M", "LE2M", "LE500K", "LE125K"}:
        raise InputError("mode must be LE1M, LE2M, LE500K, or LE125K")
    address = bit_vector(access_address if access_address is not None else _DEFAULT_ACCESS_ADDRESS, "access_address")
    if address.size != 32:
        raise InputError("access_address must contain 32 bits")
    if whiten_status not in {"On", "Off"}:
        raise InputError("whiten_status must be On or Off")
    if df_packet_type not in {"Disabled", "ConnectionCTE", "ConnectionlessCTE"}:
        raise InputError("df_packet_type must be Disabled, ConnectionCTE, or ConnectionlessCTE")
    if mode in {"LE125K", "LE500K"} and df_packet_type != "Disabled":
        raise InputError("coded PHY does not support CTE")
    if df_packet_type == "ConnectionlessCTE" and mode != "LE1M":
        raise InputError("ConnectionlessCTE requires LE1M")
    payload = np.asarray(message, dtype=np.uint8)
    if payload.size == 0 or payload.size > 2088 or np.any((payload != 0) & (payload != 1)):
        raise InputError("message must contain 1..2088 binary bits")
    if whiten_status == "On":
        payload, _ = whiten(payload, channel_index)
    cte_symbols = 0
    if df_packet_type != "Disabled":
        start = 16 if df_packet_type == "ConnectionCTE" else 32
        if len(message) < start + 8:
            raise InputError(f"{df_packet_type} message must contain the CTEInfo field")
        cte_time = sum(int(message[start + bit]) << bit for bit in range(5))
        if not 2 <= cte_time <= 20:
            raise InputError("CTE length must be 2..20 units of 8 microseconds")
        cte_symbols = cte_time * 8 * (2 if mode == "LE2M" else 1)
    phy_payload = (ble_coded_phy_encode(payload, address, mode)
                   if mode in {"LE500K", "LE125K"}
                   else np.concatenate((address, payload, np.ones(cte_symbols, dtype=np.uint8))))
    frame = np.concatenate((ble_preamble(mode, address), phy_payload))
    return ble_gmsk_modulate(frame, samples_per_symbol, modulation_index, pulse_length), {
        "frame_bits": int(frame.size), "whitened": whiten_status == "On",
        "cte_symbols": cte_symbols, "df_packet_type": df_packet_type}


def _handler(args, request):
    message = bit_vector(request.get("message"), "message", max_length=2088)
    waveform, info = generate(message, request.get("mode", "LE1M"), request.get("channel_index", 37),
                              request.get("samples_per_symbol", 8), request.get("access_address"),
                              request.get("whiten_status", "On"), request.get("modulation_index", 0.5),
                              request.get("pulse_length", 1), request.get("df_packet_type", "Disabled"))
    result, artifacts = array_result("waveform", waveform, args)
    result.update(info)
    result["samples_per_symbol"] = request.get("samples_per_symbol", 8)
    return {"result": result, "artifacts": artifacts}


if __name__ == "__main__":
    run_cli("ble_waveform", _handler, artifacts=True, description=__doc__)
