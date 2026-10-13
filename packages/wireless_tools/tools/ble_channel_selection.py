"""Stateful Bluetooth LE Channel Selection Algorithm #1 and #2."""
from __future__ import annotations

from _bluetooth_common import InputError, load_state, make_state, run_cli


def _integer(value, name, lower, upper):
    if not isinstance(value, int) or isinstance(value, bool) or not lower <= value <= upper:
        raise InputError(f"{name} must be an integer in {lower}..{upper}")
    return value


def _used_channels(value):
    if value is None:
        return list(range(37))
    if not isinstance(value, list):
        raise InputError("used_channels must be a JSON array of channel indices")
    channels = sorted({_integer(item, "used_channels item", 0, 36) for item in value})
    if len(channels) < 2:
        raise InputError("used_channels must contain at least two distinct channel indices")
    return channels


def _access_address(value):
    if not isinstance(value, str) or len(value) != 8:
        raise InputError("access_address must be an eight-digit hexadecimal string")
    try:
        return int(value, 16), value.upper()
    except ValueError as exc:
        raise InputError("access_address must be an eight-digit hexadecimal string") from exc


def _reverse_byte(value):
    return int(f"{value:08b}"[::-1], 2)


def _permute(value):
    return (_reverse_byte(value >> 8) << 8) | _reverse_byte(value & 0xFF)


def _prn(counter, identifier):
    value = counter ^ identifier
    for _ in range(3):
        value = (17 * _permute(value) + identifier) & 0xFFFF
    return value, value ^ identifier


def _subevent_prn(last_prn, identifier):
    last_prn = (17 * _permute(last_prn) + identifier) & 0xFFFF
    return last_prn ^ identifier, last_prn


def _distance(number_used):
    return max(1, max(min(3, number_used - 5), min(11, (number_used - 10) // 2)))


def _event_map(unmapped, random_number, used):
    if unmapped in used:
        channel = unmapped
    else:
        channel = used[(len(used) * random_number) // 65536]
    return channel, used.index(channel)


def _initial_dynamic():
    return {
        "event_counter": 0,
        "last_unmapped_channel": 0,
        "prn_subevent_se": 0,
        "prn_subevent_lu": 0,
        "subevent_mapping_index": 0,
        "previous_subevent_number": 0,
        "channel_index": 0,
    }


def _settings(request, prior=None):
    defaults = prior or {
        "algorithm": 1,
        "hop_increment": 5,
        "access_address": "8E89BED6",
        "used_channels": list(range(37)),
        "subevent_channel_selection": False,
    }
    settings = dict(defaults)
    for key in ("algorithm", "hop_increment", "access_address", "used_channels", "subevent_channel_selection"):
        if key in request:
            candidate = request[key]
            if prior is not None and candidate != prior[key]:
                raise InputError(f"{key} must match the configuration in state")
            settings[key] = candidate
    settings["algorithm"] = _integer(settings["algorithm"], "algorithm", 1, 2)
    settings["hop_increment"] = _integer(settings["hop_increment"], "hop_increment", 5, 16)
    _, settings["access_address"] = _access_address(settings["access_address"])
    settings["used_channels"] = _used_channels(settings["used_channels"])
    if not isinstance(settings["subevent_channel_selection"], bool):
        raise InputError("subevent_channel_selection must be true or false")
    return settings


def select(settings, dynamic, *, count=1, isochronous_event_counter=None, subevent_number=None):
    """Run CSA calls and return selected channels plus the next dynamic state."""
    channels = []
    used = settings["used_channels"]
    if settings["subevent_channel_selection"]:
        if count != 1:
            raise InputError("count must be 1 for subevent channel selection")
        counter = _integer(isochronous_event_counter, "isochronous_event_counter", 0, 65535)
        number = _integer(subevent_number, "subevent_number", 1, 128)
        if settings["algorithm"] != 2:
            raise InputError("subevent channel selection requires algorithm 2")
        identifier = ((int(settings["access_address"], 16) >> 16)
                      ^ (int(settings["access_address"], 16) & 0xFFFF))
        if number == 1:
            dynamic["prn_subevent_lu"], prn_event = _prn(counter, identifier)
            unmapped = prn_event % 37
            channel, index = _event_map(unmapped, prn_event, used)
            dynamic["subevent_mapping_index"] = index
            dynamic["previous_subevent_number"] = number
        elif number == dynamic["previous_subevent_number"] + 1:
            dynamic["prn_subevent_se"], dynamic["prn_subevent_lu"] = _subevent_prn(
                dynamic["prn_subevent_lu"], identifier
            )
            index = (dynamic["subevent_mapping_index"] + _distance(len(used))
                     + int(dynamic["prn_subevent_se"] * ((len(used) - 2 * _distance(len(used)) + 1) / 65536))) % len(used)
            channel = used[index]
            dynamic["subevent_mapping_index"] = index
            dynamic["previous_subevent_number"] = number
        elif number == dynamic["previous_subevent_number"]:
            channel = dynamic["channel_index"]
        else:
            expected = dynamic["previous_subevent_number"] + 1
            raise InputError(f"subevent_number must be sequential: expected {expected}, got {number}")
        dynamic["channel_index"] = channel
        return [channel], dynamic
    count = _integer(count, "count", 1, 4096)
    for _ in range(count):
        if dynamic["event_counter"] > 65535:
            dynamic["event_counter"] = 0
        if settings["algorithm"] == 1:
            unmapped = (dynamic["last_unmapped_channel"] + settings["hop_increment"]) % 37
            channel = unmapped if unmapped in used else used[unmapped % len(used)]
            dynamic["last_unmapped_channel"] = unmapped
        else:
            identifier = ((int(settings["access_address"], 16) >> 16)
                          ^ (int(settings["access_address"], 16) & 0xFFFF))
            _, random_number = _prn(dynamic["event_counter"], identifier)
            channel, index = _event_map(random_number % 37, random_number, used)
            dynamic["prn_subevent_lu"] = _prn(dynamic["event_counter"], identifier)[0]
            dynamic["subevent_mapping_index"] = index
        channels.append(channel)
        dynamic["channel_index"] = channel
        dynamic["event_counter"] += 1
    return channels, dynamic


def _handler(args, request):
    previous = load_state(args, "ble_channel_selection")
    prior_settings = previous.get("settings") if previous else None
    settings = _settings(request, prior_settings)
    dynamic = dict(previous["dynamic"]) if previous else _initial_dynamic()
    if request.get("reset", False):
        if not isinstance(request["reset"], bool):
            raise InputError("reset must be true or false")
        dynamic = _initial_dynamic()
    channels, dynamic = select(
        settings, dynamic, count=request.get("count", 1),
        isochronous_event_counter=request.get("isochronous_event_counter"),
        subevent_number=request.get("subevent_number"),
    )
    result = {"channel_indices": channels, "event_counter": max(0, dynamic["event_counter"] - 1)}
    return {"result": result, "state": make_state("ble_channel_selection", {"settings": settings, "dynamic": dynamic})}


if __name__ == "__main__":
    run_cli("ble_channel_selection", _handler, stateful=True, description=__doc__)
