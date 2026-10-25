"""Standalone NR BCH payload interleaving, scrambling, CRC and polar coding."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import bits, run_cli
from nr_control_codec import _recover
from nr_crc import _crc_encode_bits
from nr_polar import polar_encode, polar_rate_match
from nr_polar_decode import polar_decode_sc
from nr_prbs import prbs


_G = [16, 23, 18, 17, 8, 30, 10, 6, 24, 7, 0, 5, 3, 2, 1, 4,
      9, 11, 12, 13, 14, 15, 19, 20, 21, 22, 25, 26, 27, 28, 29, 31]


def _positions(lssb: int):
    if lssb not in (4, 8, 64):
        raise ValueError("lssb must be 4, 8 or 64")
    positions = []
    unscrambled = set()
    sf, ssb, other = 0, 11, 14
    for i in range(32):
        if 1 <= i <= 6 or 24 <= i <= 27:
            p = _G[sf]
            if i in (25, 26):
                unscrambled.add(p)
            sf += 1
        elif i == 28:
            p = _G[10]
            unscrambled.add(p)
        elif i in (29, 30, 31):
            p = _G[ssb]
            if lssb == 64:
                unscrambled.add(p)
            ssb += 1
        else:
            p = _G[other]
            other += 1
        positions.append(p)
    return positions, unscrambled


def _scramble(interleaved: np.ndarray, lssb: int, ncellid: int, v: int):
    positions, skip = _positions(lssb)
    if not 0 <= ncellid <= 1007 or not 0 <= v < 4:
        raise ValueError("ncellid must be 0..1007 and v 0..3")
    mask = np.zeros(32, dtype=np.uint8)
    usable = [i for i in range(32) if i not in skip]
    m = len(usable)
    mask[usable] = prbs(ncellid, [v * m, m])
    return interleaved ^ mask, positions


def bch(payload, sfn: int, hrf: int, lssb: int, idxoffset: int, ncellid: int):
    data = bits(payload, "payload")
    if len(data) != 24 or not 0 <= sfn <= 1023 or hrf not in (0, 1):
        raise ValueError("payload must have 24 bits, sfn 0..1023, hrf 0/1")
    if lssb not in (4, 8, 64) or not 0 <= idxoffset < (64 if lssb == 64 else 32):
        raise ValueError("invalid lssb or idxoffset")
    extra = [(sfn >> j) & 1 for j in (3, 2, 1, 0)] + [hrf]
    extra += ([(idxoffset >> j) & 1 for j in (5, 4, 3)] if lssb == 64
              else [(idxoffset >> 4) & 1, 0, 0])
    a_bar = np.r_[data, np.asarray(extra, dtype=np.uint8)]
    positions, _ = _positions(lssb)
    a = np.zeros(32, dtype=np.uint8)
    a[positions] = a_bar
    v = 2 * int(a_bar[25]) + int(a_bar[26])
    scrambled, _ = _scramble(a, lssb, ncellid, v)
    with_crc = _crc_encode_bits(scrambled, "24C")
    mother = polar_encode(with_crc, 864, 9, True)
    return {"codeword": polar_rate_match(mother, 56, 864),
            "scrambled_payload": scrambled}


def bch_decode(llr, lssb: int | None = None, ncellid: int | None = None,
               list_length: int = 1):
    soft = np.asarray(llr, dtype=float).reshape(-1)
    if len(soft) != 864 or list_length != 1:
        raise ValueError("this subset requires 864 LLRs and list_length=1")
    decoded = polar_decode_sc(_recover(soft, 56, 9), 56, 864, 9, True)
    scrambled = decoded[:32]
    crc_ok = bool(np.array_equal(decoded[32:], _crc_encode_bits(scrambled, "24C")[-24:]))
    result = {"scrambled_payload": scrambled, "crc_ok": crc_ok, "list_length": 1}
    if lssb is not None and ncellid is not None and crc_ok:
        v = 2 * int(scrambled[_G[7]]) + int(scrambled[_G[8]])
        a, positions = _scramble(scrambled, lssb, ncellid, v)
        payload = a[positions]
        result.update({"payload": payload[:24], "sfn_lsb": payload[24:28],
                       "hrf": int(payload[28]),
                       "idxoffset_msb": payload[29:32] if lssb == 64 else payload[29:30]})
    return result


if __name__ == "__main__":
    run_cli("Standalone NR BCH broadcast transport coding", {
        "nrBCH": bch,
        "nrBCHDecode": bch_decode,
    })
