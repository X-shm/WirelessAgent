"""Standalone SC decoding for DCI and polar-coded UCI (K >= 12)."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import bits, run_cli
from nr_crc import _crc_encode_bits
from nr_polar import _get_n, _subblock_interleave_map, polar_encode, polar_rate_match
from nr_polar_decode import polar_decode_sc
from nr_polar_rm import triangular_deinterleave, triangular_interleave


def _recover(llr, k: int, nmax: int, ibil: bool = False) -> np.ndarray:
    soft = np.asarray(llr, dtype=float).reshape(-1)
    e = len(soft)
    if e <= k or not np.all(np.isfinite(soft)):
        raise ValueError("LLRs must be finite and E > K")
    if ibil:
        soft = triangular_deinterleave(soft)
    n = 1 << _get_n(k, e, nmax)
    y = np.zeros(n)
    if e >= n:
        np.add.at(y, np.arange(e) % n, soft)
    elif k / e <= 7 / 16:
        y[n - e:] = soft
    else:
        y[:e] = soft
        y[e:] = max(100.0, 10.0 * float(np.max(np.abs(soft))))
    mother = np.empty(n)
    mother[_subblock_interleave_map(n)] = y
    return mother


def dci_decode(llr, payload_length: int, rnti: int = 0):
    if not 12 <= payload_length <= 140 or not 0 <= rnti <= 65535:
        raise ValueError("payload_length must be 12..140 and rnti 0..65535")
    e = len(llr)
    k = payload_length + 24
    decoded = polar_decode_sc(_recover(llr, k, 9), k, e, 9, True)
    payload = decoded[:payload_length]
    expected = _crc_encode_bits(np.r_[np.ones(24, dtype=np.uint8), payload], "24C", rnti)[-24:]
    return {"payload": payload, "crc_ok": bool(np.array_equal(decoded[-24:], expected)),
            "list_length": 1}


def uci_encode(payload, e: int, modulation: str = "QPSK"):
    data = bits(payload, "payload")
    if not 12 <= len(data) <= 1012 or e <= len(data) + (6 if len(data) <= 19 else 11):
        raise ValueError("this unsegmented polar UCI subset requires 12..1012 bits and E > K")
    if len(data) >= 360 and e >= 1088:
        raise ValueError("this subset does not implement UCI code-block segmentation")
    if modulation not in ("QPSK", "16QAM", "64QAM", "256QAM"):
        raise ValueError("unsupported UCI modulation")
    poly = "6" if len(data) <= 19 else "11"
    with_crc = _crc_encode_bits(data, poly)
    mother = polar_encode(with_crc, e, 10, False)
    return {"codeword": triangular_interleave(polar_rate_match(mother, len(with_crc), e)),
            "crc": poly}


def uci_decode(llr, payload_length: int, modulation: str = "QPSK"):
    if not 12 <= payload_length <= 1012:
        raise ValueError("this unsegmented polar UCI payload_length must be 12..1012")
    if payload_length >= 360 and len(llr) >= 1088:
        raise ValueError("this subset does not implement UCI code-block segmentation")
    if modulation not in ("QPSK", "16QAM", "64QAM", "256QAM"):
        raise ValueError("unsupported UCI modulation")
    poly = "6" if payload_length <= 19 else "11"
    k = payload_length + (6 if poly == "6" else 11)
    e = len(llr)
    decoded = polar_decode_sc(_recover(llr, k, 10, ibil=True), k, e, 10, False)
    payload = decoded[:payload_length]
    expected = _crc_encode_bits(payload, poly)[payload_length:]
    return {"payload": payload, "crc_ok": bool(np.array_equal(decoded[payload_length:], expected)),
            "list_length": 1}


if __name__ == "__main__":
    run_cli("Independent DCI/UCI polar coding", {
        "nrDCIDecode": dci_decode,
        "nrUCIEncode": uci_encode,
        "nrUCIDecode": uci_decode,
    })
