"""WLAN constellation hard/soft bit recovery with optional BCC decoding."""
from __future__ import annotations

from functools import partial

import numpy as np

from _nr_remaining_common import run_cli
from wlan_bcc import bcc_decode
from wlan_constellation import constellation_demap
from wlan_numeric_family import _complex_samples, _scheme
from wlan_scramble import scramble


BIT_RECOVER = (
    "wlanDMGDataBitRecover", "wlanDMGHeaderBitRecover",
    "wlanEHTDataBitRecover", "wlanEHTSIGCommonBitRecover", "wlanEHTSIGUserBitRecover",
    "wlanHEDataBitRecover", "wlanHESIGABitRecover", "wlanHESIGBCommonBitRecover",
    "wlanHESIGBUserBitRecover", "wlanLSIGBitRecover", "wlanNonHTDataBitRecover",
    "wlanUSIGBitRecover", "wlanVHTDataBitRecover", "wlanVHTSIGABitRecover",
    "wlanVHTSIGBBitRecover",
)
RECOVER = ("wlanHTDataRecover", "wlanHTSIGRecover", "wlanLSIGRecover",
           "wlanNonHTDataRecover", "wlanVHTDataRecover", "wlanVHTSIGARecover",
           "wlanVHTSIGBRecover")


def recover(name, symbols=None, coded_bits=None, modulation="BPSK",
            noise_variance=0.01, decision="hard", decode_bcc=False,
            code_rate="1/2", scrambler_seed=None, trim_bits=None):
    if coded_bits is None:
        if symbols is None:
            raise ValueError("symbols or coded_bits required")
        if noise_variance <= 0:
            raise ValueError("noise_variance must be positive")
        data = _complex_samples(symbols).reshape(-1)
        nbits, rotation = _scheme(modulation)
        if rotation:
            data = data * np.exp(-1j * rotation)
        raw = constellation_demap(data, noise_variance, nbits,
                                  "soft" if decision == "soft" else "hard")
        hard = (raw < 0).astype(np.uint8) if decision == "soft" else raw.astype(np.uint8)
        llr = raw.tolist() if decision == "soft" else None
    else:
        hard = np.asarray(coded_bits, dtype=np.uint8).reshape(-1)
        if not np.all((hard == 0) | (hard == 1)):
            raise ValueError("coded_bits must be binary")
        llr = None
    if hard.size == 0:
        raise ValueError("empty coded bit stream")
    if decode_bcc:
        hard = bcc_decode(hard, code_rate)
    if scrambler_seed is not None:
        hard = scramble(hard, scrambler_seed)
    if trim_bits is not None:
        if not isinstance(trim_bits, int) or trim_bits < 0:
            raise ValueError("trim_bits must be nonnegative")
        hard = hard[:trim_bits]
    output = {"source_function": name, "bits": hard.tolist(),
              "bit_count": int(hard.size), "bcc_decoded": bool(decode_bcc)}
    if llr is not None:
        output["llr"] = llr
    if name == "wlanLSIGRecover" and hard.size >= 24:
        bits = hard[:24]
        rate_code = int(sum(int(bits[i]) << i for i in range(4)))
        length = int(sum(int(bits[i+5]) << i for i in range(12)))
        parity_ok = int(bits[:18].sum() % 2) == 0
        output["lsig"] = {"rate_code": rate_code, "length_octets": length,
                          "parity_ok": parity_ok, "tail_zero": bool(np.all(bits[18:24] == 0))}
    if name.endswith("DataRecover") and hard.size % 8 == 0:
        output["bytes"] = np.packbits(hard, bitorder="little").tolist()
    return output


DISPATCH = {name: partial(recover, name) for name in BIT_RECOVER + RECOVER}


if __name__ == "__main__":
    run_cli("WLAN demap and optional BCC/data field recovery", DISPATCH)
