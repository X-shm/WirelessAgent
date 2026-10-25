"""WLAN MAC data frame, A-MPDU, field-index and format-detect slices."""
from __future__ import annotations

import zlib

import numpy as np

from _nr_remaining_common import run_cli
from wlan_numeric_family import _complex_samples
from wlan_signal_fields import _stf


_STATUS_NAMES = (
    "Success", "FCSFailed", "InvalidProtocolVersion", "UnsupportedFrameType",
    "UnsupportedFrameSubtype", "NotEnoughData", "UnsupportedBAVariant",
    "UnknownBitmapSize", "UnknownAddressExtMode", "MalformedAMSDULength",
    "MalformedSSID", "MalformedSupportedRatesIE", "MalformedIELength",
    "MissingMandatoryIEs", "NoMPDUFound", "CorruptedAMPDU",
    "InvalidDelimiterLength", "MaxAMSDULengthExceeded", "MaxMPDULengthExceeded",
    "MaxMMPDULengthExceeded", "MaxMSDULengthExceeded", "UnexpectedProtectedFrame",
    "UnsupportedTriggerType", "UnknownHELTFTypeAndGI", "UnknownAPTxPower",
    "UnknownAID12Value", "UnknownRUAllocation", "UnknownULMCS",
    "UnknownTargetRSSI", "UnsupportedBARType", "MissingUserInfo",
    "InvalidLSIGLength",
)
STATUS = {name: -i for i, name in enumerate(_STATUS_NAMES)}


def _octets(value, name):
    if isinstance(value, str):
        try:
            return bytes.fromhex(value.replace(":", "").replace("-", ""))
        except ValueError as exc:
            raise ValueError(f"{name} must be hexadecimal octets") from exc
    if not isinstance(value, list) or any(not isinstance(x, int) or not 0 <= x <= 255 for x in value):
        raise ValueError(f"{name} must be octets or hexadecimal text")
    return bytes(value)


def _address(value, name):
    result = _octets(value, name)
    if len(result) != 6:
        raise ValueError(f"{name} requires six bytes")
    return result


def mac_decode_status(name=None, code=None):
    if name is not None and name not in STATUS:
        raise ValueError("unknown MAC decode status")
    if code is not None and code not in STATUS.values():
        raise ValueError("unknown MAC decode code")
    found = name if name is not None else next((k for k, v in STATUS.items() if v == code), None)
    return {"members": STATUS, "name": found,
            "code": STATUS[found] if found is not None else None}


def mac_frame(payload, destination="ffffffffffff", source="000000000000",
              bssid="000000000000", sequence_number=0, subtype=0):
    data = _octets(payload, "payload")
    if not isinstance(sequence_number, int) or not 0 <= sequence_number <= 4095:
        raise ValueError("sequence_number must be 0..4095")
    if not isinstance(subtype, int) or not 0 <= subtype <= 15:
        raise ValueError("subtype must be 0..15")
    frame_control = bytes([(subtype << 4) | 0x08, 0])
    header = (frame_control + b"\x00\x00" + _address(destination, "destination") +
              _address(source, "source") + _address(bssid, "bssid") +
              (sequence_number << 4).to_bytes(2, "little"))
    body = header + data
    fcs = zlib.crc32(body).to_bytes(4, "little")
    return {"mpdu_hex": (body+fcs).hex().upper(), "frame_length_bytes": len(body)+4,
            "payload_length_bytes": len(data), "fcs_hex": fcs.hex().upper()}


def mpdu_decode(mpdu):
    frame = _octets(mpdu, "mpdu")
    if len(frame) < 28:
        return {"status": "NotEnoughData", "status_code": -5}
    body, fcs = frame[:-4], frame[-4:]
    passed = zlib.crc32(body).to_bytes(4, "little") == fcs
    protocol = frame[0] & 0x3
    status = "FCSFailed" if not passed else "InvalidProtocolVersion" if protocol else "Success"
    return {"status": status, "status_code": STATUS[status], "fcs_valid": passed,
            "frame_type": (frame[0] >> 2) & 3, "subtype": frame[0] >> 4,
            "destination": frame[4:10].hex().upper(),
            "source": frame[10:16].hex().upper(),
            "bssid": frame[16:22].hex().upper(),
            "sequence_number": int.from_bytes(frame[22:24], "little") >> 4,
            "payload_hex": body[24:].hex().upper(),
            "payload_length_bytes": len(body) - 24}


