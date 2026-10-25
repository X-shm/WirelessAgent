"""Single-codeword LTE BCH and single-port PBCH processing."""
from __future__ import annotations

import numpy as np

from lte_crc import crc_encode
from lte_convolutional_codec import convolutional_encode
from lte_rate_match_convolutional import rate_match, rate_match_indices
from lte_tailbiting_soft import decode_tailbiting
from lte_modulation import modulate
from lte_prbs import lte_prbs

_PORT_MASK = {1: 0, 2: 65535, 4: 21845}
_MASK_PORT = {value: key for key, value in _PORT_MASK.items()}


def bch_encode(bits, cyclic_prefix="Normal", ports=1, length=None):
    raw = np.asarray(bits, dtype=int).reshape(-1)
    cp = str(cyclic_prefix).lower()
    ports = int(ports)
    if len(raw) < 1 or np.any((raw != 0) & (raw != 1)):
        raise ValueError("BCH transport block must be nonempty binary")
    if cp not in ("normal", "extended") or ports not in _PORT_MASK:
        raise ValueError("invalid BCH cyclic prefix or reference ports")
    outlen = (1920 if cp == "normal" else 1728) if length is None else int(length)
    if outlen < 1:
        raise ValueError("BCH output length must be positive")
    coded = convolutional_encode(crc_encode(raw, "16", _PORT_MASK[ports]))
    return rate_match(coded, outlen)


def bch_decode(soft_bits, transport_length=24):
    soft = np.asarray(soft_bits, dtype=float).reshape(-1)
    length = int(transport_length)
    if len(soft) < 1 or length < 1 or not np.all(np.isfinite(soft)):
        raise ValueError("BCH decoder requires finite soft bits and positive length")
    restored = np.zeros(3*(length+16), dtype=float)
    np.add.at(restored, rate_match_indices(len(restored), len(soft)), soft)
    decoded, metric = decode_tailbiting(restored)
    payload = decoded[:-16]
    recovered_mask = int("".join(map(str, decoded[-16:] ^
                                      crc_encode(payload, "16")[-16:])), 2)
    return payload, _MASK_PORT.get(recovered_mask, 0), metric


def pbch_encode(bits, ncellid=0):
    raw = np.asarray(bits, dtype=int).reshape(-1)
    if not 0 <= int(ncellid) <= 503 or len(raw) < 1 or len(raw) % 2:
        raise ValueError("PBCH requires cell ID 0..503 and even-length codeword")
    if np.any((raw != 0) & (raw != 1)):
        raise ValueError("PBCH codeword must be binary")
    return modulate(raw ^ lte_prbs(int(ncellid), len(raw)), "QPSK")


def pbch_decode(symbols, ncellid=0, transport_length=24):
    values = np.asarray(symbols, dtype=complex).reshape(-1)
    if not 0 <= int(ncellid) <= 503 or len(values) < 1:
        raise ValueError("invalid PBCH cell ID or symbols")
    soft = np.column_stack((-values.real, -values.imag)).reshape(-1)
    soft *= 1-2*lte_prbs(int(ncellid), len(soft)).astype(int)
    payload, ports, metric = bch_decode(soft, transport_length)
    return soft, values, payload, ports, metric


def slbch_encode(bits, sidelink_mode="D2D", cyclic_prefix="Normal"):
    mode, cp = str(sidelink_mode).upper(), str(cyclic_prefix).lower()
    if mode not in ("D2D", "V2X") or cp not in ("normal", "extended"):
        raise ValueError("invalid sidelink mode or cyclic prefix")
    if mode == "V2X" and cp != "normal":
        raise ValueError("V2X SL-BCH requires Normal cyclic prefix")
    columns = 7 if mode == "V2X" else 8 if cp == "normal" else 6
    length = 1008 if mode == "V2X" else 1152 if cp == "normal" else 864
    coded = bch_encode(bits, ports=1, length=length)
    return coded.reshape(-1, columns, 2).transpose(1, 0, 2).reshape(-1)


def slbch_decode(soft_bits, sidelink_mode="D2D", cyclic_prefix="Normal",
                 transport_length=40):
    mode, cp = str(sidelink_mode).upper(), str(cyclic_prefix).lower()
    if mode not in ("D2D", "V2X") or cp not in ("normal", "extended"):
        raise ValueError("invalid sidelink mode or cyclic prefix")
    columns = 7 if mode == "V2X" else 8 if cp == "normal" else 6
    soft = np.asarray(soft_bits, dtype=float).reshape(-1)
    if len(soft) % (columns*2):
        raise ValueError("SL-BCH soft length must fit complete QPSK columns")
    rows = len(soft)//(columns*2)
    restored = soft.reshape(columns, rows, 2).transpose(1, 0, 2).reshape(-1)
    payload, ports, metric = bch_decode(restored, transport_length)
    return payload, ports != 1, metric
