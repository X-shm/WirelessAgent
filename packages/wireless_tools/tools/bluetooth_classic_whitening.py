"""Stateful Bluetooth whitening/dewhitening, including BLE channel seeds."""
from __future__ import annotations

from _bluetooth_algorithms import whiten
from _bluetooth_common import InputError, bit_vector, load_state, make_state, run_cli


def _handler(args, request):
    bits = bit_vector(request.get("bits"), "bits")
    initial = request.get("initial_conditions")
    channel_index = request.get("channel_index")
    state = load_state(args, "bluetooth_whitening")
    if state is not None:
        if initial is not None or channel_index is not None:
            raise InputError("state cannot be combined with initial_conditions or channel_index")
        initial = state["register"]
        channel_index = state["channel_index"]
    if initial is not None:
        if not isinstance(initial, list) or len(initial) != 7 or any(bit not in (0, 1, False, True) for bit in initial):
            raise InputError("initial_conditions must contain exactly seven 0/1 bits")
        if not any(initial):
            raise InputError("initial_conditions cannot be all zero")
        if channel_index is None:
            channel_index = 0
    elif not isinstance(channel_index, int):
        raise InputError("provide channel_index (0..39) or initial_conditions")
    out, next_register = whiten(bits, channel_index, list(initial) if initial is not None else None)
    return {"result": {"bits": out.tolist()}, "state": make_state("bluetooth_whitening", {"register": next_register, "channel_index": channel_index})}


if __name__ == "__main__":
    run_cli("bluetooth_classic_whitening", _handler, stateful=True, description=__doc__)