def _crc8(data):
    crc = 0xff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ (0x07 if crc & 0x80 else 0)) & 0xff
    return crc ^ 0xff


def ampdu_deaggregate(ampdu, phy_format="VHT", check_crc=True):
    data = _octets(ampdu, "ampdu")
    if phy_format not in ("HT-Mixed", "VHT", "HE-SU", "EHT-SU"):
        raise ValueError("unsupported A-MPDU PHY format")
    frames, crc_failures = [], []
    pos = 0
    while pos + 4 <= len(data):
        if data[pos+3] != 0x4e:
            pos += 4
            continue
        prefix = data[pos:pos+4]
        failed = _crc8(prefix[:2]) != prefix[2]
        length = (prefix[0] >> 4) | (prefix[1] << 4)
        if phy_format != "HT-Mixed":
            length |= (prefix[0] & 0x0c) << 10
        pos += 4
        if not length:
            if prefix[0] & 1:
                break
            continue
        if pos + length > len(data):
            break
        if failed and check_crc:
            crc_failures.append(True)
        else:
            frames.append(data[pos:pos+length].hex().upper())
            crc_failures.append(failed)
        pos += ((length + 3) // 4) * 4
    status = "Success" if frames else "NoMPDUFound"
    return {"mpdu_list": frames, "delimiter_crc_fails": crc_failures,
            "status": status, "status_code": STATUS[status]}


def field_indices(format="Non-HT", num_data_symbols=1, field_name=None):
    if format not in ("Non-HT", "HT", "VHT") or not isinstance(num_data_symbols, int) or num_data_symbols < 0:
        raise ValueError("format must be Non-HT/HT/VHT and num_data_symbols nonnegative")
    fields = [("L-STF",160),("L-LTF",160),("L-SIG",80)]
    if format == "HT":
        fields += [("HT-SIG",160),("HT-STF",80),("HT-LTF",80)]
    if format == "VHT":
        fields += [("VHT-SIG-A",160),("VHT-STF",80),("VHT-LTF",80),("VHT-SIG-B",80)]
    fields.append(("NonHT-Data" if format == "Non-HT" else f"{format}-Data",80*num_data_symbols))
    indices, cursor = {}, 1
    for name, count in fields:
        indices[name] = [cursor, cursor+count-1]
        cursor += count
    if field_name is not None:
        if field_name not in indices:
            raise ValueError("unknown field_name for format")
        return {"indices": indices[field_name], "field_name": field_name, "sample_count": cursor-1}
    return {"indices": indices, "sample_count": cursor-1, "format": format}


def format_detect(waveform, threshold=0.5):
    x = _complex_samples(waveform).reshape(-1)
    template = _stf()
    if x.size < len(template) or not 0 < threshold <= 1:
        raise ValueError("at least one L-STF and threshold in (0,1] required")
    corr = abs(np.vdot(template, x[:len(template)]))
    metric = float(corr / (np.linalg.norm(template) * np.linalg.norm(x[:len(template)]) + 1e-15))
    return {"format": "Non-HT" if metric >= threshold else "Unknown",
            "legacy_preamble_correlation": metric}


DISPATCH = {
    "wlanAMPDUDeaggregate": ampdu_deaggregate,
    "wlanFieldIndices": field_indices,
    "wlanFormatDetect": format_detect,
    "wlanMACDecodeStatus": mac_decode_status,
    "wlanMACFrame": mac_frame,
    "wlanMPDUDecode": mpdu_decode,
}


if __name__ == "__main__":
    run_cli("WLAN MAC frame and field-index slices", DISPATCH)
