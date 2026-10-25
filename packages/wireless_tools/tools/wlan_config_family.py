"""Independent, serializable WLAN configuration and enum class slices."""
from __future__ import annotations

import math
from functools import partial

from _nr_remaining_common import run_cli


ENUMS = {
    "wlan.type.ChannelCoding": {"bcc": 0, "ldpc": 1},
    "wlan.type.EHTPPDUType": {"su": 0, "ndp": 1, "dl_ofdma": 2, "dl_mumimo": 3, "unknown": 4},
    "wlan.type.PostFECPaddingSource": {"mt19937arwithseed": 0, "globalstream": 1, "userdefined": 2},
    "wlan.type.RecoveredChannelCoding": {"bcc": 0, "ldpc": 1, "unknown": 2},
    "wlan.type.SpatialMapping": {"direct": 0, "hadamard": 1, "fourier": 2, "custom": 3},
    "wlan.type.uhrChannelCoding": {"bcc": 0, "ldpc": 1, "ldpc2x": 2},
}

CONFIGS = (
    "wlanDMGConfig", "wlanEHTMUConfig", "wlanEHTRecoveryConfig", "wlanEHTRU",
    "wlanEHTTBConfig", "wlanEHTUser", "wlanHEMUConfig", "wlanHEMURU",
    "wlanHEMUUser", "wlanHERecoveryConfig", "wlanHESUConfig", "wlanHETBConfig",
    "wlanHTConfig", "wlanMACFrameConfig", "wlanMACManagementConfig",
    "wlanMACTriggerConfig", "wlanMACTriggerUserConfig", "wlanNonHTConfig",
    "wlanS1GConfig", "wlanURAConfig", "wlanVHTConfig", "wlanWURConfig",
    "wlanWURSubchannel",
)

_BANDWIDTHS = {"CBW1": 1, "CBW2": 2, "CBW4": 4, "CBW5": 5, "CBW8": 8,
               "CBW10": 10, "CBW16": 16, "CBW20": 20, "CBW40": 40,
               "CBW80": 80, "CBW160": 160, "CBW320": 320, "CBW2160": 2160}
_RU_SIZES = {26, 52, 78, 106, 132, 242, 484, 996, 1992, 3984}


def enum_type(class_name, name=None, code=None):
    values = ENUMS[class_name]
    if name is not None and name not in values:
        raise ValueError(f"{class_name}: unknown enum member {name}")
    if code is not None and (not isinstance(code, int) or code not in values.values()):
        raise ValueError(f"{class_name}: unknown enum code {code}")
    if name is not None and code is not None and values[name] != code:
        raise ValueError("enum name and code disagree")
    found = name if name is not None else next((k for k, v in values.items() if v == code), None)
    return {"class": class_name, "members": values, "name": found,
            "code": values[found] if found is not None else None}


def _validate_property(key, value):
    if key == "ChannelBandwidth":
        if value not in _BANDWIDTHS:
            raise ValueError("ChannelBandwidth must be a supported CBW value")
    elif key in ("MCS", "NumSpaceTimeStreams", "NumTransmitAntennas", "NumReceiveAntennas",
                 "PSDULength", "APEPLength", "NumUsers", "RUSize", "RUIndex"):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{key} must be a nonnegative integer")
        if key == "MCS" and value > 15:
            raise ValueError("MCS must be in 0..15")
        if key.startswith("Num") and value == 0:
            raise ValueError(f"{key} must be positive")
        if key == "RUSize" and value not in _RU_SIZES:
            raise ValueError("RUSize must be a standard WLAN RU size")
        if key == "RUIndex" and value < 1:
            raise ValueError("RUIndex must be positive")
    elif key in ("CenterFrequency", "SampleRate", "ElementSpacing"):
        if isinstance(value, (int, float)) and (not math.isfinite(value) or value <= 0):
            raise ValueError(f"{key} must be positive and finite")
    elif key == "ChannelCoding":
        if value not in ("BCC", "LDPC", "bcc", "ldpc", 0, 1):
            raise ValueError("ChannelCoding must be BCC or LDPC")


def config(class_name, properties=None, **overrides):
    """Build a validated JSON descriptor for a public WLAN config class."""
    if properties is None:
        properties = {}
    if not isinstance(properties, dict):
        raise ValueError("properties must be a JSON object")
    fields = {**properties, **overrides}
    if not all(isinstance(k, str) and k and k[0].isalpha() for k in fields):
        raise ValueError("property names must be nonempty identifiers")
    for key, value in fields.items():
        _validate_property(key, value)
    if class_name == "wlanEHTRU":
        size = fields.get("RUSize", fields.get("Size"))
        index = fields.get("RUIndex", fields.get("Index"))
        if size is not None and size not in _RU_SIZES:
            raise ValueError("wlanEHTRU size is not a standard RU size")
        if index is not None and (not isinstance(index, int) or index < 1):
            raise ValueError("wlanEHTRU index must be positive")
    if class_name == "wlanURAConfig":
        dims = fields.get("Size", [2, 2])
        if not isinstance(dims, (list, tuple)) or len(dims) != 2 or any(
            not isinstance(x, int) or x < 1 for x in dims
        ):
            raise ValueError("wlanURAConfig Size must be two positive integers")
        fields.setdefault("Size", list(dims))
        fields.setdefault("ElementSpacing", 0.2)
    derived = {}
    if "ChannelBandwidth" in fields:
        bw = _BANDWIDTHS[fields["ChannelBandwidth"]]
        derived["bandwidth_hz"] = bw * 1e6
        if bw in (5, 10, 20, 40, 80, 160, 320):
            derived["base_sample_rate_hz"] = bw * 1e6
            derived["legacy_fft_length"] = 64 * max(1, bw // 20)
    if "MCS" in fields:
        mcs = fields["MCS"]
        if class_name == "wlanNonHTConfig":
            table = (1, 1, 2, 2, 4, 4, 6, 6)
            if mcs > 7:
                raise ValueError("Non-HT MCS must be 0..7")
            derived["modulation_bits_per_symbol"] = table[mcs]
        else:
            derived["modulation_bits_per_symbol"] = (
                1 if mcs == 0 else 2 if mcs in (1, 2) else 4 if mcs in (3, 4)
                else 6 if mcs in (5, 6, 7) else 8 if mcs in (8, 9)
                else 10 if mcs in (10, 11) else 12
            )
    return {"class": class_name, "properties": fields, "derived": derived}


DISPATCH = {name: partial(config, name) for name in CONFIGS}
DISPATCH.update({name: partial(enum_type, name) for name in ENUMS})


if __name__ == "__main__":
    run_cli("Public WLAN configuration and enum descriptors", DISPATCH)
