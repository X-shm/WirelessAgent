"""Stateless single-code-block NR DL-SCH/UL-SCH transport subsets."""
from __future__ import annotations

import numpy as np

from _nr_remaining_common import bits, run_cli
from nr_crc import _crc_encode_bits, _crc_decode_bits
from nr_ldpc import encode as ldpc_encode, decode as ldpc_decode
from nr_ldpc_rm import _Qm
from nr_sch_info import sch_info


def _parameters(tbs: int, target_code_rate: float, e: int, modulation: str, rv: int):
    if type(tbs) is not int or tbs <= 0:
        raise ValueError("tbs must be a positive integer")
    if modulation not in _Qm or modulation == "BPSK" or rv not in range(4):
        raise ValueError("invalid modulation or redundancy version")
    qm = _Qm[modulation]
    if e <= 0 or e % qm:
        raise ValueError("E must be positive and divisible by bits per symbol")
    info = sch_info(tbs, target_code_rate)
    if info["C"] != 1:
        raise ValueError("this stateless subset supports one LDPC code block only")
    zc = info["Zc"]
    cwlen = (66 if info["BGN"] == 1 else 50) * zc
    first = max(0, tbs + info["L"] - 2 * zc)
    last = info["K"] - 2 * zc
    filler = set(range(first, last))
    start = [0, 17, 33, 56][rv] * zc if info["BGN"] == 1 else [0, 13, 25, 43][rv] * zc
    return info, cwlen, filler, start % cwlen, qm


def _selection(cwlen: int, filler: set[int], start: int, e: int):
    if len(filler) >= cwlen:
        raise ValueError("no LDPC bits remain after filler exclusion")
    selected, pos = [], start
    while len(selected) < e:
        if pos not in filler:
            selected.append(pos)
        pos = (pos + 1) % cwlen
    return np.asarray(selected, dtype=int)


def _interleave(data: np.ndarray, qm: int):
    return data.reshape(len(data) // qm, qm, order="F").T.flatten(order="F")


def _deinterleave(data: np.ndarray, qm: int):
    return data.reshape(qm, len(data) // qm, order="F").T.flatten(order="F")


def ulsch(payload, target_code_rate: float, e: int, modulation: str = "QPSK",
          rv: int = 0):
    data = bits(payload, "payload")
    info, cwlen, filler, start, qm = _parameters(len(data), target_code_rate, e,
                                                  modulation, rv)
    with_crc = _crc_encode_bits(data, info["CRC"])
    padded = np.pad(with_crc, (0, info["K"] - len(with_crc)))
    encoded = ldpc_encode(padded, info["BGN"], info["Zc"])
    if len(encoded) != cwlen:
        raise ValueError("LDPC encoder returned an unexpected codeword length")
    positions = _selection(cwlen, filler, start, e)
    codeword = _interleave(encoded[positions], qm)
    return {"codeword": codeword, "info": info, "rv": rv}


def _decode(llr, tbs: int, target_code_rate: float, modulation: str = "QPSK",
            rv: int = 0, max_iter: int = 8):
    soft = np.asarray(llr, dtype=float).reshape(-1)
    if max_iter < 1 or np.any(~np.isfinite(soft)):
        raise ValueError("max_iter must be positive and LLRs finite")
    info, cwlen, filler, start, qm = _parameters(tbs, target_code_rate, len(soft),
                                                  modulation, rv)
    positions = _selection(cwlen, filler, start, len(soft))
    recovered = np.zeros(cwlen, dtype=float)
    np.add.at(recovered, positions, _deinterleave(soft, qm))
    if filler:
        recovered[list(filler)] = 100.0
    decoded = ldpc_decode(recovered, info["BGN"], max_iter)
    block_length = tbs + info["L"]
    payload, error = _crc_decode_bits(decoded[:block_length], info["CRC"])
    return {"payload": payload[:tbs], "crc_ok": not error,
            "info": info, "iterations_limit": max_iter}


def dlsch_decoder(llr, tbs: int, target_code_rate: float,
                  modulation: str = "QPSK", rv: int = 0, max_iter: int = 8):
    return _decode(llr, tbs, target_code_rate, modulation, rv, max_iter)


def ulsch_decoder(llr, tbs: int, target_code_rate: float,
                  modulation: str = "QPSK", rv: int = 0, max_iter: int = 8):
    return _decode(llr, tbs, target_code_rate, modulation, rv, max_iter)


def ulsch_multiplex(data_bits, uci_bits, uci_positions, total_length: int):
    """Insert already-coded UCI at explicit output positions."""
    data = bits(data_bits, "data_bits")
    uci = bits(uci_bits, "uci_bits")
    positions = np.asarray(uci_positions, dtype=int).reshape(-1)
    if len(positions) != len(uci) or len(data) + len(uci) != total_length:
        raise ValueError("data and UCI sizes must fill total_length")
    if len(set(positions)) != len(positions) or np.any(positions < 0) or np.any(positions >= total_length):
        raise ValueError("uci_positions must be distinct and inside output")
    output = np.empty(total_length, dtype=np.uint8)
    output[positions] = uci
    output[np.setdiff1d(np.arange(total_length), positions)] = data
    return {"codeword": output}


def ulsch_demultiplex(codeword, uci_positions):
    values = bits(codeword, "codeword")
    positions = np.asarray(uci_positions, dtype=int).reshape(-1)
    if len(set(positions)) != len(positions) or np.any(positions < 0) or np.any(positions >= len(values)):
        raise ValueError("invalid uci_positions")
    return {"data_bits": values[np.setdiff1d(np.arange(len(values)), positions)],
            "uci_bits": values[positions]}


if __name__ == "__main__":
    run_cli("Stateless single-code-block NR shared transport coding", {
        "nrDLSCHDecoder": dlsch_decoder,
        "nrULSCH": ulsch,
        "nrULSCHDecoder": ulsch_decoder,
        "nrULSCHMultiplex": ulsch_multiplex,
        "nrULSCHDemultiplex": ulsch_demultiplex,
    })
